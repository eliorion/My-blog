---
angle: tool spotlight
post_number: 2
blog_post: 2025-12-11 - New-homelab-workflow
generated: 2026-05-26T14:17:50.607022
---

My Mac has exactly 2 tools installed for my entire homelab.
DevPod and Docker. That's it.

Everything else — kubectl, helm, talosctl, Pulumi, direnv — lives inside a devcontainer.

Here's why this matters:

Before: tools installed directly on the host, version conflicts everywhere, one bad update could corrupt my entire environment.

After: everything isolated. If my workstation dies, I clone the repo, launch the devcontainer, and I'm back to the exact same environment in minutes.

The stack:
→ DevPod — manages devcontainers across projects
→ Devcontainer — isolated env with all project dependencies
→ Dotfiles — synced config that makes any machine feel like home instantly
→ Pulumi — IaC in Python (more natural for me than HCL)

No more "works on my machine" — even for my own machine.

If you're running a homelab and still installing tools locally, try devcontainers.
First setup takes time. You won't go back.

#devcontainers #homelab #kubernetes #developer tools #infrastructure
