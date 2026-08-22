---
title: "One Mount Option Away From an Unbootable Server"
date: 2026-07-18T09:00:00+02:00
draft: false
aliases: ["/11---posts/2026-07-18---one-mount-option-from-unbootable/"]
topics:
  - Homelab
  - DevOps
tags:
  - nixos
  - zfs
  - systemd
  - nixpkgs
  - debugging
  - boot
  - homelab
projects:
  - garage-fleet
categories:
  - IT
  - Homelab
weight: 2
cover:
  image: cover.svg
  alt: noauto nofail ZFS boot bug
  caption: ""
  relative: true
  hidden: true
  hiddenInList: true
  hiddenInSingle: false
---

## A Filesystem That Must Fail to Mount

My backup fleet's storage nodes have a deliberate quirk: the Garage data pool is encrypted with ZFS-native encryption and `keylocation=prompt`, and **nobody is there to answer the prompt at boot**. That is the design — the "manual gate". The node boots, joins the tailnet, and the data stays ciphertext until I unlock it remotely.

Which means that at every single boot, the Garage datasets *cannot* mount. Their key is not loaded. The mount units fail — by design.

systemd does not share my enthusiasm for designed failure. A failed mount fails `local-fs.target`, and a failed `local-fs.target` drops the machine into emergency mode: no SSH, no tailnet, a console prompt in a place where there is no console operator. The node that was supposed to boot unattended and wait for its unlock instead sat bricked at a rescue shell.

So I reached for the classic fix. And the classic fix nearly took the whole fleet down.

---

## The Textbook Answer

Any sysadmin who has dealt with removable or unreliable mounts knows the incantation: `noauto` + `nofail`. Don't try to mount it automatically, and don't treat its absence as fatal. I set it on the Garage datasets:

```nix
mountOptions = [ "noauto" "nofail" ];
```

Boot stopped failing. Problem solved — apparently. The `nofail` half of that line was exactly right. The `noauto` half quietly broke something a full layer *below* mounting, and I only found it on node-A's first real install.

---

## What noauto Actually Does in nixpkgs

On NixOS, ZFS pools are imported by generated systemd services — `zfs-import-<pool>` — and the wiring for those services lives in nixpkgs' `zfs.nix`:

```nix
requiredBy = getPoolMounts prefix pool
             ++ lib.optional (!noauto) "zfs-import.target";
```

Read that second line carefully. The import service is pulled into `zfs-import.target` **only if the pool is not "noauto"** — and a pool counts as `noauto` when *all of its filesystems* carry the `noauto` mount option.

Every filesystem on my `dpool` is a Garage dataset. I had just marked every one of them `noauto`. So `zfs-import-dpool` silently dropped out of `zfs-import.target`, and nothing else in the boot graph asked for it. The pool was listed in `boot.zfs.extraPools`, the disks were healthy, the service existed — and no unit ever started it.

The pool did not import at all.

The first symptom made no sense until the mechanism was clear: the install's finalize step ran `zfs load-key dpool/garage` and got back

```
cannot open 'dpool/garage': dataset does not exist
```

"Does not exist"? I had *just* created it. But of course — to a system where the pool was never imported, the dataset genuinely does not exist. The error was truthful; it was just answering a different question than the one I thought I was asking.

---

## Why It Was Almost Much Worse

On node-A, the damage was contained by luck: its second pool, `wpool`, carries `/home/dev` and `/var/lib/docker`, which are *not* Garage datasets and not `noauto`. One non-noauto filesystem is enough to keep a pool in `zfs-import.target`, so `wpool` imported normally and the box was reachable and debuggable.

node-B and node-C have no such luck built in. Every pool on them is Garage-only. With this config, **no data pool would have imported at all** — on machines sitting offsite, in another building, with nobody nearby. The exact nodes that exist to be the reliable copies would have been the ones bricked the hardest.

Finding this on the onsite node's *first* install, rather than after rolling the fleet out, is the closest I have come to being grateful for a bug.

---

## The Fix: Half the Options

The correct configuration is almost embarrassing:

```nix
mountOptions = [ "nofail" ];
```

`nofail` alone gives both properties I actually wanted:

- The pool **imports** at boot — its import service stays in `zfs-import.target`.
- The mount is **attempted and fails harmlessly** — the key is not loaded, systemd logs the failure, and `nofail` keeps it out of the critical path. That journal line is not noise to suppress; *it is the manual gate working*. The failed mount **is** the pool being locked.
- Boot completes, `sshd` comes up, the node joins the mesh, and `fleet unlock` can do its job.

Verified in the built configs before redeploying: `zfs-import-dpool` and `zfs-import-wpool` on node-A, both pools on node-B, node-C's pool — all `requiredBy zfs-import.target` again, all Garage mounts `["nofail","zfsutil"]`.

The same debugging session also flushed out a race in the install script's finalize step: it SSH'd into the freshly rebooted node at full speed and hit `Connection refused`. Now `wait_for_ssh` polls until the box actually answers — and drops the stale `known_hosts` entry from the installer phase while it is at it. Two-line fix, one less flaky install.

---

## What I Took Away

`noauto` + `nofail` is a *pattern* — and I applied the pattern instead of understanding the machine. The pattern comes from a world where a mount is one line in `/etc/fstab` with no consequences beyond itself. On NixOS with ZFS, mount options feed a module that *generates the boot graph*, and an option I thought meant "don't mount this dataset" actually meant "this pool has no reason to exist at boot".

The turning point was not a clever hypothesis. It was opening nixpkgs' `zfs.nix` and reading the eight lines that wire pool imports. Once `lib.optional (!noauto)` was on the screen, the whole failure — the missing import, the "dataset does not exist", why `wpool` survived — collapsed into one obvious mechanism.

When a well-known option behaves strangely, the documentation tells you what the option *means*. Only the source tells you what it *does*. On NixOS the source is right there, and the twenty minutes it takes to read it are cheaper than one bricked offsite node.
