---
angle: behind-the-scenes
post_number: 6
blog_post: 2026-07-14 - A ransomware-resistant backup fleet
generated: 2026-07-27T21:29:46.144559
---

Four servers, three physical locations, zero manual installs.
Every machine in my backup fleet comes from one git repo.

Behind the scenes, the whole fleet is declarative NixOS:

- disko declares the disk layouts — partitions and ZFS pools as code
- nixos-anywhere installs a node from nothing, over SSH, onto a blank machine
- deploy-rs pushes day-2 changes
- sops-nix keeps secrets encrypted inside the repo, one age key per node

The repository is small and boring in the best way: a modules folder with base hardening, Garage, ZFS snapshots, and Tailscale — plus one small file per host declaring its role, zone, and capacity.

My favorite consequence: security configuration follows roles, not memory. The ZFS snapshot module activates itself on any node that declares the storage role:

config = lib.mkIf (config.fleet.role == "storage") { ... }

A new storage node can't silently forget its snapshot protection. The gateway can't accidentally pick it up. I don't have to remember — the system does.

Rebuilding a dead node isn't archaeology, it's a reinstall. And every security decision lives in code, reviewable in a diff.

Boring infrastructure is a feature. Save the excitement budget for the threat model.

#nixos #infrastructureascode #devops #homelab
