---
angle: personal story
post_number: 1
blog_post: 2026-06-28 - From K3s to Talos
generated: 2026-07-27T20:05:58.379385
---

Last month I deleted the VM that taught me Kubernetes.
No backup. No regrets.

My first homelab cluster was a single-node K3s box: Flux, SOPS-encrypted secrets, one bookmark manager behind a Cloudflare tunnel. It taught me GitOps end to end.

Then it stopped being a demo.

A scraping platform. Keycloak. Monitoring. Self-hosted CI runners. Suddenly the cluster carried things I couldn't afford to lose, and a hand-installed VM I had to patch and babysit wasn't good enough anymore.

So I rebuilt it on Talos Linux: an immutable OS with no SSH, no shell, no package manager. The whole machine is declared through an API, the same way the cluster is declared in Git.

I built the new cluster next to the old one, moved workloads tier by tier, and when the last one was proven, I deleted the K3s VM, revoked its deploy key, and closed that chapter.

The homelab used to be a place I experimented and rebuilt by hand.

Now it's infrastructure I can reason about — declared in Git, from the operating system up.

That shift, from 'my pet server' to 'a system I trust', taught me more about operations than any tutorial ever did.

#homelab #kubernetes #talos #gitops #devops
