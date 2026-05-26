---
angle: personal story
post_number: 1
blog_post: 2026-02-26 - First GitOps implementation
generated: 2026-05-26T14:23:38.761137
---

I went from running Kubernetes on my laptop to deploying real apps exposed to the internet.
One homelab project changed how I think about infrastructure.

After finishing a basic K3s course on Rancher Desktop, I moved to the real thing:

→ A Debian VM on my Proxmox server
→ A full GitOps setup with FluxCD
→ A self-hosted app with a custom domain, accessible from the internet

The goal wasn't just to "use Kubernetes."

It was to understand what happens under the hood.

So I kept root access. No GUIs. Debian CLI only. I wanted to inspect processes, troubleshoot at the system level, and feel what a real production environment looks like.

Did I need powerful hardware? No.
50 GB of storage. 2 GB of RAM. That's it.

The project is intentionally simple — single node, single repo, simplified architecture.

Not because it's easy.
Because building strong foundations before scaling is how you actually learn.

Next step: multiply nodes, tighten security, and move toward a proper production homelab.

#GitOps #Kubernetes #Homelab #K3s #DevOps
