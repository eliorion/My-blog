---
angle: tool spotlight
post_number: 4
blog_post: 2026-05-30 - mve-itguard-key-rotation
generated: 2026-07-28T16:38:46.773005
---

SOPS + age is the most underrated secrets combo in the self-hosted world.
Encrypted secrets, living in git, no vault server to babysit.

How it works:

age gives you a tiny keypair — one line of private key, one line of public key. No PGP ceremony.

SOPS encrypts your YAML and .env files value-by-value. Keys stay readable, values get encrypted. Diffs still make sense in code review.

A .sops.yaml file in each directory declares which public key to encrypt to. Add a new secret, SOPS picks the right key automatically.

The feature that sold me: sops updatekeys. When you rotate your keypair, it decrypts each file with the old key and re-encrypts with the new one — atomically. A failure mid-file leaves the original untouched.

I built my entire key rotation automation on that guarantee. My CI pipeline detects a new key, runs updatekeys across nine encrypted files in four directories, commits the result, and deploys. If anything fails, nothing is half-rotated.

For a homelab or a small team, this beats running a secrets manager 24/7: no extra infrastructure, no single point of failure, full git history of every change.

Sometimes the boring, file-based tool is the right tool.

#sops #age #secretsmanagement #homelab #devsecops
