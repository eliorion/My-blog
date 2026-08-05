---
angle: technical deep-dive
post_number: 2
blog_post: 2025-09-02 - Network-configuration
generated: 2026-05-26T14:16:09.048401
published: 2026-08-05T10:16:55.143046
post_urn: urn:li:share:7490712433788088320
---

Static IPs in a Kubernetes homelab without a real router.
One config file, 10 lines, done.

The problem: Proxmox VMs change IPs when the environment changes. Talos Linux nodes need stable endpoints to form a cluster. These two facts do not get along.

The fix: a dedicated virtual bridge (vmbr1) + dnsmasq as a lightweight DHCP server on the Proxmox host.

Setup:
1. Create vmbr1 in Proxmox — takes 2 minutes
2. Attach it as a second network interface to every VM
3. Install dnsmasq on the Proxmox host
4. Drop a config file at /etc/dnsmasq.d/vmbr1.conf

The config:
```
interface=vmbr1
dhcp-range=10.0.0.10,10.0.0.99,12h
dhcp-host=AA:BB:CC:DD:EE:01,10.0.0.10  # control plane
dhcp-host=AA:BB:CC:DD:EE:02,10.0.0.11  # worker 0
dhcp-host=AA:BB:CC:DD:EE:03,10.0.0.12  # worker 1
dhcp-host=AA:BB:CC:DD:EE:04,10.0.0.100 # cluster manager
```

MAC address → fixed IP. Every reboot, every location, same addresses.

VMs keep vmbr0 for internet. vmbr1 handles all intra-cluster traffic.

Last step: update controlplane.yaml, worker.yaml, and the Talos endpoint to point at the vmbr1 IPs. Otherwise the cluster forms correctly and then immediately can't reach itself.

#proxmox #taloslinux #kubernetes #homelab #networking
