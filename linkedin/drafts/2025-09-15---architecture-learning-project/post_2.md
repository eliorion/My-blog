---
angle: technical deep-dive
post_number: 2
blog_post: 2025-09-15 - Architecture-learning-project
generated: 2026-05-26T14:16:59.937315
---

3 virtual networks. 1 VPN. 1 self-built load balancer. All on a 16 GB RAM box.
Here's the architecture I designed to simulate real Kubernetes production.

Net0 — public-facing
Exposed to internet. First firewall layer. Hosts the VPN endpoint. Only customer-facing services live here.

Net1 — admin network
Reachable only through VPN. Contains the K8s cluster, management VM with Talos toolset, dashboards, logging, storage.

Net2 — application traffic
Dedicated to load balancer ↔ cluster communication. Clean separation from admin traffic.

Why containers for VPN and load balancer instead of VMs?
Both are lightweight and single-purpose. VMs would burn RAM I need for cluster nodes.

Why Proxmox?
Debian-based, well-documented, free. Less time fighting the hypervisor = more time learning Kubernetes.

The goal: simulate production on budget hardware.

16 GB isn't a lot. But it's enough to understand why distributed systems are hard.

#Kubernetes #Proxmox #Homelab #Infrastructure #TalosLinux
