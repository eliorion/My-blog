---
angle: tool spotlight
post_number: 4
blog_post: 2026-07-14 - A ransomware-resistant backup fleet
generated: 2026-07-27T21:29:46.143758
---

My backup cluster is 4 mismatched machines in 3 different buildings.
The tool that makes this work: Garage.

When people want self-hosted S3, they usually reach for MinIO. But my constraint was different: a handful of heterogeneous boxes, spread across physical sites, forming one storage cluster over a VPN.

That's exactly the shape Garage was built for.

My layout:
- 1 onsite storage node
- 2 offsite storage nodes, each at a different location
- 1 gateway node with zero capacity — holds no data, only serves the S3 API

Each storage node sits in its own zone, so Garage places replicas across physical locations automatically. A house fire, a stolen box, or a dead disk takes out one copy — not the data.

The network story is just as simple: Garage's RPC and S3 listeners bind to Tailscale IPs. There is no public endpoint anywhere in the fleet. If you're not on the tailnet, the cluster doesn't exist.

Its job: receive etcd snapshots, Postgres PITR archives, and volume backups from my production cluster — and survive anything that happens to that cluster.

Lightweight, S3-compatible, designed for exactly the hardware homelabbers actually have.

Sometimes the less famous tool is the better fit.

#selfhosted #s3 #garage #tailscale #homelab
