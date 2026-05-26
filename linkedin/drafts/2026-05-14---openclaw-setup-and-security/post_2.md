---
angle: personal story
post_number: 2
blog_post: 2026-05-14 - OpenClaw setup and security
generated: 2026-05-26T14:26:53.185422
---

I wanted an AI agent that could actually help with my homelab.
Not one that sends my entire workspace to a SaaS.

So I set up OpenClaw — a self-hosted agent platform on my Linux box.
It reads my files, runs commands, spawns subagents.
Real power. Real risk.

The challenge: access it from all my devices without opening a public port.

What I refused to do:
✗ Port forward on my router
✗ Public reverse proxy with a password
✗ Any public IP at all

What I did instead: Tailscale.

Tailscale creates a private WireGuard mesh between my devices.
Each device gets a stable 100.x.y.z IP.
Only authorized devices can reach each other.

No public IP. No port to scan. Nothing visible from the internet.

I bound the gateway directly to the Tailscale interface.
Two lines of config. The whole thing just works.

Now I reach my agent from my laptop, my phone, anywhere on my tailnet.
No one else can even see it exists.

I didn't have to choose between convenience and security.
Tailscale gives me both.

#homelab #selfhosted #tailscale #AI #homelabsecurity
