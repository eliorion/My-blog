---
title: "One Script to Run a Fleet"
date: 2026-07-22T09:00:00+02:00
draft: false
topics:
  - Homelab
  - DevOps
tags:
  - nixos
  - bash
  - tooling
  - nixos-anywhere
  - deploy-rs
  - sops
  - tailscale
  - automation
  - homelab
projects:
  - garage-fleet
categories:
  - IT
  - Homelab
weight: 2
cover:
  image: cover.svg
  alt: the fleet lifecycle script
  caption: ""
  relative: true
  hidden: true
  hiddenInList: true
  hiddenInSingle: false
---

## Death by a Dozen Runbooks

Provisioning a node in my backup fleet used to involve two scripts (`bootstrap-node`, `deploy-node`), a README section, and a mental checklist of things that must happen in exactly the right order: generate the age key, add its recipient, re-encrypt the secrets, commit them, run nixos-anywhere, seed the key, unlock the pools, join the Garage layout…

Each of those steps is easy. The *sequence* is the hazard. Forget to re-encrypt before installing, and the freshly wiped node cannot decrypt its own secrets. Forget the recipient, same outcome. Run the deploy before committing, and the flake silently builds without your changes. The failure modes were not exotic bugs — they were ordinary human ordering mistakes with disk-wiping consequences.

So the two scripts and the checklist collapsed into one tool: `scripts/fleet`. Every node lifecycle operation goes through it — and, more importantly, every *guardrail* now lives in one place.

---

## The Lifecycle in Subcommands

```
fleet new <node>        scaffold hosts/<node>.nix + disko, mint the age key,
                        wire recipients, re-encrypt secrets
fleet install <node>    provision from nothing (nixos-anywhere), seed secrets
fleet finalize <node>   retry the post-install unlock over ssh
fleet deploy <node>     apply config (deploy-rs, magic-rollback; --detached)
fleet rollback <node>   previous generation
fleet unlock <node>     feed the ZFS passphrase to a locked storage node
fleet status            aligned table: reachability, garage.service, tailnet IPs
fleet secrets           edit / verify / commit the sops files
fleet buckets           S3 buckets + keys: keygen / apply / status / browse
fleet layout            Garage cluster layout: show / apply from .nix
fleet config / guide    tailnet setup, on-box fallback runbook
```

Run `fleet` with no arguments and it drops into a small TUI menu with the current fleet status printed above it — the same commands, numbered, for the days when I do not remember the exact verb.

None of this is clever engineering. It is a bash script with a case statement. The value is not in the code; it is in *where the dangerous logic now lives*.

---

## Guardrails on the Destructive Path

`fleet install` wipes disks. It is the one command that must never run half-prepared, so it refuses to start until the world is provably consistent.

My favourite guard is the chicken-and-egg check. The dedicated age key that `install` seeds onto the new node (`/var/lib/sops-nix/key.txt`) is that node's *only* sops identity. If the secrets in the repo are not actually encrypted to that key's recipient, here is the failure chain on a freshly wiped machine: sops-nix fails at first boot → no tailscale authkey is decrypted → the node never joins the mesh → and the ZFS unlock, which is *only reachable over the mesh*, becomes impossible. A wiped box, offsite, that cannot be finished remotely.

So before touching a disk, `install` reads the recipient out of the key file and greps `.sops.yaml` for it:

```bash
grep -q "$seeded_recip" "$SOPS_YAML" \
  || die "$node's age key has recipient $seeded_recip, which is NOT in
          .sops.yaml — the secrets are encrypted to a DIFFERENT key…"
```

Alongside it: the secrets file must actually *be* encrypted (not a plaintext accident), the recipient entry must exist, and the encrypted secrets must be **committed** — because a flake copies only git-tracked files, and an uncommitted secret simply does not exist as far as the install is concerned. Every one of these checks encodes a mistake I either made or could see myself making at 11pm.

---

## Deploys That Can Undo Themselves — and One That Must Not

Day-2 changes go out with `fleet deploy`, which wraps deploy-rs and its **magic-rollback**: if a change breaks reachability, the node auto-reverts in about 30 seconds. The script knows one edge case deploy-rs cannot: the *first* push to a node has no rollback baseline, so it warns explicitly — a bad firewall or tailscaled change will NOT auto-revert; keep a console nearby — and asks before proceeding.

Then there is the one deploy class where magic-rollback is not the safety net but the *hazard*: *changes to Tailscale itself.* A normal deploy rides an SSH session over the tailnet. Restart tailscaled mid-switch and that SSH drops, the activation dies half-done, rollback kicks in — and rolling *back* a version bump downgrades tailscaled onto a state file the older version cannot parse. The node ends up off the mesh with Garage unable to bind its RPC listener. The rollback is what does the bricking.

`fleet deploy --detached` exists for exactly this. It builds the closure locally, `nix copy`-es it to the node over the tailnet, then launches `switch-to-configuration switch` as a **transient systemd unit owned by PID 1** via `systemd-run`. The command returns immediately; when the switch restarts tailscaled and the SSH session drops, the switch keeps running to completion under systemd. The node only ever moves *forward*, so a version bump self-heals instead of half-reverting.

---

## Unlocking Over the Mesh

The storage nodes keep their Garage data pools locked at boot by design, and `fleet unlock` is how they open: it prompts for the ZFS passphrase on my workstation and feeds it to the node across the tailnet.

The detail I care about: the passphrase travels **only on ssh stdin** — never in argv, never in an environment variable — so it never appears in any process table on either machine. On the node, the remote snippet walks every encryption root, loads the key for whichever are still locked, mounts the datasets, and starts Garage. The nodes also carry `garage-status` and `garage-unlock` as on-box operator commands for the fallback case where I am at a console instead.

`fleet status` closes the loop: one aligned table over the whole fleet with reachability, a live `garage.service` column, and each node's tailscale address — the difference between "I think node-C is fine" and seeing it.

---

## Buckets and Layout, Declared

The most recent additions pull the *Garage-level* configuration into the same declarative fold as the OS. S3 buckets and their access keys are declared in the repo; `fleet buckets apply` reconciles the running cluster against the declaration, `keygen` mints credentials, `status` and `browse` inspect, and a vault check verifies the credentials are stored where they belong. `fleet layout` does the same for cluster topology — each node's zone and capacity declared in the `.nix` host files, shown and applied in one step, instead of hand-typed `garage layout` incantations on some node.

Somewhere along the way, the design docs got renumbered from 09–14 (their positions in the *prod cluster's* documentation) to 00–05, with a fresh 06 for the buckets guide. A small rename, but an honest signal: the backup fleet stopped being an appendix of another project and became its own system, with its own doc zero.

---

## What I Took Away

An ops tool earns its keep the day the *dangerous* paths are the *scripted* paths. Nothing stops me from running `nixos-anywhere` or `sops updatekeys` by hand — but the moment the scripted route is also the easiest route, the guardrails actually run: the pre-wipe recipient check, the first-deploy warning, the stdin-only passphrase, the detached switch.

One entrypoint means one place to encode every lesson. Each near-miss in this project — the key that was not in `.sops.yaml`, the deploy that bricked over its own rollback — turned into a `die` or a `warn` in one bash file. The script is not automation for speed. It is a memory: the fleet's accumulated scar tissue, executable.
