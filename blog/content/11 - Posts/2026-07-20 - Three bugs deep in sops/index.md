---
title: "Three Bugs Deep: The Week sops Refused to Decrypt"
date: 2026-07-20T09:00:00+02:00
draft: false
aliases: ["/11---posts/2026-07-20---three-bugs-deep-in-sops/"]
topics:
  - Homelab
  - Security
  - DevOps
tags:
  - sops
  - age
  - sops-nix
  - nixos
  - rosetta
  - apple-silicon
  - cryptography
  - debugging
  - homelab
projects:
  - garage-fleet
categories:
  - IT
  - Homelab
weight: 2
cover:
  image: cover.svg
  alt: sops decryption debugging saga
  caption: ""
  relative: true
  hidden: true
  hiddenInList: true
  hiddenInSingle: false
---

## One Error Message, Three Different Bugs

For most of a week, every deploy to node-A of my backup fleet ended the same way. `sops-install-secrets` printed:

```
0 successful groups required, got 0
```

…no secrets landed in `/run/secrets`, and `garage.service` crash-looped because its `rpc_secret_file` did not exist. The node was up, the tailnet worked, the disks were unlocked, and the secrets layer was dead.

I fixed it. It kept failing. I fixed it again. It kept failing. In the end there were **three separate bugs stacked on top of each other**, each one hidden behind the previous, all three producing that identical error line. This post walks through them in the order I hit them, because the order is the story: every fix was correct, and every fix revealed the next bug.

---

## Bug 1: The Identity That Almost Worked

The fleet's secrets are encrypted with sops to age recipients. Standard sops-nix practice derives each node's age identity from its SSH host key, using the bundled `ssh-to-age`. Elegant on paper: the host key already exists, already persists, and never leaves the machine.

Except decryption failed, in a maddeningly specific way. The derived identity's *recipient* matched what the file was encrypted to, but the *payload* decryption failed. sops found the right encrypted key block, tried it, and got garbage. Meanwhile, the standalone `ssh-to-age` binary plus the sops CLI decrypted the very same file with the very same host key just fine.

The decisive experiment: generate a **native** age key on the box with `age-keygen` and round-trip a file with it. Flawless. So the key material was fine, the box was fine, sops was fine: the *conversion path* inside sops-nix's activation was the culprit.

Rather than dig into why one ssh-to-age produced something another ssh-to-age disagreed with, I removed the conversion from the design entirely. Each node now has a **dedicated age key**:

- `private-keys/node-<x>-age.txt`: generated with `age-keygen`, gitignored
- `.sops.yaml` recipients replaced with the dedicated age publics for all four nodes, secrets re-encrypted with `sops updatekeys`
- `modules/sops.nix`: `age.keyFile = /var/lib/sops-nix/key.txt`, seeded at install time onto the TPM-encrypted root

Fewer moving parts, one identity per node, no derivation step. Deploy. Same error.

---

## Bug 2: The Default That Refused to Die

Here is the thing about replacing a mechanism: the old one has to actually *stop running*.

sops-nix defaults `age.sshKeyPaths` to the system's SSH host keys. Setting `age.keyFile` does not clear that default. So at activation, `sops-install-secrets` dutifully tried the SSH host keys **first**, derived the same stale ssh-to-age recipient from Bug 1, failed with `0 successful groups`, and never reached the dedicated key file sitting right there on disk.

The fix is one line, and it is a line worth remembering:

```nix
age.sshKeyPaths = lib.mkForce [ ];
```

Force the list empty, so the only identity sops-nix knows is the dedicated `keyFile`. Deploy. **Same error.**

At this point I had replaced the key, replaced the mechanism, and confirmed the config was doing exactly what I wrote. The recipient in `.sops.yaml` matched the key on the node byte for byte. And decryption still failed. Which meant something I trusted completely was lying to me.

---

## Bug 3: The Emulator in the Cryptography

Step back to where the secrets are *encrypted*: my operator devcontainer. It runs on an Apple-Silicon Mac, but the container image is **x86_64, emulated under Rosetta 2** (the CPU shows up as "VirtualApple").

Rosetta mis-translates the hand-written assembly implementation of **ChaCha20-Poly1305** in Go's crypto stack: the exact AEAD that sops/age use to encrypt the file payload. Every sops file encrypted in that devcontainer carried a **corrupt AEAD**: subtly wrong, but *self-consistently* wrong. The workstation could decrypt its own output perfectly (the same broken code inverted its own mistake) while the real x86 nodes, running correct code, saw only garbage. The corruption was invisible from the only place I was testing.

That explains the whole week. Bug 1's "recipient matches, payload fails" was this. The "stale" recipient in Bug 2 was tainted by this. Every re-encryption I did while "fixing" things re-poisoned the files.

Suspecting your own CPU emulation of breaking cryptography sounds like paranoia, so I made it a falsifiable experiment: run the **RFC 8439 known-answer test** (the test vectors from the ChaCha20-Poly1305 spec) against Go's implementation in both modes. Under Rosetta, the assembly path returns the **wrong tag**; built with `-tags=purego` (pure Go, no assembly), the tag is correct. On node-A's real x86 silicon, both are correct. X25519 and AES-GCM survive Rosetta fine: only the ChaCha20-Poly1305 assembly breaks.

Superstition became proof in about thirty lines of test harness.

The repair:

- Decrypt every secret with the self-consistent (broken) sops, re-encrypt with a **purego-built sops**, then verify on node-A that its own `sops-install-secrets` decrypts all five secrets
- `flake.nix`: a `withPurego` overlay, so the devShell and the packaged `sops`/`age` are purego builds
- `mise.toml`: drop the prebuilt sops/age binaries entirely: the Rosetta-corrupt path is no longer installable by accident

Deploy. Secrets in `/run/secrets`. `garage.service` up. Silence, of the good kind.

---

## What I Took Away

Three lessons, one per bug.

**Layered failures hide behind one symptom.** The error message never changed across three distinct root causes, and "I already fixed that error" is exactly how the second and third bug stay invisible. Each fix was real; none was sufficient. The only way through was treating every recurrence as a *new* investigation that happened to share a symptom.

**Defaults outlive the design that replaced them.** Bug 2 was not exotic. It was a default I had mentally deleted but never actually disabled. When swapping mechanism A for mechanism B, the job is not done until A is provably out of the code path, `mkForce`-empty if need be.

**When crypto fails "randomly", suspect the layer you trust most.** I questioned my keys, my YAML, my module wiring (everything at the top of the stack) while the actual fault sat in the CPU emulation layer beneath the language runtime. Cryptographic code is precisely where "it works on my machine" means the least, because AEADs are built to turn one flipped bit anywhere into total failure everywhere else. And the way out of paranoia is not more staring at configs: it is a known-answer test. Test vectors do not have opinions.
