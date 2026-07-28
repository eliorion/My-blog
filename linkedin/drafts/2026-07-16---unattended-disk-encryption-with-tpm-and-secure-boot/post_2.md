---
angle: technical deep-dive
post_number: 2
blog_post: 2026-07-16 - Unattended disk encryption with TPM and Secure Boot
generated: 2026-07-27T21:31:01.267132
---

My NixOS node decrypts its own root disk at boot — no human present.
Here's the chain that makes that safe instead of reckless.

The naive version of TPM auto-unlock is a trap: if the TPM hands out the key unconditionally, an attacker boots their own OS on your hardware and just asks for it.

So the LUKS keyslot is sealed against PCR 7 — the register that measures Secure Boot state. The TPM only unseals if the machine booted exactly the software I signed.

The full chain:

Firmware verifies my enrolled platform keys.
That validates a signed unified kernel image, built by lanzaboote on NixOS.
The signed initrd asks the TPM for the LUKS key.
TPM checks PCR 7, unseals, the encrypted volume opens.
The ZFS pool inside imports, root mounts, Tailscale comes up.

Tamper with any link — different bootloader, unsigned kernel, modified boot chain — and PCR 7 changes. The TPM refuses. The disk stays ciphertext.

The result: a machine that survives power cuts with no operator, but won't decrypt for anyone who boots around the OS or pulls the drive.

TPM auto-unlock without Secure Boot is a lock with the key under the doormat.

The two aren't separate features. They're one feature.

#nixos #secureboot #tpm #luks #encryption
