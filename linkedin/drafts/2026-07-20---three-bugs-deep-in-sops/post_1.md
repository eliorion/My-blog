---
angle: personal story
post_number: 1
blog_post: 2026-07-20 - Three bugs deep in sops
generated: 2026-07-27T21:34:05.021335
---

For a week, every deploy to one node failed with the exact same error:

"0 successful groups required, got 0"

I fixed it. It failed again. I fixed it again. Same line.

Turns out there were THREE separate bugs stacked on top of each other — each hidden behind the previous, all three producing that identical error.

Bug 1: sops-nix derived the node's age identity from its SSH host key. The conversion produced a key that almost worked — right recipient, garbage payload. I replaced it with dedicated age keys per node.

Same error.

Bug 2: sops-nix defaults to trying SSH host keys first. Setting a new keyFile doesn't clear that default. The old broken path ran before my fix ever got a chance. Fix: age.sshKeyPaths = lib.mkForce [ ];

Same error.

Bug 3: my devcontainer runs x86_64 emulated under Rosetta 2 on Apple Silicon. Rosetta mis-translates the ChaCha20-Poly1305 assembly in Go's crypto stack — the exact cipher sops uses. Every secret I encrypted was corrupt. And because the broken code inverted its own mistake, my machine decrypted everything perfectly. Only the real nodes saw garbage.

Every "fix" I made re-encrypted the secrets — and re-poisoned them.

The lesson that stuck: "I already fixed that error" is exactly how bugs two and three stay invisible. Treat every recurrence as a new investigation that happens to share a symptom.

#debugging #devops #nixos #homelab
