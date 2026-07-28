---
angle: personal story
post_number: 1
blog_post: 2026-07-16 - Unattended disk encryption with TPM and Secure Boot
generated: 2026-07-27T21:31:01.266889
---

A server in a house has two different thieves.
Most encryption setups only defend against one of them.

The powered-off thief unplugs the box and carries it away. Full-disk encryption stops them cold — the disks are ciphertext without the keys.

The powered-on thief takes the machine while it's running. Or boots it and lets it decrypt itself. Against them, any encryption that unlocks automatically is worthless. The machine politely opens the door for whoever holds it.

Here's the twist: my backup node has to boot unattended. Power cuts happen, and I'm not driving to another city to type a passphrase every time the electricity blinks.

Unattended boot and defence against the powered-on thief are contradictory requirements.

Unless you split the disks into two trust domains:

1. The NVMe auto-unlocks via TPM in early boot. Root mounts, SSH comes up, the node rejoins my Tailscale mesh. No operator needed. Pull that disk out of the machine and it's ciphertext — the key lives in this board's TPM.

2. The data pool stays locked after every reboot. The TPM knows nothing about it. It waits, encrypted, until I unlock it remotely over the mesh.

Everything the node needs to be reachable unlocks itself.
Everything worth stealing waits for me.

Threat model first. The hardware design falls out of it.

#homelab #encryption #security #nixos #selfhosting
