---
angle: personal story
post_number: 6
blog_post: 2026-05-27 - mve-itguard-secrets
generated: 2026-07-28T16:36:03.108233
---

Every project has that one .env file that exists on exactly one machine.

I used to be that guy. Private repo, .gitignore for .env, a manual setup step "documented" in my head.

It works. Until it doesn't:

- You clone the repo on a fresh machine and the app won't start.
- You try to reproduce the setup a year later and can't remember which value goes where.
- The repo claims to be the source of truth, but half the truth lives outside it.

GitOps made me stop ignoring this. If Git is the single source of truth, secrets have to live there too — just not in plaintext.

Now every secret in my homelab is encrypted with SOPS + AGE and committed as an .enc file. Cloudflare token, MQTT credentials, backup passwords — all versioned, all diffable, all recoverable.

Onboarding a new machine went from archaeology session to: clone the repo, drop one key file in place, done.

No Vault server to babysit. No secrets scattered across CI settings. One key to guard, and everything else takes care of itself.

If your setup relies on a file only .gitignore knows about, that's not secret management. That's a time bomb with your name on it.

#gitops #homelab #devops #secrets
