---
angle: tool spotlight
post_number: 3
blog_post: 2025-12-11 - Persistent-volume-with-nfs
generated: 2026-05-26T14:19:01.933020
---

TrueNAS + NFS + Kubernetes.
Three tools that turned my homelab storage from "it works" to "it works reliably."

Here's the architecture:

TrueNAS (on Proxmox) → NFS share → nfs-csi driver in Talos K8s → PersistentVolumeClaim

Why this combo?

TrueNAS handles actual data storage with ZFS underneath — snapshots, integrity checks, built-in backup tools.

NFS gives every Kubernetes node access to the same volume. No more "the data lives on node-2" problem.

The nfs-csi driver means Kubernetes provisions volumes dynamically. Create a PVC, the storage appears.

What I learned the hard way:
→ Node-local storage seems easy but breaks when nodes fail
→ Shared NFS storage is more moving parts upfront, way more resilient long-term
→ TrueNAS + ZFS is the right complexity level for a serious homelab

All of this managed with Pulumi IaC on Talos Linux. Everything reproducible from code.

If you're building a homelab K8s setup, invest in storage architecture early. You'll thank yourself later.

#truenas #kubernetes #homelab #nfs #iac
