---
angle: hot take
post_number: 4
blog_post: 2026-07-20 - Three bugs deep in sops
generated: 2026-07-27T21:34:05.023233
---

"Works on my machine" is most dangerous in exactly one place: cryptography.
Because crypto is built to hide the difference until failure is total.

I spent a week debugging sops decryption failures. I questioned my keys. My YAML. My module wiring. Everything at the top of the stack.

The actual fault: CPU emulation. Rosetta 2 mis-translating ChaCha20-Poly1305 assembly beneath the Go runtime.

My machine encrypted files it could decrypt perfectly — the broken code inverted its own mistake. Every other machine saw garbage. The one place I was testing from was the one place the bug couldn't be seen.

An AEAD is designed so one flipped bit anywhere means total failure everywhere. That's the security property. It also means there is no "partially works" signal to debug from. It works, or it's noise.

So when crypto fails "randomly": suspect the layer you trust most. The runtime. The CPU. The emulator you forgot was even there.

And the way out of paranoia is not more staring at configs. It's a known-answer test — published test vectors, run against your actual binary, on your actual hardware.

Test vectors don't have opinions.

#cryptography #security #debugging #softwareengineering
