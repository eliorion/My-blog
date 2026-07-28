---
angle: tool spotlight
post_number: 4
blog_post: 2026-05-31 - mve-itguard-backup
generated: 2026-07-28T16:39:59.650028
---

One binary. Encrypted, deduplicated, versioned backups.
After evaluating five tools for my homelab, restic won — and it wasn't close.

What sold me:

Encryption before data leaves the client. Backup nodes only ever see ciphertext. I can put a node at a friend's house with zero trust concerns.

Deduplication that actually matters. Data is split into content-addressed chunks, each stored once. My Home Assistant database appends rows every minute — yet daily incremental transfers are megabytes, not gigabytes.

Integrity you can verify. Every chunk is identified by its hash. restic check catches silent corruption before a restore attempt reveals it. You don't appreciate this property until the day you desperately need it.

Backend-agnostic. SFTP, S3, local disk, or its own HTTP server. Same backup logic everywhere.

The ones that didn't make it:
— Borg: great dedup, but remote access rides on SSH, which makes append-only protection awkward
— Duplicati: .NET runtime, corruption history on long retention
— rclone sync: not a backup tool — no versioning, no snapshots
— Kopia: promising, less battle-tested

Bonus: rest-server, maintained by the same team, adds --append-only mode. Your production server physically cannot delete backup history.

Free. Open source. Single binary. Sometimes the boring choice is the right one.

#restic #backup #opensource #selfhosted #homelab
