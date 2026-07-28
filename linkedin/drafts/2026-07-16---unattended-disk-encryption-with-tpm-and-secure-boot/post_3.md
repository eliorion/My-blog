---
angle: behind-the-scenes
post_number: 3
blog_post: 2026-07-16 - Unattended disk encryption with TPM and Secure Boot
generated: 2026-07-27T21:31:01.267258
---

I nearly bricked my server three times — before ever touching the hardware.
It was the best evening I've spent on this project.

Before installing, I ran the whole disk encryption plan through an adversarial review: assume this config is wrong. Find where it kills the machine.

It found three brick-class bugs. On paper, not on hardware.

1. Signing keys that don't exist yet.
Lanzaboote signs boot images with keys created AFTER install. Enable it at install time, and the build fails after the disks are already wiped. No bootloader, no old system to fall back to. Fix: a flag that keeps plain systemd-boot until the keys actually exist on the box.

2. ESP mathematics.
Signed kernel images bundling ZFS and TPM tooling are big, and NixOS keeps old generations around. Ten of them can fill a 1G boot partition and wedge every future deploy. Hence a 2G ESP — decided before the partition table was written, which is the only convenient time.

3. Two hands on one crypttab line.
Two modules both declared the TPM unlock token. A duplicate entry would have broken the early-boot unlock. Now exactly one module owns it.

None of these show up in a successful build. All of them show up at the worst possible moment: after the installer has destroyed the previous system.

Review the install path as hard as the configuration.
The ordering can brick what the code cannot.

#nixos #devops #homelab #infrastructure
