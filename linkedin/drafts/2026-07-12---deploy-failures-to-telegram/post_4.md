---
angle: behind-the-scenes
post_number: 4
blog_post: 2026-07-12 - Deploy failures to Telegram
generated: 2026-07-27T21:28:10.350647
---

Every failure in my cluster now falls into exactly two buckets.
Neither of them is "silently broken."

My HelmReleases are armed to roll back automatically when an upgrade fails. On top of that sits Telegram alerting — Flux events plus Prometheus conditions.

Combine the two, and failures sort themselves:

Bucket 1: Self-healing.
The rollback restores the last good release. The Telegram message is informational — something landed badly, production already recovered, fix it when convenient.

Bucket 2: Self-announcing.
The failure persists, so the metrics path keeps buzzing until I deal with it.

The third bucket — broken, and nobody knows — no longer exists.

A detail I'm quietly proud of: the bot token is the only credential in the whole chain. It lives SOPS-encrypted in Git like every other secret, in two namespaces, and Alertmanager reads its copy from a file mount — so the rendered config never carries a plaintext token.

The whole thing was one of the smallest changes in my repository: a Provider, an Alert, a PodMonitor, a PrometheusRule.

It changed my relationship with the cluster more than most big ones.

#gitops #kubernetes #selfhosted #sre #devops
