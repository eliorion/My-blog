---
angle: key lesson
post_number: 3
blog_post: 2025-09-02 - Network-configuration
generated: 2026-05-26T14:16:09.048881
published: 2026-08-06T10:18:30.809202
post_urn: urn:li:share:7491075222796742656
---

Your cluster config can be perfect and your cluster still won't work.
Network layer lies to you silently.

I spent time debugging Talos Linux configs before realizing the nodes couldn't even see each other on the network.

No error. No timeout message pointing at the real cause. Just... nothing.

Here's what I learned the hard way:

A virtual bridge in Proxmox is not a network.
It's a switch with no DHCP — machines connect but get no address.
They sit in silence.

Kubernetes assumes stable, reachable IPs.
Talos bootstraps from a specific endpoint.
If that IP drifts between your office and your home setup, the cluster breaks in ways that look like software problems but are actually physical topology problems.

Fix the foundation first:
- Stable IPs via DHCP reservation (MAC → IP)
- Dedicated interface for cluster traffic, separate from WAN
- Then touch the cluster config

The boring infrastructure work is what makes the interesting stuff possible.

Homelab teaches you this faster than any course.

#homelab #kubernetes #taloslinux #devops #selfhosted
