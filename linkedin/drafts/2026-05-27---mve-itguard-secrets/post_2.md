---
angle: tool spotlight
post_number: 2
blog_post: 2026-05-27 - mve-itguard-secrets
generated: 2026-07-28T16:36:03.107701
---

GPG made me dread encrypting files.

AGE made a key pair just two strings.

If you've fought GPG — the keyring, the subkeys, the expiry dates, the web of trust, the flags you copy from Stack Overflow without understanding them — AGE feels like a joke at first. Too simple.

One command:

age-keygen -o keys.txt

You get a private key (one line) and a public key (one age1... string). Encrypt to the public key. Decrypt with the private one.

No keyring. No key servers. No expiry management. No trust model to configure. Nothing to misconfigure at 2am.

In my homelab, that one key pair is the root of trust for the entire project. Every secret — deploy credentials, backup passwords, API tokens — is encrypted to a single AGE public key and committed to Git as ciphertext.

Pair it with SOPS and you get value-level encryption of dotenv and YAML files, with diffs you can actually read.

Sometimes the best security tool is the one with the fewest ways to hold it wrong.

#encryption #security #opensource #devops
