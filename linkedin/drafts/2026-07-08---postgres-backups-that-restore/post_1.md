---
angle: personal story
post_number: 1
blog_post: 2026-07-08 - Postgres backups that restore
generated: 2026-07-27T21:26:10.506290
---

Two databases. Same cluster. Same disk failure.
One came back with its data. One came back empty.

During an HA expansion of my homelab Kubernetes cluster, a disk-UUID mismatch ended with Longhorn volumes being reformatted. Both Postgres databases were gone. Not corrupted. Empty.

Database #1 (asp-db) had CloudNativePG configured with Barman: nightly base backups plus continuous WAL archiving to Cloudflare R2.

It bootstrapped straight into recovery mode. Pulled the newest base backup, replayed WAL on top, and came back with its data. Point-in-time recovery, exactly as advertised.

Database #2 (fbref-db) was my football statistics store. No Barman config, no base backups, no WAL archive. It "didn't matter yet".

There was nothing to restore. Delete the cluster, recreate it fresh, re-scrape everything from scratch.

Same storm, same day, same failure mode. The entire difference between recovery and total loss was configuration that felt optional when I wrote it.

The lesson that stuck: data starts mattering before you decide it does.

If you have a database somewhere with "I'll add backups later" energy — later is now.

#postgresql #kubernetes #homelab #disasterrecovery #devops
