---
angle: hot take / key lesson
post_number: 1
blog_post: 2026-05-30 - mve-itguard-key-rotation
generated: 2026-07-28T16:38:46.771439
---

Encryption key rotation is the security chore everyone agrees on and almost nobody does.
It's not laziness. It's friction.

In my homelab, one AGE key encrypts nine files across four directories. Rotating it manually means:

- generating a new key
- updating four .sops.yaml files
- running sops updatekeys on every encrypted file
- updating the key on the production server
- updating the GitHub Actions secret

Miss one step, or do them in the wrong order, and deployments break until you figure out which key is out of sync with which file.

So I moved the whole thing into CI. On every push, a dedicated job compares the key on the server with the key in the GitHub secret.

If they match: exit in milliseconds, deploy proceeds.
If they differ: the pipeline re-encrypts everything with the new key, commits the result, and deploys.

Rotation is now two steps for me: update the server key, update the secret. Push. Done.

The real lesson: security practices don't fail because people don't care. They fail because they're painful.

Make the safe thing the easy thing, and it actually happens.

#devops #security #cicd #automation #homelab
