---
angle: behind-the-scenes
post_number: 6
blog_post: 2026-06-28 - From K3s to Talos
generated: 2026-07-27T20:05:58.381911
---

My CI pipeline runs inside the same cluster it deploys to.
Sounds circular. Works beautifully.

My homelab cluster is private — no public API, everything behind a tailnet. Which raises a question: how does CI reach it?

Answer: it doesn't reach in. It already lives there.

GitHub Actions jobs run on the cluster itself via Actions Runner Controller. A default runner pool handles normal jobs, and a larger pool takes the heavy k3d end-to-end tests.

The unglamorous details that made it reliable:

A Nexus cache inside the cluster. Runners pull dependencies through it, so builds stay fast and I stopped hitting public registry rate limits.

Reflector for secrets. Image pull secrets across many namespaces were a constant headache — one central ghcr pull secret is now mirrored everywhere it's needed, with ordering set so the secret exists before anything tries to pull.

Telegram alerts. If a Flux HelmRelease fails, my phone knows before I do. Combined with automatic rollback, most failures either fix themselves or announce themselves loudly.

None of this is the exciting part of a homelab. All of it is why I trust the thing.

The boring plumbing is the project.

#cicd #githubactions #kubernetes #homelab #flux
