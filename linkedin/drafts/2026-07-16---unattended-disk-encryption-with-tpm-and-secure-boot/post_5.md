---
angle: hot take
post_number: 5
blog_post: 2026-07-16 - Unattended disk encryption with TPM and Secure Boot
generated: 2026-07-27T21:31:01.267484
---

"Encrypt the disks" is not a security plan.
"Which thief, and what should they get?" is.

Full-disk encryption gets treated as a checkbox constantly. Encrypted? Good. Secure. Ship it.

But encryption that auto-unlocks defends against exactly one attacker: the one who steals a powered-off machine.

Steal it running? It's already unlocked.
Steal it and boot it? It unlocks itself for you.

For a server in a house — not a datacenter — the powered-on theft scenario is real. And the checkbox doesn't cover it.

My answer: stop pretending one unlock policy fits every byte.

The OS auto-unlocks via TPM, because a backup node must survive power cuts unattended. If someone steals it, they get... an operating system. Reproducible from a git repo anyway.

The actual data sits in a second encryption domain the TPM knows nothing about. After any reboot it stays ciphertext until I unlock it remotely over the mesh. Steal the machine mid-operation, reboot it, and the interesting disk is a brick.

One box. Two attackers. Two unlock policies.

If you can't name the attacker each layer of your encryption stops, you don't have a design.

You have a checkbox.

#security #encryption #threatmodeling #homelab
