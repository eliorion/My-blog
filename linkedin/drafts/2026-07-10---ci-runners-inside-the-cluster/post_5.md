---
angle: hot take
post_number: 5
blog_post: 2026-07-10 - CI runners inside the cluster
generated: 2026-07-27T21:27:15.738151
---

"That commit is just fiddly resource tuning."
No. That commit is the actual work.

I recently moved my GitHub Actions runners inside my Kubernetes cluster. The commit most people would skim past is the one full of memory requests, CPU limits, and anti-affinity rules.

Here's the thing about running CI on 50Gi spread across three nodes that are simultaneously control planes, workers, and CI farm:

There is no slack to hide mistakes.

Every resource request is a promise taken from someone else.
Every missing limit is an eviction waiting for the worst moment.
The scheduler only balances what you've told it about.

Cloud CI hides all of this behind someone else's capacity planning. You push, it builds, and the tradeoffs someone made about memory and CPU stay invisible.

Run the runners yourself, and every one of those tradeoffs lands in a YAML file you have to justify line by line.

That's not overhead. That's the skill.
The tuning IS the engineering.

If your platform work feels like "just config" — look closer. The config is where the thinking lives.

#platformengineering #kubernetes #devops #sre #cicd
