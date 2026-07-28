---
angle: behind-the-scenes
post_number: 5
blog_post: 2026-07-02 - A scraper that survives its own death
generated: 2026-07-27T21:22:52.308954
---

Confession: after building all my clever self-healing patterns, the most effective fix was raising a memory limit.

One of my scraper workers kept getting OOM-killed. Over and over.

By then, the platform could shrug it off. The queue treats every claim as an expiring lease, so the dead worker's URLs went back to the pool and another worker picked them up. No lost work. No stuck queue.

It would have been easy to call that a win and move on.

But harmless is not the same as free. A pod that dies every few minutes wastes real throughput — browser startup, session warmup, re-claimed work. The system was tolerating a problem I should have just fixed.

The honest fix: raise the memory limit to 3Gi. That's it. No new mechanism, no retry logic, no architecture diagram.

That's the division of labor I now aim for:

- Resource limits sized for reality
- A system that shrugs when reality misbehaves anyway

Self-healing infrastructure is not an excuse to ignore why things are dying. It buys you the time to fix root causes calmly instead of at 2am.

Sometimes the sophisticated answer is a bigger number in a values file.

#kubernetes #homelab #devops #sre #engineering
