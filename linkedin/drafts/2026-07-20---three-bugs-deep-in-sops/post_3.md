---
angle: key lesson
post_number: 3
blog_post: 2026-07-20 - Three bugs deep in sops
generated: 2026-07-27T21:34:05.022792
---

The most humbling bug of my week was a default.
Not a line I wrote — a line I never turned off.

I had replaced a whole mechanism: SSH-host-key-derived age identities out, dedicated per-node age keys in. New keys generated, secrets re-encrypted, config pointing at the new keyFile.

Deploy. Same error as before.

Because sops-nix defaults age.sshKeyPaths to the system's SSH host keys — and setting age.keyFile does NOT clear that default.

At activation, the old broken derivation ran first, failed, and the process never reached the new key sitting right there on disk.

The fix was one line:

age.sshKeyPaths = lib.mkForce [ ];

Force the list empty, so the only identity sops-nix knows is the one I actually designed.

The lesson generalizes far beyond Nix:

When you swap mechanism A for mechanism B, the job is not "B works." The job is "A is provably out of the code path."

Defaults outlive the design that replaced them. You mentally deleted the old path — the system didn't.

Migrations, feature flags, fallback logic, layered config: same trap everywhere. Old behavior doesn't stop running because you stopped thinking about it.

#nixos #devops #sops #softwareengineering
