---
title: "Multi-Node Backup with Restic"
date: 2026-05-31T09:00:00+02:00
draft: false
aliases: ["/11---posts/2026-05-31---mve-itguard-backup/"]
topics:
  - Homelab
  - DevOps
  - Infrastructure
tags:
  - restic
  - backup
  - homeassistant
  - cloudflare
  - debian
  - ansible
  - homelab
  - security
projects:
  - mve-itguard
categories:
  - IT
  - Homelab
weight: 2
cover:
  image: cover.svg
  alt: Multi-node Restic backup
  caption: ""
  relative: true
  hidden: true
  hiddenInList: true
  hiddenInSingle: false
---

## Why Backup Is Usually an Afterthought

Home servers tend to accumulate state. Home Assistant builds up months of sensor history and device automations. Zigbee2MQTT stores the pairing database for every device. If the disk fails and there is no backup, all of that is gone.

The typical homelab backup story goes like this: copy the data to an external drive occasionally, forget to do it, the drive fails too, or it was stored in the same location as the server. The backup exists on paper but provides no real protection.

For mve-itguard, backup was designed as a first-class concern from the start, with three explicit requirements:

1. **Automated and scheduled**. It runs at 03:00 every day without any human involvement
2. **Geographically redundant**, data exists on at least two machines in different physical locations
3. **Ransomware-resistant**: a compromised production server cannot delete backup history

Those three requirements shaped every tool and architecture decision in this section.

---

## Why Restic

