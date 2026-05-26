---
angle: behind-the-scenes
post_number: 4
blog_post: 2026-05-25 - mve-itguard-gitops
generated: 2026-05-26T14:29:18.968732
---

My CI runner cannot touch Docker.
My deploy runner can — but only through a restricted proxy.

Both are self-hosted runners on the same production server. GitHub-hosted runners can't reach a home network, so self-hosted is required.

But that creates a real risk: any pull request can trigger CI. If that runner has Docker access, an attacker can read secrets, inspect containers, or manipulate running services.

So I split them:

runner-ci (label: ci)
→ No Docker access whatsoever
→ Runs lint + validation only
→ Triggered by PRs and pushes to main

runner-deploy (label: deploy)
→ Docker access via socket proxy only
→ Only starts after CI passes on main
→ Never triggered by pull requests

The socket proxy sits between the runner and the Docker daemon:

runner-deploy → TCP:2375 → socket-proxy → unix socket → dockerd

The proxy allows only what `docker compose` needs: CONTAINERS, IMAGES, NETWORKS, VOLUMES, POST, INFO, PING. No direct socket access. No unrestricted API.

CI jobs never see production. Deploy jobs never run unvalidated code.

Two runners, two labels, completely different trust levels. Simple to configure, hard to bypass accidentally.

#security #selfhosted #githubactions #docker #homelab
