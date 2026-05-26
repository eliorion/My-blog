---
angle: hot take
post_number: 3
blog_post: 2025-12-11 - New-homelab-workflow
generated: 2026-05-26T14:17:50.608267
---

Most homelab setups are one bad update away from breaking completely.
Mine was. I ignored it for too long.

talosctl, kubectl, everything else — all installed directly on my Mac.
I had to watch versions constantly.
One update at the wrong time and the whole environment would silently break.

It "worked" — but it wasn't stable. And it wasn't fun.

The fix wasn't more discipline. It was better architecture.

Now:
→ Entire toolchain lives in a devcontainer
→ Proxmox VMs created with IaC — full cluster rebuild in minutes
→ Dotfiles synced so any machine is ready in seconds

The homelab stopped being a source of stress and became something I actually enjoy using.

That shift — from "it works but it's painful" to "it works and it's clean" — is wildly underrated in the homelab community.

Everyone talks about what they're running. Nobody talks about how sustainable the workflow actually is.

What's the thing in your homelab that "works" but you secretly hate maintaining?

#homelab #infrastructure #devops #talos #selfhosted
