---
angle: key lesson
post_number: 4
blog_post: 2026-05-27 - mve-itguard-secrets
generated: 2026-07-28T16:36:03.107987
---

My whole homelab's security reduces to one file.

Lose it, and every secret I own turns into permanent noise.

That's the trade I made with SOPS + AGE: every credential in the project — deploy passwords, API tokens, backup keys — is encrypted to one AGE key pair, and the ciphertext lives in Git.

The upside is real. The repo is genuinely complete. New machine? Clone + one key file = fully operational.

The lesson that took a while to sink in: you haven't eliminated the secret management problem. You've compressed it into one key.

And one key demands root-credential discipline:

- Backed up in at least two independent places (password manager + encrypted USB)
- Never in Git as plaintext
- Rotated the moment you suspect exposure

My favorite detail of the setup: the AGE private key is ALSO stored in the repo — encrypted with itself.

Sounds circular. But it's a free self-referential backup: if the key exists somewhere but you've lost track of which file or machine holds it, decrypting that one file recovers it. And it re-encrypts automatically during key rotation. Zero maintenance.

Simplifying security rarely means removing the hard part. It means moving all of it into one place you can actually defend.

#security #encryption #homelab #lessonslearned
