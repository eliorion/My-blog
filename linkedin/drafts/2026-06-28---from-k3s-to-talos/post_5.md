---
angle: tool spotlight
post_number: 5
blog_post: 2026-06-28 - From K3s to Talos
generated: 2026-07-27T20:05:58.381437
---

One Kubernetes operator replaced my reverse proxy setup, my port forwarding, and my exposed API server.
And nothing touches the public internet anymore.

The Tailscale Kubernetes operator is doing three distinct jobs in my homelab:

1. Internal UIs on the tailnet.
The Longhorn dashboard, admin UI, and JupyterLab sandboxes are published straight to my private mesh network. Reachable from my laptop or phone anywhere — invisible to everyone else. No public exposure, no extra reverse proxy.

2. Egress proxy pool.
My scraping platform routes outbound traffic through dedicated Tailscale egress proxies, so each scraping lane gets its source IP through the tailnet.

3. Kubernetes API without public exposure.
The operator's API server proxy puts the cluster's control plane on the tailnet. I run kubectl from anywhere I am, and the API is never open to the internet.

Before this, my answer to 'how do I reach internal tools?' was a pile of tunnels and 'I'll deal with it later.'

Now it's one mesh network, zero public ports, and the same access model whether I'm home or not.

Public apps still go through Cloudflare tunnels. But private things are finally, actually private.

#tailscale #kubernetes #homelab #networking #selfhosted
