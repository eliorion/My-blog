---
angle: personal story
post_number: 1
blog_post: 2025-12-11 - Persistent-volume-with-nfs
generated: 2026-05-26T14:19:01.931889
---

I've been learning Kubernetes for months.
Yesterday I finally hit the wall called PersistentVolume.

My learning status before this session:
✅ Deployments — understood
✅ NFS driver with TrueNAS — working
🟠 Calico, Traefik, Services — operational but not mastered
🔴 PV / PVC — not touched yet

I'd been avoiding it because I didn't need it yet.

Then I needed stateful storage. Time to face PV and PVC.

First instinct: store data directly on the node. Quick, easy, done.

Bad idea.

What happens if that node goes down? Pod reschedules on another node — and suddenly it can't find the data. Service dead.

Backups? Nightmare when data is scattered across nodes.

The right answer in my homelab: centralize on TrueNAS, expose via NFS, mount through a PVC.

More moving parts. But reliable, portable, and actually recoverable.

Sometimes the fast path is the wrong path.

What K8s concept forced you to rethink your approach?

#kubernetes #homelab #devops #k8s #learning
