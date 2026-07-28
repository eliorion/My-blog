---
angle: technical deep-dive
post_number: 2
blog_post: 2026-05-31 - mve-itguard-backup
generated: 2026-07-28T16:39:59.649805
---

My backup nodes live behind CGNAT with no public IP, no port forwarding, no DDNS.
They still receive encrypted backups from my server every night at 3 AM.

The problem: the 3-2-1 rule wants one copy off-site. For a homelab, that means a box at a friend's or family member's place. But most residential connections today share a public IP address — inbound connections are simply impossible.

The solution: Cloudflare Tunnel on each node.

cloudflared establishes an outbound connection from the node to Cloudflare's network, and Cloudflare handles the routing. The production server just talks HTTPS to a hostname.

The flow:
prod server → HTTPS → Cloudflare → cloudflared on the node → rest-server on localhost:8000

Each node gets its own tunnel token. No shared infrastructure. If one node's tunnel dies, only that node's backups are affected — the others still get updated.

And trust? Not needed. Restic encrypts every block before it leaves my server. The nodes store ciphertext. My friend could pull the drive and read nothing.

That's the part I like most: geographic redundancy without asking anyone to trust me with their network, or me trusting them with my data.

Hardware requirement for a secondary node: a Raspberry Pi Zero and a 64 GB drive.

#cloudflare #homelab #backup #restic #networking
