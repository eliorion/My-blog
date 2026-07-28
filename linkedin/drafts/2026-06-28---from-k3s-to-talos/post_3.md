---
angle: key lesson
post_number: 3
blog_post: 2026-06-28 - From K3s to Talos
generated: 2026-07-27T20:05:58.380550
---

A backup you've never restored isn't a backup.
It's a hope.

I learned this the good way — by accident.

In my homelab, Postgres runs on CloudNativePG, a Kubernetes operator that treats databases as managed resources. It streams base backups and WAL archives to Cloudflare R2, and takes a fresh base backup every time a cluster is created or recreated.

I set it up because it seemed like the right thing to do. I never actually tested a restore.

Then I lost a volume.

And instead of a dead database, CNPG restored the whole thing from its R2 archive. Data intact. No heroics, no 3am panic. The recovery path I had never exercised just... worked.

I got lucky that my first real restore was involuntary and successful. Most people find out their backups are broken at the worst possible moment.

So if you run anything stateful — homelab or production — don't ask 'do I have backups?'

Ask 'when did I last restore one?'

If the answer is 'never', you don't have backups. You have hope.

#postgresql #cloudnativepg #kubernetes #backups #sre
