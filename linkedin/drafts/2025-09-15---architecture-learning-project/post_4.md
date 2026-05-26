---
angle: behind-the-scenes
post_number: 4
blog_post: 2025-09-15 - Architecture-learning-project
generated: 2026-05-26T14:16:59.938086
---

Behind every architecture decision is a constraint you didn't plan for.
Here's what actually shaped my homelab.

Constraint 1: Budget
Can't buy 3 physical servers. Fix: 1 mini PC + Proxmox + VMs. Hardware cost stays low.

Constraint 2: Security without complexity
Need cluster access from anywhere, safely. Fix: VPN container on the public network. Nothing in the admin network is reachable without it. Full stop.

Constraint 3: Realistic Kubernetes environment
Cloud K8s hides the load balancer from you. I wanted to build one. Fix: lightweight container on a dedicated network, sitting in front of the cluster.

Constraint 4: Device-independent development
Don't want tools tied to my laptop. Fix: management VM holds all tooling — Talos, GitOps, everything. Any machine becomes my workstation.

The result: a lab that behaves like production, runs on modest hardware, and teaches me every layer of the stack.

Architecture isn't about what's ideal.
It's about what works given your actual constraints.

#Homelab #Kubernetes #DevSecOps #Infrastructure #SelfHosted
