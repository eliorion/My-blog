---
angle: technical deep-dive
post_number: 2
blog_post: 2026-07-18 - One mount option from unbootable
generated: 2026-07-27T21:32:21.523353
---

"cannot open 'dpool/garage': dataset does not exist"
I had created that dataset five minutes earlier.

The error was truthful. It was just answering a different question than the one I thought I was asking.

The setup: NixOS imports ZFS pools through generated systemd services. I'd added noauto + nofail to my encrypted datasets so their (intentionally) failing mounts wouldn't drop the box into emergency mode.

The mechanism, straight from nixpkgs' zfs.nix:

requiredBy = getPoolMounts prefix pool
  ++ lib.optional (!noauto) "zfs-import.target";

Read that second line carefully. The pool's import service joins zfs-import.target only if the pool is not "noauto". And a pool counts as noauto when ALL of its filesystems carry the noauto mount option.

Every filesystem on my pool was one of those datasets. So the import service silently dropped out of the boot graph. The service existed. The disks were healthy. Nothing ever started it.

To a system where the pool was never imported, the dataset genuinely does not exist.

An option I thought meant "don't mount this dataset" actually meant "this pool has no reason to exist at boot".

The fix: remove noauto, keep nofail. The mount still fails at boot — by design, the key isn't loaded — but the pool imports, SSH comes up, and I can unlock remotely.

Mount options on NixOS don't just configure mounts. They generate the boot graph.

#nixos #zfs #systemd #linux #debugging
