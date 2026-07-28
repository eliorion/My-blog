---
angle: personal story
post_number: 1
blog_post: 2026-07-04 - Caching everything through Nexus
generated: 2026-07-27T21:23:58.727660
---

Docker Hub rate-limited my entire CI overnight.
Not because of code. Because of an IP address.

Self-hosted runners have one property nobody warns you about: every job on every runner leaves through the same IP. Docker Hub doesn't see a small homelab politely building images — it sees one address hammering the registry.

Its answer: 429 Too Many Requests.

Suddenly the e2e pipeline was red, and nothing in the diff explained why. The base images just... stopped pulling.

The fix was an in-cluster Nexus mirror between CI and the internet. Base images are the highest-volume, most cacheable thing CI pulls — the same handful of tags, over and over, from every job.

Once Nexus held them:
— the 429s stopped
— builds got faster as a side effect (pulls travel the cluster network, not the internet)

The bigger lesson took longer to sink in: when you run CI on your own cluster, you own your supply chain. Every upstream registry, package index, and vulnerability database becomes your problem.

The mirror was step one. Then I kept widening what flows through it until nothing critical depended on an upstream being friendly.

If you self-host runners and haven't hit a 429 yet: it's coming.

#devops #cicd #selfhosted #homelab #docker
