---
angle: technical deep-dive
post_number: 2
blog_post: 2026-07-20 - Three bugs deep in sops
generated: 2026-07-27T21:34:05.022230
---

Rosetta 2 silently corrupted my cryptography.
And the corruption was invisible from the only place I was testing.

Setup: operator devcontainer on an Apple Silicon Mac, but the image is x86_64 — emulated under Rosetta 2.

Rosetta mis-translates the hand-written assembly implementation of ChaCha20-Poly1305 in Go's crypto stack. That's the exact AEAD sops and age use to encrypt file payloads.

Result: every sops file encrypted in that container carried a corrupt AEAD. Subtly wrong — but self-consistently wrong.

The broken code inverted its own mistake. My workstation decrypted its own output flawlessly. The real x86 nodes, running correct code, saw only garbage.

How do you prove something like that without sounding paranoid? A known-answer test. I ran the RFC 8439 test vectors against Go's implementation in every mode:

- Under Rosetta, assembly path: wrong tag
- Built with -tags=purego: correct tag
- On real x86 silicon: both correct

X25519 and AES-GCM survive Rosetta fine. Only the ChaCha20-Poly1305 assembly breaks.

Thirty lines of test harness turned superstition into proof.

The fix: purego builds of sops and age across the toolchain, prebuilt binaries dropped so the corrupt path can't come back by accident.

AEADs are designed to turn one flipped bit into total failure. That's a feature — until the bit flips beneath your language runtime.

#cryptography #golang #applesilicon #security #devops
