---
angle: hot take
post_number: 4
blog_post: 2026-02-26 - First GitOps implementation
generated: 2026-05-26T14:23:38.763744
---

You don't need a Raspberry Pi cluster or enterprise hardware to learn Kubernetes properly.
2 GB of RAM was enough.

My entire GitOps homelab runs on:

→ 1 VM on Proxmox
→ 50 GB storage
→ 2 GB RAM
→ Debian CLI install

That's it.

Running K3s + FluxCD + Prometheus + Grafana + a self-hosted app exposed to the internet.

The trap I see a lot: people wait until they have "the right hardware" before learning.

The real bottleneck isn't compute. It's understanding the concepts.

Single node? Fine. You'll learn:
→ K3s internals
→ GitOps workflow
→ FluxCD reconciliation
→ Kustomize overlays

Just as well as on a 10-node cluster.

My plan is to scale up later — but with solid foundations, not just more hardware.

Start small. Learn deep. Scale when you actually need to.

#Homelab #Kubernetes #K3s #SelfHosted #DevOps
