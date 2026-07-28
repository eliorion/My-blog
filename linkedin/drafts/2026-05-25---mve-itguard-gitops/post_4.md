---
angle: behind-the-scenes
post_number: 4
blog_post: 2026-05-25 - mve-itguard-gitops
generated: 2026-07-27T19:10:18.019766
---

I haven't SSH'd into my server to deploy in months.
There is no shell in the deploy path at all.

The deploy runner already lives on the server. When a commit lands on main and CI passes:

1. The runner checks out the repo
2. It writes the AGE key from a GitHub secret and decrypts secrets with SOPS
3. docker compose up -d --remove-orphans --pull always
4. The key is deleted — in a step marked if: always(), so it disappears even when the deploy fails

What that buys me:

Secrets never sit on disk between deployments.
--pull always fetches fresh images on every deploy.
--remove-orphans removes containers Git no longer declares.

Drift doesn't accumulate. The running state is always a consequence of what's in the repository.

SSH still exists — for actual operations: a failing container, logs that aren't surfaced elsewhere, hardware changes.

But deploys? Edit a config. Open a PR. Merge.
Services update within seconds, without touching the server.

The day I stopped deploying by hand was the day deployments stopped being scary.

#gitops #automation #sops #devops
