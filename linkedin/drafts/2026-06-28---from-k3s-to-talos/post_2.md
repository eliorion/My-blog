---
angle: technical deep-dive
post_number: 2
blog_post: 2026-06-28 - From K3s to Talos
generated: 2026-07-27T20:05:58.380098
---

You can't migrate a live Kubernetes cluster by flipping a flag.
Here's the order that actually worked.

I moved my homelab from K3s to Talos Linux with real workloads running: databases, an identity provider, CI runners. The trick was building the new cluster alongside the old one and migrating tier by tier, keeping K3s alive until each layer was proven.

The order was deliberate:

1. Storage first — Longhorn up and running, so stateful workloads have somewhere to land.

2. Infrastructure controllers — Cloudflare tunnel, ingress, certificates.

3. Monitoring — move observability early, so the new cluster is visible from day one.

4. Databases — CloudNativePG, seeded from backups in Cloudflare R2, volumes on Longhorn.

5. Apps last — once everything they depend on already works.

One surprise: Talos enforces Pod Security Admission more strictly than K3s. Every workload that quietly relied on privileges got exposed — monitoring, CI runners, Longhorn all needed explicit privileged PSA labels.

Annoying in the moment. But that's exactly the kind of thing you want visible instead of implicit.

Dependencies flow upward. Migrate from the bottom.

#kubernetes #talos #k3s #longhorn #migration
