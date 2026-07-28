---
angle: hot take
post_number: 1
blog_post: 2026-07-14 - A ransomware-resistant backup fleet
generated: 2026-07-27T21:29:46.142158
---

A backup your production system can delete is not disaster recovery.
It's a convenience copy.

My Kubernetes cluster had it all on paper: etcd snapshots, Postgres WAL archives streaming to object storage, replicated volumes.

Then I asked one question: who can delete these?

Answer: the cluster itself. The credentials that write the backups live inside it. Anyone who owns the cluster — an attacker, or me fat-fingering something with cluster-admin — owns the backups too.

Ransomware operators built their playbook on this. Step one: encrypt the data. Step two: delete the backups. If both are reachable with the same credentials, you never had disaster recovery.

So I built a separate fleet with one design goal: nothing in production can destroy it.

- Different OS, different secrets, different control plane
- Prod's S3 credentials can write backups — and nothing else
- Read-only ZFS snapshots underneath, out of reach of any S3 API call
- Replicas spread across three physical locations

Worst case, an attacker with prod access can upload garbage. They cannot destroy history.

A backup system is a security system. And a security system starts with naming your attacker — not picking your tools.

#disasterrecovery #ransomware #backup #kubernetes #homelab
