---
angle: tool spotlight
post_number: 4
blog_post: 2026-05-29 - mve-itguard-bootstrap
generated: 2026-07-27T20:03:40.273753
published: 2026-07-28T12:34:15.698191  # posted manually
---

Every secret my server needs is committed to Git.
Encrypted with a tool you can learn in an afternoon.

The stack: SOPS + age.

age is a modern encryption tool. One keypair, no GPG ceremony.
SOPS encrypts files with it, and plays nicely with YAML, JSON and dotenv formats.

How I use it in my homelab:

- CI runner credentials: ci.env.enc, deploy.env.enc, rotate.env.enc
- App secrets: Cloudflare tunnel token, camera passwords, MQTT host
- Infra credentials: sysadmin password, hostname — for human operators, not automation
- Even a GitHub App private key, base64-encoded and encrypted

The public key goes in .sops.yaml files in the repo. Anyone can encrypt.

The private key exists in exactly three places: my dev machine, one GitHub Actions secret, and /etc/sops/age/keys.txt on the server — root-only, mode 600.

The payoff during provisioning:

Plaintext secrets exist on disk for seconds. Decrypted, read by docker compose, immediately wiped. The GitHub App key never touches disk at all — decrypted straight into memory.

Result: git clone + one key = fully reproducible server.

If you're still keeping server secrets in a password manager and pasting them over SSH, try sops. It changes how you think about infrastructure.

#sops #encryption #secretsmanagement #devops #homelab
