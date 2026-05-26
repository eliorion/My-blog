---
angle: personal story
post_number: 5
blog_post: 2026-05-25 - mve-itguard-gitops
generated: 2026-05-26T14:29:18.971158
---

I haven't SSH'd into my server to deploy in months.
Every deployment is triggered by a git push.

This was a hard constraint I set for my home security system: production deployments must never require SSH.

No logging into the server to run commands. No deployment script over a remote shell. No "quick fix" pushed directly to avoid the pipeline.

When a commit lands on main:
1. CI runs lint and validation automatically
2. If CI passes, the deploy pipeline triggers
3. The self-hosted runner — already running on the server — checks out the repo
4. Secrets are decrypted from encrypted files committed to Git
5. `docker compose up --pull always --remove-orphans` runs
6. The decryption key is immediately deleted from disk (even on failure)

Every change is auditable. Every deploy is reproducible. The running state of the server is always a consequence of what the repository declares.

SSH still exists for real operational tasks: debugging a failing container, checking logs, hardware changes. But that's rare.

The interesting side effect: I stopped making manual "temporary" changes that never get committed. If it's not in Git, it doesn't exist.

That discipline is the actual value of GitOps. The automation just enforces it.

#gitops #devops #automation #homelab #selfhosted
