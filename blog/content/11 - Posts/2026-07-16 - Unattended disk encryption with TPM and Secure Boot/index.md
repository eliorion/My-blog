---
title: "Unattended Disk Encryption: LUKS, TPM, and Secure Boot on NixOS"
date: 2026-07-16T09:00:00+02:00
draft: false
aliases: ["/11---posts/2026-07-16---unattended-disk-encryption-with-tpm-and-secure-boot/"]
topics:
  - Homelab
  - Security
  - DevOps
tags:
  - nixos
  - luks
  - tpm
  - secure-boot
  - lanzaboote
  - zfs
  - disko
  - encryption
  - homelab
  - security
projects:
  - garage-fleet
categories:
  - IT
  - Homelab
weight: 2
cover:
  image: cover.svg
  alt: LUKS TPM Secure Boot on NixOS
  caption: ""
  relative: true
  hidden: true
  hiddenInList: true
  hiddenInSingle: false
---

## Two Different Thieves

node-A of my backup fleet lives in a house, not a datacenter. That single fact drives its entire disk design, because a machine in a house has two distinct theft scenarios, and they call for opposite defences.

**The powered-off thief** unplugs the box and carries it away. Against them, full-disk encryption is enough: the disks are ciphertext, the keys are not on a sticky note, done.

**The powered-on thief** takes the machine while it is running, or takes it off, boots it, and lets it decrypt itself. Against them, any encryption that unlocks automatically is worthless, because the machine will politely unlock itself for whoever has it.

But here is the constraint that makes it interesting: this node must also **boot unattended**. Power cuts happen. I will not drive somewhere to type a passphrase into a console every time the electricity blinks. An unattended boot and a defence against the powered-on thief are contradictory requirements, *unless you split the disks into two trust domains*.

---

## Two Trust Domains on One Box

The design gives node-A two encryption domains with different unlock policies:

**TPM-AUTO**: the NVMe. A LUKS2 volume (`cryptwork`) opens automatically in early boot, unsealed from a **TPM2 keyslot bound to PCR 7** (the Secure Boot policy register). Inside it lives a ZFS pool, `wpool`, holding the root filesystem, the sysadmin home, and the docker datasets. Because it unlocks in the initrd with no human present, the node comes all the way up after a power cut: root mounts, the SSH host key is available, tailscaled starts, and the box rejoins the tailnet with **no operator**. This domain defends against powered-off theft only: pull the NVMe out of *this* machine and it is ciphertext, because the key lives in this board's TPM.

**MANUAL GATE**: the HDD. The Garage data pool, `dpool`, uses ZFS-native encryption with `keylocation=prompt`. The TPM knows nothing about it. After a reboot it stays locked (ciphertext even if a *powered-on* node walks out the door mid-operation) until I unlock it over the mesh from my workstation with `fleet unlock`, which feeds the passphrase across the tailnet.

The division of labour is clean: everything the node needs to *be reachable* auto-unlocks; everything worth *stealing* waits for me.

---

## Design B: Root as a ZFS Dataset

Inside the auto domain, one decision I am particularly happy with: the root filesystem is not a partition. It is a ZFS dataset: `wpool/root`, with a 30G reservation.

The NVMe layout is minimal:

```
ESP        2G      (boot)
swap       8G      (randomEncryption — a fresh key every boot)
cryptwork  rest    (LUKS2 → zpool wpool)
  wpool/root       30G reservation — the OS
  wpool/home       the workstation
  wpool/docker     images and containers
```

No guessing "how big should root be" at install time and living with the answer forever: the reservation guarantees the OS its floor, and everything else flexes. And because root is a dataset, `zfs rollback` works *on the operating system itself*: a botched change is one snapshot away from undone, on top of NixOS generations.

All Garage data stays on the HDD. The NVMe holds nothing the moat is supposed to protect.

---

## Secure Boot with Lanzaboote

TPM auto-unlock is only as strong as what the TPM agrees to unlock *for*. Binding the keyslot to PCR 7 means: if the Secure Boot state changes (someone boots a different, unsigned OS to extract the key) the TPM refuses to unseal.

Which requires actual Secure Boot. NixOS does this with **lanzaboote** (pinned at v0.4.2): it builds signed unified kernel images (UKIs), verified by my own enrolled platform keys. The chain is: firmware verifies my signature → signed UKI → systemd initrd → TPM unseals LUKS → root pool imports. Tamper with any link and the disk stays shut.

---

## The Three Ways I Nearly Bricked It

The part of this work I want to remember most is not the architecture. It is the review. Before the first install, I ran the whole plan through an adversarial pass: *assume this config is wrong; find where it kills the machine*. It found three brick-class bugs, on paper instead of on hardware.

**1. Signing keys that do not exist yet.** Lanzaboote signs UKIs with keys created by `sbctl create-keys`: a *post-install* step. Install with lanzaboote enabled, and the build fails after the disks are already wiped: no bootloader, no old system to fall back to. The fix is an explicit flag, `fleet.secureBoot`, default **false**: install and first deploy run on plain systemd-boot, and the flag flips only after the keys exist on the box. Both bootloader backends are gated with `mkForce` so that exactly one is ever enabled, verified in the built configs for both flag states before touching hardware.

**2. The ESP mathematics.** Signed UKIs bundling kernel + initrd + ZFS + TPM tooling are big, and NixOS keeps old generations around. Ten of them can fill a 1G ESP and wedge every future deploy. Hence the 2G ESP: boring, cheap, and decided *before* the partition table was written to disk, which is the only convenient time.

**3. Two hands on the TPM token.** Both disko and my secureboot module wanted to declare the `tpm2-device` crypttab token, and a duplicate entry would have broken the initrd unlock. One owner now, disko.

None of these would have shown up in a `nix build`. All of them would have shown up at the worst possible moment: after `nixos-anywhere` had destroyed the previous system.

---

## What I Took Away

The threat model came first, and the hardware design fell out of it. "Encrypt the disks" is not a plan; *"which thief, and what should they get?"* is. Powered-off theft and powered-on theft are different attackers, and one box can answer both, with two domains and two unlock policies.

And the second lesson, the one that saved me a re-install at minimum: **review the install path as hard as the configuration**. A NixOS config that evaluates, builds, and even boots in a VM can still brick a real machine if the *ordering* is wrong: keys created after they are needed, an ESP sized for a different bootloader, two modules fighting over one crypttab line. The adversarial pass cost an evening. The bricks it caught would each have cost a drive to another city.
