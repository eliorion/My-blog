---
angle: personal story
post_number: 3
blog_post: 2026-07-14 - A ransomware-resistant backup fleet
generated: 2026-07-27T21:29:46.143301
---

I deliberately built a weak point into my backup fleet.
Writing down why was the most useful part of the design.

One of my four backup nodes doubles as my dev workstation. It hosts my DevPod containers, and rootless podman couldn't give me what I needed — privileged containers, docker-in-docker, ports below 1024. So it runs root docker, and my user is in the docker group.

The docker group is root-equivalent. `docker run -v /:/host` hands out uid 0. And uid 0 can destroy the ZFS snapshots that protect my backups from ransomware.

So on that node, my carefully built snapshot moat doesn't hold against a container escape or a malicious dependency arriving through some package.json. VPN-only networking doesn't help either — the threat isn't the network perimeter, it's the code I voluntarily run.

I could have pretended this was fine. Instead, I wrote the consequence into the design:

This node is only the onsite copy. The real ransomware defense is the two offsite nodes, whose moats are intact — and which will never, ever take on a workstation role.

Every system has a weakest point. The difference between a solid design and a fragile one isn't the absence of weaknesses.

It's whether you can name them — and whether anything important depends on the parts you know are soft.

#security #homelab #docker #threatmodeling
