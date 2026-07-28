---
angle: personal story
post_number: 5
blog_post: 2026-05-30 - mve-itguard-key-rotation
generated: 2026-07-28T16:38:46.773398
---

I broke my own deployment by rotating an encryption key wrong.
Then I made sure it could never happen again.

The setup: one AGE key encrypting nine SOPS files across four directories, plus a copy on the production server, plus a GitHub Actions secret. Three places that all have to agree.

Manual rotation meant a checklist: new key, four .sops.yaml updates, updatekeys on every file, server update, secret update. Get the order wrong — say, update the server but not CI — and the next deploy fails with a decryption error that tells you nothing about WHICH key is stale WHERE.

The fix wasn't more discipline. It was removing myself from the process.

Now a CI job compares key material between the server and the GitHub secret on every push to main. A mismatch means I intentionally started a rotation, so the pipeline finishes it: re-encrypts every file with the new key, updates the server, commits back, deploys.

My part shrank to: generate a key, update two places, push.

The insight that stuck with me: if a security task needs a checklist to be done safely, it will eventually be done unsafely.

Checklists are where mistakes hide. Pipelines are where they die.

#security #devops #automation #cicd #homelab
