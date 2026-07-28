---
angle: technical deep-dive
post_number: 3
blog_post: 2026-05-27 - mve-itguard-secrets
generated: 2026-07-28T16:36:03.107862
---

An encrypted secrets file that still gives you a useful Git diff.

That's the problem SOPS actually solves.

AGE (or GPG) encrypts a file as one opaque blob. Fine for binaries. Terrible for config: change one password and the entire ciphertext changes. Did one value change or all of them? The diff can't tell you.

SOPS encrypts at the VALUE level instead. Keys stay plaintext, values get encrypted individually:

CLOUDFLARE_TUNNEL_TOKEN=ENC[AES256_GCM,data:...]
FRIGATE_RTSP_PASSWORD=ENC[AES256_GCM,data:...]

What this buys you:

1. Diffs show exactly which key changed — and nothing else. Your Git history becomes an audit trail of secret rotations.

2. You see the structure — which secrets exist, when the file was last touched — without reading a single value.

3. A MAC covers all values. Flip one character in the file and decryption fails with an integrity error. Tampering doesn't go unnoticed.

4. A .sops.yaml per directory pins the public key, so "sops -e file.env" just works. No flags to remember.

And editing is one command: "sops secrets.env.enc" decrypts into your $EDITOR, waits, re-encrypts on save. No intermediate plaintext file ever touches disk.

Encryption you can't diff is encryption you'll eventually work around.

#sops #secrets #gitops #security #devops
