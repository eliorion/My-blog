---
angle: key lesson
post_number: 3
blog_post: 2026-05-24 - mve-itguard
generated: 2026-05-26T14:28:03.162359
---

I run Kubernetes at home for learning.
I chose Docker Compose for this production system. That's not a contradiction.

When I designed mve-itguard — a self-hosted home security platform — I had two real options:

1. K3s (which I already run in my homelab)
2. Docker Compose

I chose Docker Compose. Deliberately.

Here's the reasoning:

This is a production system for a real home, not a learning environment.
The priority is reliability and operational simplicity — not exploring new tech.

What Kubernetes would add:
→ More complexity
→ More failure modes
→ More things to debug at 2am when a camera stops working

What it wouldn't add:
→ Horizontal scaling (not needed)
→ Multi-node compute (one server)
→ Anything that makes the system more reliable

If Frigate needs more CPU, the answer is better hardware — not more pods.

Using the right tool for the job means sometimes choosing the simpler one.
Even when you know the more sophisticated option.
Especially then.

Too many engineers (myself included, early on) reach for complexity because it feels more impressive.

It isn't. Boring and operational beats interesting and fragile every time.

Full write-up on the mve-itguard architecture — link in comments.

#devops #docker #kubernetes #homelab #softwareengineering