[Restic](https://restic.net/) is a single binary that handles encrypted, deduplicated, versioned backups. It is the standard choice for self-hosted backup workloads, and it earned that position.

The properties that matter most here:

**Encrypted at rest.** Every block written to a restic repository is encrypted with the repository password before it leaves the client. Backup nodes see only ciphertext. They cannot read the data they store. This means backup nodes can be on machines owned by friends or family without any trust concern.

**Deduplication.** Restic splits data into variable-size chunks and stores each chunk once, content-addressed. After the first full backup, daily incremental backups transfer only what changed. For a Home Assistant database that appends new rows every minute, the daily delta is in the megabytes, not gigabytes.

**Content-addressed integrity.** Every chunk is identified by its hash. Running `restic check` verifies that every stored block matches its hash, silent corruption is detected before a restore attempt reveals it. This is not a property you appreciate until you need to restore and discover your backup was silently corrupt.

**Backend-agnostic.** Restic supports SFTP, S3, local filesystem, and its own HTTP backend. The backup logic is identical regardless of where data goes.

Alternatives were considered:

- **Borg**: excellent deduplication and encryption, but native remote support relies on SSH, which makes append-only protection harder to implement cleanly
- **Duplicati**: .NET runtime, a history of corruption bugs on long retention periods
- **rclone sync**: not a backup tool: no versioning, no snapshot semantics, no deduplication
- **Kopia**: promising and modern, but less battle-tested than restic for production use

---

## Why rest-server and Append-Only Mode

Restic needs somewhere to store its repository. The natural choice for a remote node is restic's own HTTP backend: [rest-server](https://github.com/restic/rest-server), maintained by the restic team.

The critical feature is **append-only mode**. When rest-server runs with `--append-only`, the restic client can write new snapshots and read existing ones, but **cannot delete anything**. Pruning and forget operations are blocked at the server.

```
prod server ──HTTPS──▶ rest-server (--append-only) ──▶ restic repo
                        write: allowed
                        delete: blocked
```

This is the ransomware protection model. If the production server is compromised (by malware, by an attacker who gained access, or by anything else) and the attacker discovers the backup configuration, they can write garbage snapshots but they cannot erase the historical backups. The backup history is protected by the node's filesystem permissions, not by the client's goodwill.

Pruning does still need to happen to manage storage. But it runs on the backup node directly, with a weekly systemd timer and a local trusted account. The production server never holds delete authority.

```
restic-prune.timer (weekly, Sunday 02:00) — runs on backup node as root
  restic forget --keep-daily 7 --keep-weekly 4 --keep-monthly 6 --prune
```

The separation is clean: the production server **writes**, backup nodes **prune**. Neither side needs the other's authority for its own role.

---

## Why Multiple Nodes

A single backup node is a single point of failure in a different location. Disk failure, power surge, theft, fire at that location, any of these wipes the backup history.

The 3-2-1 rule is the standard: three copies of data, on two different media types, with one copy off-site. For a homelab, this translates to: the production server (one copy), a local or nearby node (second copy), and a geographically distant node: a friend's home, a family member's place, or a remote office (third copy).

The architecture here uses two to three nodes at different physical sites:

```
Production Server (03:00 daily)
         │
    ┌────┼────┐
    ▼    ▼    ▼
 Node1 Node2 Node3
(home)(friend)(optional)
```

The production server is the single writer. It pushes to each node sequentially. Nodes do not talk to each other: no replication, no mesh, no consensus protocol. If Node 2 is offline when the backup runs, Node 1 and Node 3 still get updated. The failed node is flagged in the log and a notification fires in Home Assistant.

---

## Data Tiers

Not all data has the same value or the same size. The backup splits into two tiers:

| Tier | Data | Nodes | Retention |
|------|------|-------|-----------|
| **Critical** | HA database, Zigbee2MQTT pairings, Mosquitto state | All nodes | 7 daily / 4 weekly / 6 monthly |
| **Frigate** | Camera recordings | Node 1 only | 7 daily / 2 weekly |

**Critical data** is small (roughly 5 GB total) and irreplaceable. Losing the Home Assistant history means months of sensor graphs gone. Losing the Zigbee2MQTT pairing database means re-pairing every device manually. These go to all nodes for maximum redundancy.

**Frigate recordings** can reach hundreds of gigabytes and grow continuously. They are replaceable, cameras will record again immediately after a restore. Requiring every secondary node to have 500 GB+ of storage to hold video files would make the backup network impractical. Recordings go to the primary node only.

The git-tracked configuration files (`app/config/`) are deliberately excluded from backup. They live in the repository, versioned and encrypted, Git is already their redundant backup.

---

## Connectivity: Cloudflare Tunnel on Each Node

Each backup node runs its own Cloudflare Tunnel, pointing to its local rest-server:

```
Prod server ──HTTPS──▶ Cloudflare ──▶ cloudflared (node) ──▶ rest-server (localhost:8000)
```

This project already uses Cloudflare Tunnel to expose Home Assistant remotely. Using the same mechanism for backup nodes was a natural fit.

The key advantage is that it works behind CGNAT. Most residential internet connections today share a public IP address. There is no way to accept inbound connections without a relay. Cloudflare Tunnel establishes an outbound connection from the node to Cloudflare's network, which handles routing. No port forwarding, no static IP, no DDNS.

Each node gets its own tunnel token, configured independently in the Cloudflare dashboard. Nodes do not share tunnel infrastructure with the production server. If one node's tunnel fails, it affects only that node's backups.

---

## The Backup Flow

The backup runs daily at 03:00, triggered by a systemd timer installed by Ansible during server provisioning:

```ini
[Timer]
OnCalendar=*-*-* 03:00:00
RandomizedDelaySec=1800
Persistent=true
```

`RandomizedDelaySec=1800` jitters the start time by up to 30 minutes. This prevents all nodes from being hit simultaneously and spreads network load. `Persistent=true` means if the server was off at 03:00, the backup runs on next boot.

The script (`ops/backup`) runs as root and follows this sequence:

**Step 1, Decrypt node configuration**

```bash
_node_env=$(sops -d --input-type dotenv --output-type dotenv ops/backup.env.enc)
eval "$_node_env"
```

All node URLs, passwords, and HA notification settings are stored in `ops/backup.env.enc`, encrypted with the same AGE key as the rest of the project. The AGE key is at `/etc/sops/age/keys.txt`, installed by bootstrap. Nothing from backup configuration is in plaintext on disk.

**Step 2, Pause critical containers**

```bash
docker pause homeassistant mqtt
```

Home Assistant uses SQLite for its database. A running SQLite process writes to a WAL (Write-Ahead Log) file and periodically checkpoints to the main database file. Reading the database mid-checkpoint can produce a backup that is internally inconsistent: the snapshot captures a mix of old and new state.

`docker pause` sends SIGSTOP to every process in the container. The container freezes in place, mid-execution if necessary, with all its files in a consistent on-disk state. The backup reads those files while nothing is modifying them. `docker unpause` sends SIGCONT and execution resumes exactly where it stopped: no restart, no reconnection, no data loss.

Total pause duration is 20 to 40 seconds while restic scans and uploads all critical paths.

**Step 3, Back up critical tier to each node**

```bash
NODE_1_URL=rest:https://backup:PASSWORD@backup-node-1.example.com
NODE_1_PASSWORD=RESTIC_ENCRYPTION_PASSWORD

RESTIC_REPOSITORY="$NODE_1_URL" RESTIC_PASSWORD="$NODE_1_PASSWORD" \
    restic backup \
    /opt/mve-itguard/app/data/homeassistant \
    /opt/mve-itguard/app/data/mosquitto \
    /opt/mve-itguard/app/data/zigbee2mqtt \
    --tag critical \
    --host mve-itguard \
    --exclude "*.log" \
    --exclude "home-assistant_v2.db-shm" \
    --exclude "home-assistant_v2.db-wal"
```

The WAL and shared memory files are excluded because they are transient SQLite working files, not needed for a consistent restore. Node configuration is stored as numbered variables (`NODE_1_URL`, `NODE_2_URL`, etc.): the script iterates until it finds an empty `NODE_N_URL`.

**Step 4, Unpause**

```bash
docker unpause homeassistant mqtt
```

Services resume. The node iteration continues for any remaining critical nodes after unpause, but the containers are only paused once, during the first (and fastest) pass.

**Step 5, Frigate tier (non-fatal)**

```bash
RESTIC_REPOSITORY="$NODE_1_URL/frigate" RESTIC_PASSWORD="$NODE_1_PASSWORD" \
    restic backup /opt/mve-itguard/app/data/frigate --tag frigate
```

Frigate is not paused. Individual recording files are written sequentially: a backup that captures a partially-written file gets a shorter but valid video clip, not corruption. A few seconds of recording lost is an acceptable trade-off to avoid pausing the camera detection system.

A Frigate backup failure exits with a warning, not an error. Recordings are replaceable; the overall backup run is not considered failed because of a missed Frigate snapshot.

---

## Two Passwords Per Node

Each node uses two distinct credentials:

| Credential | Purpose | Where stored |
|------------|---------|--------------|
| HTTP password (in the URL) | Authenticates the prod server to rest-server | `backup.env.enc` on prod; `/etc/restic-node/htpasswd` on node |
| Restic password | Encrypts the repository data | `backup.env.enc` on prod; `/etc/restic-node/env` on node (for prune) |

Splitting these matters: if a backup node is physically stolen, the attacker gets the htpasswd file (which would let them write garbage snapshots to that node) but not the restic encryption password. The actual backup data remains unreadable.

The restic password is stored on the node only in `/etc/restic-node/env`, which is `root:root 600`, accessible only to root and to the weekly prune timer that runs as root. It is never in the rest-server process environment.

---

## Node Setup: One Ansible Playbook

Each backup node is provisioned with a dedicated Ansible playbook:

```bash
# Secondary node (critical tier only)
ansible-playbook infrastructure/ansible/backup-node.yaml \
    -e "backup_password=<restic-password>" \
    -e "backup_http_password=<http-password>" \
    -e "cloudflare_token=<tunnel-token>"

# Primary node (critical + Frigate)
ansible-playbook infrastructure/ansible/backup-node.yaml \
    -e "backup_password=<restic-password>" \
    -e "backup_http_password=<http-password>" \
    -e "cloudflare_token=<tunnel-token>" \
    -e "backup_primary=true"
```

The playbook installs rest-server, cloudflared, sets up a dedicated `restic-backup` system user that runs the server process, creates the repository directories, configures the htpasswd file, installs the prune timer, and hardens SSH. It is idempotent, safe to re-run after any configuration change.

Minimum hardware for a secondary node is a Raspberry Pi Zero or an old PC with a 64 GB drive. The primary node needs significantly more storage: roughly 500 GB for six months of Frigate recordings at typical resolution.

---

## Failure Notification via Home Assistant

If any critical node backup fails, the script calls the Home Assistant API to create a persistent notification:

```bash
curl -X POST \
    -H "Authorization: Bearer $HA_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"title":"Backup Failed","message":"2 node(s) failed on 2026-05-31"}' \
    "${HA_URL}/api/services/persistent_notification/create"
```

The notification appears in the Home Assistant interface on the next login. There is no separate alerting infrastructure: the home automation system that the backup protects is also the alerting channel for backup failures.

---

## Restore

Two entry points exist for restore:

```bash
# After OS reinstall — integrated into bootstrap
sudo bash ops/bootstrap ~/keys.txt --restore

# On a running server — standalone restore
sudo bash ops/restore
sudo bash ops/restore --node 2          # specific node
sudo bash ops/restore --snapshot abc123  # specific snapshot
sudo bash ops/restore --dry-run          # preview paths only
```

The restore script decrypts node configuration, probes nodes in order for reachability, stops running app containers, runs `restic restore latest --target /`, fixes file ownership, and prints the `docker compose up` command to restart services. It does not restart services automatically: a deliberate choice to give the operator a moment to verify the restored state before bringing the system back up.

---

## What Is Deliberately Not Implemented

A few things were explicitly decided against to keep the system maintainable:

**No cross-node replication.** The production server pushes to all nodes independently. Nodes do not know about each other. No mesh, no consensus.

**No automated failover.** A failed node is logged and notified. Investigation is manual.

**No real-time backup.** Daily at 03:00 is sufficient. Home automation state does not need sub-daily RPO (Recovery Point Objective). If the server fails at 02:59, 24 hours of state is lost: an acceptable trade-off for the simplicity of a daily schedule.

**No backup dashboard.** Results go to the systemd journal and to Home Assistant notifications. No external monitoring service required.

These deliberate omissions keep the backup system simple enough to be understood, operated, and fixed at 03:00 AM if something goes wrong.

---

## Closing the Series

This post is the last in the mve-itguard series. Across seven posts, the full picture of the system has been covered:

1. What it is and why: services, hardware, motivation
2. GitOps with Docker Compose, CI/CD without Kubernetes
3. Secrets with SOPS + AGE, encrypted values committed to Git
4. Self-hosted runners: isolated, least-privilege, socket-proxied
5. Server bootstrap: one command, reproducible from scratch
6. AGE key rotation: automated in CI, two steps for the developer
7. **This post**: multi-node backup, append-only, daily, automated

The design philosophy throughout has been the same: make the right thing easy to do consistently, and make the dangerous thing difficult to do accidentally. Secrets are encrypted by default. Deployments are gated by CI. The backup system cannot be destroyed by a compromised server. The production state is always a reflection of what Git declares.

None of these properties require expensive tooling. They require deliberate architecture.
