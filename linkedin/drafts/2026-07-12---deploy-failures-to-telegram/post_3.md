---
angle: hot take
post_number: 3
blog_post: 2026-07-12 - Deploy failures to Telegram
generated: 2026-07-27T21:28:10.350160
---

Dashboards are where information waits for you.
That's exactly why they fail for homelabs.

Hot take: if your monitoring strategy is "I check Grafana," you don't have a monitoring strategy. You have a habit. And habits erode.

A homelab you have to babysit is a homelab you will eventually ignore.

GitOps makes this sneakier, not better. Deploys happen automatically when a commit lands, so nothing forces you to watch them land. Automation without alerting is just failure with a delay.

My rule now: information that matters must come find me.

For me that's Telegram — already on my phone, already has a bot API, costs nothing. Flux failures land in my chat the moment they happen. Prometheus keeps re-sending while things stay broken.

The dashboards still exist. But I use them to investigate, not to discover.

Discovery should be push, not pull.

The moment I made that switch, I stopped checking on my cluster — and started trusting it.

#monitoring #observability #devops #homelab
