---
angle: hot take
post_number: 4
blog_post: 2026-07-08 - Postgres backups that restore
generated: 2026-07-27T21:26:10.506782
---

Everyone has backups.
Almost nobody has restores.

Until you've actually restored one, a backup is not protection. It's a checkbox that makes you feel protected while quietly hiding whatever is wrong with it.

Maybe the base backup never ran. Maybe the WAL archive has a gap. Maybe the credentials expired months ago. You won't find out from the green checkmark. You'll find out at 2am, mid-incident, when finding out is most expensive.

I got lucky: my homelab forced the test. A storage failure wiped my database volumes, and my CNPG cluster had to restore itself from its Barman archive for real. It worked — newest base backup pulled from R2, WAL replayed on top, data back.

Here's the uncomfortable part: the only reason I know that archive was restorable is that the restore actually ran. Before that day, I had the same green checkmarks everyone else has.

A backup that has never been restored is a hope, not a plan.

You don't need a disaster to run the test. Restore into a scratch namespace this week. Either you gain real confidence, or you find the problem while it's still cheap to fix.

Both outcomes beat the checkbox.

#backups #disasterrecovery #postgresql #sre
