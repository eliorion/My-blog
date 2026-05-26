---
angle: tool spotlight
post_number: 4
blog_post: 2026-02-23 - Why learn linux before containerisation
generated: 2026-05-26T14:21:55.398511
---

Docker Desktop and Rancher Desktop look similar on the surface.
Under the hood, they handle resources very differently.

I switched to Rancher Desktop to run a local K3s cluster while following a Linux and Kubernetes course. The switch was smooth. Everything worked.

Until I went back to my homelab devcontainers.

Here's what I didn't understand:

Both tools run a Linux VM on macOS — containers don't run natively on the host kernel. But Rancher Desktop is more explicit about resource allocation. My VM was capped at 2 GB.

That 2 GB was shared between:
- K3s cluster
- Kubernetes experiment containers
- Devcontainer environments

Not enough. The OOM killer started terminating processes.

Key difference:

Docker Desktop: resource limits configurable, but less exposed
Rancher Desktop: explicit VM allocation — closer to real infrastructure behavior

The explicitness that tripped me up is actually the feature. You're forced to think about resource constraints, just like in production.

Before switching container runtimes: understand the VM model. Know your memory limits. Know what's sharing that memory.

The tool wasn't the problem.
The missing mental model was.

#docker #rancher #kubernetes #devcontainers #homelab
