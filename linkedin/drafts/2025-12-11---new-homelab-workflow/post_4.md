---
angle: key lesson
post_number: 4
blog_post: 2025-12-11 - New-homelab-workflow
generated: 2026-05-26T14:17:50.608826
---

Rebuilding my Kubernetes cluster used to take hours.
Now it takes minutes. One architectural decision changed everything.

Old way:
→ VMs created manually in Proxmox
→ Every tool installed locally
→ Nothing reproducible
→ One failed node = manual rebuild, one by one

New way:
→ Pulumi (Python) declares the full Proxmox VM layer
→ All tooling lives in a devcontainer — nothing on the host
→ Dotfiles handle machine setup instantly

The key insight I kept missing: reproducibility beats cleverness.

I spent weeks on a "clever" setup the first time.
Custom Docker containers for tool management, complex configs, lots of moving parts.

It broke constantly. After a week away from the project I couldn't even remember how it worked.

The new setup is simpler on the surface but rock solid underneath.
Declare your infrastructure. Version-control it. Let the devcontainer handle the rest.

If I was starting a homelab today, I'd skip straight to IaC + devcontainers from day one.
The upfront cost is real. So is the payoff.

#kubernetes #infrastructure as code #homelab #proxmox #pulumi
