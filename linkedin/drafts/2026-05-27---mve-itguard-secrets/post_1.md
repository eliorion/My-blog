---
angle: hot take
post_number: 1
blog_post: 2026-05-27 - mve-itguard-secrets
generated: 2026-07-28T16:36:03.107429
---

I commit secrets to Git. On purpose.

Before you close this tab — the ciphertext is the point.

Every project that deploys somewhere real has secrets. Tokens, passwords, API keys. And GitOps forces the question: if Git is the single source of truth, where do the secrets live?

The usual answers all leak completeness:

- Env vars in CI? Now your secrets live in GitHub Actions settings, disconnected from the code that uses them.
- Vault? Great for a team running a SaaS. Heavy infrastructure for a single-server homelab.
- .gitignore + private repo + hope? Works until you clone on a new machine a year later and half the setup lives in your head.

My approach for mve-itguard: encrypt every secret with SOPS + AGE and commit the .enc files.

Cloudflare tokens, MQTT credentials, backup passwords, even the GitHub App private key — all in the repo, all ciphertext, all useless without the one AGE private key.

Clone the repo on any machine with that key, and you have everything needed to understand, modify, and operate the system. Nothing lives in someone's head.

The trade-off is honest: that private key is now the single point of failure. Treat it like a root credential — backed up twice, never committed in plaintext.

But "one key to protect carefully" beats "a dozen secrets scattered across CI settings and someone's memory."

#gitops #devops #security #homelab
