---
angle: behind-the-scenes
post_number: 5
blog_post: 2025-09-02 - Network-configuration
generated: 2026-05-26T14:16:09.049665
---

Real homelab reality: you don't have a fixed location, a server room, or a router you control.
You improvise.

My setup:
- Server lives at one place
- I work at two different locations
- One has a proper network. One is just my PC and the server connected with a cable.

No DHCP server on a direct cable connection means no IP address. No IP address means no SSH. No SSH means no Proxmox.

First hack: Windows Internet Connection Sharing over Ethernet. The PC becomes a minimal DHCP server. Server gets 192.168.137.2. Done. Ugly, but it works.

Second problem: my VM IPs change depending on which network I'm on. Kubernetes does not enjoy this.

Second hack: virtual bridge in Proxmox isolated from the physical network + dnsmasq for private DHCP. Now the cluster has stable 10.0.0.x addresses regardless of where the server is plugged in.

This isn't how a production setup works.
But that's not the point.

The point is learning to solve real constraints with the tools you have.

Every limitation you work around teaches you something a clean lab environment never would.

The messy setups are where the real learning happens.

#homelab #proxmox #kubernetes #selfhosted #devops
