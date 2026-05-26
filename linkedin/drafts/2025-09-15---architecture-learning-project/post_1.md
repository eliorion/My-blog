---
angle: personal story
post_number: 1
blog_post: 2025-09-15 - Architecture-learning-project
generated: 2026-05-26T14:16:59.936388
---

I wanted to learn Kubernetes. Really learn it.
So I built a data center at home — on a tiny mini PC.

Not just tutorials. Not managed clusters where the hard parts are hidden.

I wanted to understand what happens when a load balancer fails, when nodes can't talk to each other, when a VPN is the only way into your cluster.

So I took a machine with 16 GB RAM and 500 GB storage and turned it into a multi-server lab using Proxmox.

The setup:
→ 3 isolated virtual networks
→ A VPN container for secure remote access
→ A self-built load balancer (container, not a VM)
→ A dedicated management VM with Talos toolset
→ A Kubernetes cluster that behaves like a real prod environment

The constraint of single hardware forced real architecture decisions.

No shortcuts. No 'just use cloud.' Every problem is mine to solve.

That's the whole point.

#Kubernetes #Homelab #DevOps #LearningInPublic
