---
angle: tool spotlight
post_number: 4
blog_post: 2025-09-02 - Network-configuration
generated: 2026-05-26T14:16:09.049306
---

dnsmasq is the most underrated tool in a homelab stack.
Full DHCP server in one lightweight binary.

I needed DHCP on my Proxmox host to serve a private virtual bridge for my Kubernetes nodes. Didn't want to spin up a full ISC DHCP server for 4 machines.

dnsmasq handles it in one config file:

/etc/dnsmasq.d/vmbr1.conf
```
interface=vmbr1
dhcp-range=10.0.0.10,10.0.0.99,12h
dhcp-host=<MAC>,10.0.0.10
dhcp-host=<MAC>,10.0.0.11
```

That's it. Restart the service. Nodes get stable IPs on boot.

What dnsmasq does well:
- DHCP with static reservations by MAC
- DNS caching
- Tiny footprint — fits on the host without eating resources
- Config is readable by humans, not just sysadmins

I've seen people stand up VMs just to run DHCP. dnsmasq on the hypervisor host is simpler and more resilient — if Proxmox is up, DHCP is up.

If you're building a homelab cluster and struggling with IP stability, this is the $0, 15-minute fix.

#homelab #proxmox #networking #selfhosted #linux
