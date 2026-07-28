---
angle: technical deep-dive
post_number: 2
blog_post: 2026-05-29 - mve-itguard-bootstrap
generated: 2026-07-27T20:03:40.273323
published: 2026-07-28T12:34:15.698191  # posted manually
---

How do you clone a private repo on a brand-new server
without copying credentials to it first?

It's the chicken-and-egg problem every bootstrap script hits: the setup code lives in a private repository, but the fresh server has no way to authenticate.

The common answers all have downsides:
- Deploy keys: one more secret to manage and copy around
- Personal access tokens: tied to a human, broad scope
- Copying your own SSH key over: please don't

My solution: a GitHub App + SOPS.

The App's private key sits inside the repo itself, encrypted with age. The bootstrap script only needs one AGE key to unlock everything else.

The flow:
1. Decrypt the App key with sops, in memory, never written to disk
2. Sign a JWT with it
3. Exchange the JWT for an installation token (scoped to repo access, expires in 1 hour)
4. Clone with that token
5. Token is never stored anywhere

So provisioning a new server means copying exactly two things: the ops/ directory and one AGE key file.

Everything else — runner credentials, app secrets, infrastructure passwords — is already in the repo, encrypted.

One key unlocks the whole system. One command provisions it.

The repository becomes the complete operational record. No archaeology required.

#devops #github #sops #automation #infrastructureascode
