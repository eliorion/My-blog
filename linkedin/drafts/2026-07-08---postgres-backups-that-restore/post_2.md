---
angle: key lesson
post_number: 2
blog_post: 2026-07-08 - Postgres backups that restore
generated: 2026-07-27T21:26:10.506540
---

My Postgres cluster was shipping WAL to object storage from minute one.
It was still unrecoverable for hours.

Here's the gap that bit me:

CloudNativePG backups have two parts. Base backups (a full snapshot, taken on a schedule) and WAL archiving (every write-ahead-log segment, shipped continuously).

A restore needs both: newest base backup first, then WAL replayed on top.

My ScheduledBackup ran at 03:00. So a freshly bootstrapped cluster spent its first hours with a perfect WAL stream... and no base backup to apply it to.

WAL alone is a diff with nothing to diff against.

Then a staging node got renamed, the local-path PVs got orphaned, and I had to re-bootstrap the cluster. Recovery was impossible. From the outside, everything looked backed up. Nothing was.

The fix is one line in the ScheduledBackup spec:

immediate: true

Every time the cluster is created or recreated, it takes a base backup right away instead of waiting for the schedule. The WAL stream has an anchor from minute one.

Cheapest insurance in my whole repo. It's now the default on every database I run, staging and production.

Check your operators. "Backups configured" and "recovery point exists" are two different states.

#postgresql #cloudnativepg #kubernetes #backups #devops
