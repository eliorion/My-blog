---
angle: technical deep-dive
post_number: 2
blog_post: 2026-07-10 - CI runners inside the cluster
generated: 2026-07-27T21:27:15.736806
---

Every missing resource limit is an eviction waiting for the worst possible moment.
I learned this running CI inside a 50Gi Kubernetes cluster.

Three nodes. All of them simultaneously control planes, workers, and CI farm.

The heavy job: a k3d end-to-end test — an entire disposable Kubernetes cluster running inside Docker-in-Docker. On the default runner pool it was starving, and worse, it could be evicted by whatever else CI was doing.

The fix was a dedicated XL runner pool. Nearly every line of its config exists because on a small cluster, something can always starve something else:

• minRunners 1 — one XL runner always warm, so e2e never waits for scale-up
• dind sidecar: 4Gi request, 10Gi limit — guaranteed memory, capped headroom
• Hard podAntiAffinity — two e2e clusters never share a node's memory
• Default pool trimmed 5/15 to 2/8 — the XL RAM had to come from somewhere
• Default dind bounded to 6Gi — previously BestEffort, so a runaway build could OOM-evict an e2e run mid-test

And the one that matters most: CPU limits on the XL dind.

With no system-reserved carve-out on kubelet, an uncapped build can steal enough CPU to make etcd miss heartbeats. That limit isn't fairness between jobs. It's armor for the control plane.

Cloud CI hides all of this behind someone else's capacity planning. Run it yourself and every tradeoff lands in a YAML file you justify line by line.

#kubernetes #cicd #sre #platformengineering #homelab
