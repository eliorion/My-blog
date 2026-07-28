---
angle: behind-the-scenes
post_number: 5
blog_post: 2026-05-27 - mve-itguard-secrets
generated: 2026-07-28T16:36:03.108112
---

A trailing newline made my deploys fail. Silently.

The fix was three characters: printf '%s'.

Behind the scenes of my GitOps setup, the CI pipeline has to decrypt SOPS secrets during deploy. That means the AGE private key must exist on the runner — briefly.

The sequence:

1. Write the key from a GitHub Actions secret to disk:
printf '%s' "$SOPS_AGE_KEY" > ~/.config/sops/age/keys.txt
Then chmod 600.

2. Decrypt and inject into the deploy:
export $(sops -d --input-type dotenv --output-type dotenv app/security.env.enc)

3. Delete the key. Always. Even when the job fails:
rm -f ~/.config/sops/age/keys.txt

Why printf and not echo? Because echo appends a newline, and an AGE key file with a trailing newline fails decryption with no useful error message. One invisible byte, hours of debugging.

There's also a guardrail in CI that rejects any commit containing a plaintext .env file:

git ls-files | grep -E '\.env$' && exit 1

Because .gitignore is a suggestion, and humans (me) are the weakest link.

Secrets management isn't the fancy architecture diagram. It's these tiny, boring details — a newline, a chmod, an rm -f in the cleanup step — done right every single time.

#cicd #devops #githubactions #security
