---
angle: personal story
post_number: 1
blog_post: 2026-07-18 - One mount option from unbootable
generated: 2026-07-27T21:32:21.522742
---

I almost bricked my entire backup fleet.
The cause? Two words in a mount config.

My storage nodes are designed to boot with their data locked. ZFS-native encryption, a key prompt that nobody answers. The node boots, joins the network, and waits for me to unlock it remotely.

Problem: systemd hates mounts that fail. A failed mount at boot dropped the node into emergency mode. No SSH. No remote access. A rescue shell on a machine with no keyboard attached.

So I reached for the classic sysadmin fix: noauto + nofail.

Boot stopped failing. I thought I'd solved it.

What actually happened: on NixOS, marking ALL of a pool's filesystems as noauto silently removes the pool's import service from the boot graph. The pool never imports at all.

On my first node, I got lucky — one pool held other datasets and stayed importable, so the machine was reachable and I could debug.

The other two nodes have no such luck. Storage-only pools. Sitting offsite, in another building, with nobody nearby. With that config, they would have booted with zero data pools imported.

The exact machines that exist to be the reliable copies would have been bricked the hardest.

The fix? Delete one word:

mountOptions = [ "nofail" ];

Finding this on the first install, instead of after rolling out the fleet, is the closest I've come to being grateful for a bug.

#nixos #zfs #homelab #devops #debugging
