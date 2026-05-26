---
angle: key lesson
post_number: 3
blog_post: 2026-02-23 - Why learn linux before containerisation
generated: 2026-05-26T14:21:55.396615
---

I spent 3 days debugging a script that wasn't broken.
The real bug lived two layers below where I was looking.

When my devcontainer setup failed after switching to Rancher Desktop, I went straight to the application layer. Reviewed the script. Checked Chezmoi initialization. Inspected logs line by line.

The script was fine.

The OOM killer was silently terminating my process because Rancher Desktop's Linux VM only had 2 GB RAM — shared between a K3s cluster, experiment containers, and my devcontainers.

Wrong layer. Wasted days.

The debugging model I'm building now:

→ Host layer (CPU, RAM, disk on the machine)
→ Virtualization layer (VM limits, hypervisor config)
→ Runtime layer (container engine, orchestrator)
→ Container layer (image, mounts, env vars)
→ Application layer (your code)

Start from infrastructure up, not code down.

Especially after switching tools, runtimes, or environments. A tool change shifts the failure domain. What was impossible in setup A might be the most likely failure in setup B.

Debugging isn't just reading logs.
It's identifying which layer the failure actually lives on.

#debugging #devops #linux #containers #platformengineering
