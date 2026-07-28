---
angle: technical deep-dive
post_number: 2
blog_post: 2026-05-30 - mve-itguard-key-rotation
generated: 2026-07-28T16:38:46.772107
---

The trickiest part of automating key rotation: you need the OLD key to hand over to the NEW one.
Here's how my CI pipeline does it with SOPS and age.

1. A rotate job runs before every deploy. It compares the AGE-SECRET-KEY line from the server's key file against the SOPS_AGE_KEY GitHub secret. Identical? Exit 0 in milliseconds.

2. On mismatch, both keys go into mktemp files, mode 600, cleaned up by a trap on EXIT no matter how the script ends.

3. sed swaps the old public key for the new one in every .sops.yaml. From that moment, anything newly encrypted targets the new key.

4. The clever bit: SOPS_AGE_KEY_FILE points at the OLD key while sops updatekeys runs on each .enc file. SOPS decrypts with the old key, reads the new public key from .sops.yaml, and re-encrypts. Atomic per file — a failure leaves the original untouched.

5. The new key is written to the server through a read-write volume mount, and the pipeline commits the re-encrypted files back to main.

One file needs special treatment: keys.txt.enc contains the private key itself, encrypted. updatekeys would only change what it's encrypted TO, not what's inside. That one gets rebuilt from scratch with the new key.

No secrets in the logs — only public keys. The old key exists exactly as long as the script runs.

#sops #encryption #githubactions #devsecops #cicd
