---
angle: personal story
post_number: 1
blog_post: 2025-09-02 - Network-configuration
generated: 2026-05-26T14:16:09.046221
published: 2026-08-04T10:20:40.480963
post_urn: urn:li:share:7490350989661691905
---

I lost 4 hours to network problems that had nothing to do with Kubernetes.
Here's what actually broke my homelab.

I work between two locations. One has a proper router. The other has my server, my PC, and an Ethernet cable connecting them directly.

No router. No DHCP. No IP address for my Proxmox server.

Fix #1: force Windows to share the WiFi connection over Ethernet. Suddenly the server gets 192.168.137.2, the PC is .1, and SSH works. Two hours gone.

Fix #2 was sneakier.

I created a virtual bridge (vmbr1) in Proxmox so my 4 VMs would always have the same IPs regardless of which location I'm in. Connected all the machines to it.

Nothing worked.

A virtual bridge with no DHCP is just four machines staring at each other. Nobody has an IP. Nobody can talk. Two more hours gone.

Solution: install dnsmasq on the Proxmox host. One config file. Static IPs tied to MAC addresses for each node.

Now every machine gets the same IP every time, wherever I plug in.

The lesson nobody tells you about homelabs:
half the problems aren't in the tech you're building.
They're in the infrastructure under it.

#homelab #proxmox #selfhosted #kubernetes #networking
