---
angle: technical deep-dive
post_number: 3
blog_post: 2026-07-08 - Postgres backups that restore
generated: 2026-07-27T21:26:10.506678
---

The most dangerous thing a recovering Postgres cluster can do:
write into the archive that's saving its life.

Two details from a real CNPG disaster recovery that most tutorials skip:

1. Restore into a new serverName.

When my database restored from its Barman archive on Cloudflare R2, it read from s3://.../asp-db/ but archived new WAL under s3://.../asp-db-r1/.

The source archive stayed read-only and untouched. If the restore had failed halfway, I could have retried from an intact source. If the recovering cluster had written into the original prefix, a failed restore could have damaged the only copy of my data.

2. Never reuse a WAL prefix across cluster generations.

Later I wanted to collapse the bucket back to a single prefix. The trap: a brand-new Postgres cluster starts on timeline 1 and generates WAL segment names that collide with the old archive's timeline-1 segments.

Mix WAL from two cluster generations under one prefix and the archive silently poisons itself. It looks healthy. It restores garbage.

The order matters: purge the stale prefix, repoint serverName, verify the new archive is healthy, then drop the orphan.

Archive hygiene is unglamorous. But a backup you can't trust is exactly as useful as no backup.

#postgresql #cloudnativepg #disasterrecovery #sre #devops
