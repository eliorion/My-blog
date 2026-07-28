---
angle: hot take
post_number: 1
blog_post: 2026-05-31 - mve-itguard-backup
generated: 2026-07-28T16:39:59.649567
---

If your production server can delete your backups, you don't have backups.
You have a copy that ransomware will encrypt right after it encrypts everything else.

Think about the typical setup: a cron job pushes data to a NAS or cloud bucket. The credentials sit on the server. Full read-write-delete access.

An attacker who owns that server owns your backup history too. One command and years of snapshots are gone.

The fix costs nothing: append-only mode.

For my homelab, every backup node runs restic's rest-server with --append-only. The production server can write new snapshots and read old ones. It cannot delete anything. Ever.

Pruning old snapshots still happens — but on the backup node itself, via a weekly systemd timer running as a local trusted account.

The separation is clean:
— Production server writes.
— Backup nodes prune.
— Neither side holds the other's authority.

A compromised server can write garbage snapshots. Annoying, sure. But it cannot touch the history. Restore from the last clean snapshot and move on.

This isn't enterprise tooling. It's one flag on a free, open-source binary running on a Raspberry Pi at a friend's house.

Ransomware resistance is not a product you buy. It's an architecture decision you make.

#backup #ransomware #restic #homelab #security
