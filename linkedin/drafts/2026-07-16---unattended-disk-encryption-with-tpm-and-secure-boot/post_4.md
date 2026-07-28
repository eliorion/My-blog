---
angle: tool spotlight
post_number: 4
blog_post: 2026-07-16 - Unattended disk encryption with TPM and Secure Boot
generated: 2026-07-27T21:31:01.267374
---

My root filesystem isn't a partition.
It's a ZFS dataset with a 30G reservation — and I'm not going back.

The classic install-time question: how big should root be?

Whatever you answer, you live with it forever. Too small, and you're resizing partitions from a rescue shell two years later. Too big, and you've wasted disk you'll want elsewhere.

The NVMe layout on my backup node:

ESP — 2G
Swap — 8G, random encryption, fresh key every boot
LUKS2 volume — everything else, holding one ZFS pool:
• root (30G reservation)
• home
• docker

The reservation guarantees the OS its floor. Everything else flexes around it. No guessing, no regrets baked into a partition table.

And the part I like most: because root is a dataset, zfs rollback works on the operating system itself.

A botched change is one snapshot away from undone — on top of NixOS generations, which already let you boot the previous config.

Two independent undo buttons for the OS. Both free.

Meanwhile the data worth protecting lives on a separate encrypted pool entirely. The NVMe holds nothing the moat is supposed to guard.

#zfs #nixos #linux #homelab #storage
