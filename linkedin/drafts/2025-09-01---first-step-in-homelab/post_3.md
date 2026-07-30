---
angle: technical deep-dive
post_number: 3
blog_post: 2025-09-01 - First-step-in-homelab
generated: 2026-05-26T14:15:18.989972
published: 2026-07-30T08:03:16.770957
post_urn: urn:li:share:7488504473967812609
---

My homelab Kubernetes stack — and why I chose each piece.
(Spoiler: total cost under 300€)

Hardware: Nipogi E3B mini PC, 16GB RAM
→ Small. Quiet. Enough to run multiple VMs without a datacenter.

Hypervisor: Proxmox
→ Free. Linux-based. Without it, a single bare-metal machine can't simulate a real multi-node cluster.

Tooling VM: Ubuntu LTS
→ All tooling lives here — not on my MacBook, not on the Proxmox host. Clean separation.

Kubernetes OS: Talos Linux
→ Immutable. API-driven. No SSH by default. Forces you to do things the right way from day one.

CLI: talosctl + k9s
→ talosctl handles cluster config. k9s makes navigating it visual.

Architecture: MacBook is terminal only. All compute lives on the server.

This simulates a real production environment — without cloud costs.

300€ + time. That's the full investment.

#Kubernetes #TalosLinux #Proxmox #Homelab #DevOps
