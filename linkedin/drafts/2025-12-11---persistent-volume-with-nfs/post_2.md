---
angle: key lesson
post_number: 2
blog_post: 2025-12-11 - Persistent-volume-with-nfs
generated: 2026-05-26T14:19:01.932708
---

K8s tutorials teach you Deployments and Services.
Nobody warns you about persistent storage until it's too late.

Most beginner guides stop at stateless apps. Spin up a pod, expose a service, done.

Then reality hits: your app needs to write data. And keep it.

The "obvious" solution: mount a directory on the node where the pod runs.

Here's what nobody mentions:
→ Pod dies → reschedules on a different node → your data is gone
→ One node fails → service dies with it
→ Backup strategy? Non-existent

Kubernetes wasn't built for data to live on nodes. It was built so workloads can move.

The fix: a PersistentVolume backed by shared storage — in my case, TrueNAS over NFS.

Setup takes longer. But now:
→ Any node can access the data
→ TrueNAS handles backups
→ Pod failures don't mean data loss

If you're running stateful workloads in K8s, skip the shortcut. Start with a real storage backend from day one.

#kubernetes #k8s #infrastructure #homelab #devops
