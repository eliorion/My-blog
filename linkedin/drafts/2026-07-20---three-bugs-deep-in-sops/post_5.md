---
angle: behind-the-scenes
post_number: 5
blog_post: 2026-07-20 - Three bugs deep in sops
generated: 2026-07-27T21:34:05.023677
---

How do you debug a failure with zero useful output?
You design experiments that can only fail one way.

Behind my week-long sops decryption saga were three small, boring experiments — and they did all the work:

Experiment 1: generate a native age key on the failing box, round-trip a file with it. Flawless. So the key material, the box, and sops itself were fine — the ssh-to-age conversion path was the suspect.

Experiment 2: after replacing that mechanism, same error. So I read the module's defaults instead of my own config. sops-nix was still trying SSH host keys first — my new key was never reached.

Experiment 3: the paranoid one. Suspecting Rosetta 2 of corrupting cryptography sounds unhinged, so I made it falsifiable: run the RFC 8439 ChaCha20-Poly1305 test vectors against Go's crypto under emulation. Wrong tag. Same test with a pure-Go build: correct. Same test on real x86: correct.

Emulator convicted by spec vectors, not vibes.

The pattern in all three: stop debugging the symptom and design experiments where each outcome eliminates a layer. "Works with a native key" clears the machine. "Wrong tag on known vectors" convicts the emulator.

The error message never changed once all week. The experiments are what moved.

#debugging #homelab #cryptography #devops
