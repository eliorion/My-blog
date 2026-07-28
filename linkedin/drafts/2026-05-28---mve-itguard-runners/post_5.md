---
angle: technical deep-dive
post_number: 5
blog_post: 2026-05-28 - mve-itguard-runners
generated: 2026-07-28T16:37:35.483264
---

A leaked Personal Access Token is persistent access until a human notices.
My CI runners don't use PATs at all.

The usual way to register self-hosted GitHub Actions runners is a PAT. Two problems: it's tied to a person's account, and it lives until someone revokes it.

I switched to GitHub App authentication. The chain looks like this:

1. Container starts and signs a JWT with the App's private key — valid 10 minutes.

2. The JWT is exchanged for an installation token — valid 1 hour.

3. That's exchanged for a runner registration token — which can do exactly one thing: register runners.

The longest-lived credential in the whole chain expires in an hour. The most exposed one has a single capability.

Shutdown is symmetric: the runner fetches a fresh removal token and deregisters itself. If the container dies hard, the stale runner entry in GitHub is harmless — the next startup registers with --replace and overwrites it.

Nothing tied to a user account.
Nothing long-lived.
Nothing worth stealing.

If your runner registration still depends on a PAT taped to a service account, this swap is a weekend's work and removes an entire class of credential leak.

#githubactions #security #devops #cicd
