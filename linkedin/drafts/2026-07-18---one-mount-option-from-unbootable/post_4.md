---
angle: hot take
post_number: 4
blog_post: 2026-07-18 - One mount option from unbootable
generated: 2026-07-27T21:32:21.524265
---

The textbook fix nearly took down my fleet.
The correct fix was half of it.

Hot take: knowing the classic incantations makes you more dangerous, not less — right up until you understand the system underneath.

noauto + nofail is THE answer for mounts that shouldn't block boot. Every sysadmin knows it. Stack Overflow knows it. I knew it. I typed it without thinking.

mountOptions = [ "noauto" "nofail" ];

And it worked. Boot stopped failing. Ship it.

Except the pattern comes from a world where a mount is one line in /etc/fstab with no consequences beyond itself. I wasn't in that world. On NixOS with ZFS, mount options feed a module that generates the boot graph — and noauto on every dataset of a pool means the pool's import service silently drops out of boot entirely.

The nofail half of that line was exactly right.
The noauto half broke something a full layer below mounting.

The fix:

mountOptions = [ "nofail" ];

And the failed mount at boot? Not noise to suppress. The encryption key isn't loaded, the mount can't happen, systemd logs it, boot continues. That journal line IS my security gate working.

Patterns are compressed experience — someone else's. They carry invisible assumptions about the system they grew up in. Apply one to a different machine and you're not being experienced.

You're being lucky. Until you're not.

#devops #nixos #sysadmin #engineering
