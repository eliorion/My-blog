---
title: "A Ransomware-Resistant Backup Fleet on NixOS"
date: 2026-07-14T09:00:00+02:00
draft: false
aliases: ["/11---posts/2026-07-14---a-ransomware-resistant-backup-fleet/"]
topics:
  - Homelab
  - Security
  - DevOps
tags:
  - nixos
  - zfs
  - garage
  - s3
  - backup
  - disaster-recovery
  - sanoid
  - tailscale
  - self-hosted
  - homelab
projects:
  - garage-fleet
categories:
  - IT
  - Homelab
weight: 2
cover:
  image: cover.svg
  alt: garage-fleet backup cluster
  caption: ""
  relative: true
  hidden: true
  hiddenInList: true
  hiddenInSingle: false
---

## The Backup Question Nobody Asks

My Talos cluster backs things up. etcd snapshots, CNPG Postgres streaming its WAL archives to object storage, Longhorn volumes with replicas. On paper, the data is safe.

But safe from what? Every one of those backups is reachable *from the cluster itself*. The credentials that write them live in the cluster. If an attacker owns the cluster — or if I fat-finger something with cluster-admin — the same power that created the backups can delete them. Ransomware operators know this: the first thing they encrypt is the data, and the second thing they delete is the backups.

The uncomfortable conclusion: a backup that your production system can destroy is not disaster recovery. It is a convenience copy.

So I built **garage-fleet**: a small, geo-distributed object store whose entire design goal is that *nothing in production can destroy it*. It is the durable DR target for the prod cluster — etcd snapshots, CNPG Postgres PITR archives, and selected Longhorn PVCs land there and stay there.

---

## What It Is

garage-fleet is a 4-node [Garage](https://garagehq.deuxfleurs.fr/) S3 object store running on **NixOS + ZFS**, deployed with **disko + nixos-anywhere + deploy-rs + sops-nix**. Garage is a lightweight, S3-compatible store built exactly for this shape of deployment: a handful of heterogeneous machines in different physical locations, forming one storage cluster.

The four nodes each have a distinct role:

- **node-A** — onsite storage, and doubles as my DevPod workstation
- **node-B** — offsite location 1, storage + proxy
- **node-C** — offsite location 2, storage
- **node-D** — gateway: capacity 0, holds no data, belongs to no zone — it only serves the S3 API

Each storage node sits in its own zone, so Garage places replicas across physical locations. A house fire, a stolen box, or a dead disk takes out one copy, not the data.

All of it talks over the tailnet. Garage's RPC and S3 listeners bind to the nodes' Tailscale IPs — there is no public endpoint anywhere in the fleet.

---

## A Separate Trust Domain, on Purpose

The most important design decision is not a technology. It is a boundary.

garage-fleet is a **separate trust domain** from the production cluster: different operating system (NixOS, not Talos), different identities, different secrets, different network posture, different control plane. The fleet is *not* joined to prod and is deliberately *not* a second Kubernetes cluster.

That separation is the whole point. The prod cluster holds S3 credentials that let it **write** backups. Those credentials do not administer the fleet, cannot reach its nodes over SSH, and cannot touch its configuration. Someone who fully compromises the prod cluster gets the ability to upload garbage — not the ability to destroy history.

It also cuts the other way: the fleet has its own sops recipients, its own age keys, its own `.sops.yaml`. A leaked secret in one domain unlocks nothing in the other.

---

## The Snapshot Moat

Trust-domain separation protects against a compromised *cluster*. But what about compromised *S3 credentials*? An attacker holding a valid key can issue S3 deletes, and Garage will obediently execute them.

This is where ZFS earns its place. Every storage node runs **sanoid**, taking scheduled read-only ZFS snapshots of the Garage datasets — plus regular scrubs to catch silent corruption. I think of it as a moat: S3 operations happen inside the castle, but snapshots live outside its walls. No Garage credential, no S3 API call, nothing short of root on the node itself can destroy a snapshot. Deleted or encrypted objects roll back with one `zfs rollback`.

One detail I ended up caring about more than expected: the moat configures *itself*. Originally each host imported the sanoid module by hand — which means a new storage node could silently forget it. Now the module is part of the common set and gates on the node's declared role:

```nix
config = lib.mkIf (config.fleet.role == "storage") { ... };
```

A storage node cannot be missing its moat, and the gateway cannot accidentally grow one. The configuration follows the role, not my memory.

---

## The Honest Tradeoff: node-A

I need to be honest about the weakest node, because I made it weak on purpose.

node-A is also my development workstation — it hosts DevPod containers. Rootless podman could not provide the full container envelope I wanted (`--privileged`, docker-in-docker, host ports below 1024), so node-A runs **root docker**, and my dev user is in the docker group.

The docker group is root-equivalent. `docker run -v /:/host` hands out uid 0, and uid 0 can run `zfs destroy dpool/garage@*`. So on node-A, the snapshot moat no longer holds against a container escape or a malicious transitive dependency arriving through some `package.json`. Tailscale-only exposure does not mitigate this — the threat is not the network perimeter, it is the code I voluntarily run.

I accepted that trade with eyes open, and wrote the consequence into the design: **node-A is only the onsite copy. The real ransomware defence is node-B and node-C**, whose moats are intact — and which may never, ever take on a workstation role.

---

## How It Is Built

The repository is small and boring in the best way:

```
modules/
  base.nix        # ssh hardening, nftables firewall, users, boot generations
  sops.nix        # sops-nix wiring, per-node age keys
  garage.nix      # services.garage + garage.toml, listeners on the tailnet
  zfs-sanoid.nix  # the snapshot moat + autoScrub (storage roles only)
  tailscale.nix   # mesh membership, tags, proxy toggle
  workstation.nix # node-A only: the DevPod host
hosts/
  node-a.nix … node-d.nix   # per-node role, zone, capacity
  disko-*.nix               # declarative disk layouts
```

Disks are declared with disko, nodes are installed from nothing with nixos-anywhere, day-2 changes go out with deploy-rs, and secrets ride in the repo encrypted with sops. The entire lifecycle is driven by one script — `scripts/fleet` — but that tool deserves its own post.

---

## What This Design Actually Buys

Layered answers to "who can delete my backups?":

- **Prod cluster compromised** → its credentials only write to S3; the fleet is a different trust domain.
- **S3 credentials leaked** → deletes hit objects, not the read-only ZFS snapshots underneath.
- **One site burns down** → two other zones hold replicas.
- **node-A's workstation betrayed by a container** → it was never the line of defence; B and C are.

None of these layers is exotic. The work was deciding what each layer defends against, and being honest about where a layer is deliberately absent. A backup system is a security system — and a security system starts with naming your attacker, not picking your tools.
