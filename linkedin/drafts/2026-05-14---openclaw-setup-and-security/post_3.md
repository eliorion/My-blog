---
angle: technical deep-dive
post_number: 3
blog_post: 2026-05-14 - OpenClaw setup and security
generated: 2026-05-26T14:26:53.186701
---

App-layer auth vs network-layer isolation:
One is a door lock. The other removes the door from the building.

For my self-hosted AI agent (OpenClaw), I chose the second option.

The config that does it:

{
  "gateway": {
    "bind": "tailnet",
    "tailscale": { "mode": "off" }
  }
}

With bind: "tailnet", the gateway listens only on the Tailscale IP of the host.
Not 0.0.0.0. Not localhost. Private mesh interface only.

What this means in practice:

1. Gateway is invisible from the public internet
2. Firewall misconfiguration doesn't matter — public interface has nothing
3. A zero-day in the gateway is useless if you can't reach the socket

The auth layer still exists. It's just not the first line of defense.

Tailscale's WireGuard mesh handles access control at the network level.
The agent sees only traffic from devices I've explicitly authorized.

Defense in depth, done simply:
- Layer 1: Tailscale network (who can even connect)
- Layer 2: Application auth (who can use the agent)

For anything with real shell access on a real machine, I won't settle for less.

#tailscale #wireguard #security #selfhosted #homelab
