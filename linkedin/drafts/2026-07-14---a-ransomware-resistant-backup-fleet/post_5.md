---
angle: key lesson
post_number: 5
blog_post: 2026-07-14 - A ransomware-resistant backup fleet
generated: 2026-07-27T21:29:46.144163
---

The most important decision in my backup architecture isn't a technology.
It's a boundary.

My backup fleet is a separate trust domain from production. Not a second Kubernetes cluster. Not more nodes in the same mesh. A different world:

- Different OS (NixOS, while prod runs Talos)
- Different identities and SSH access
- Different secrets, encrypted for different keys
- Different control plane

The production cluster holds S3 credentials that let it write backups. That's all they do. They can't administer the fleet, can't SSH into its nodes, can't touch its configuration.

Full prod compromise buys an attacker the ability to upload garbage — not the ability to destroy history.

And the boundary cuts both ways: a leaked secret in one domain unlocks nothing in the other.

The tempting path was to reuse what I had. Join the backup nodes to the existing cluster, manage everything from one place, one set of tools. Convenient — and it would have quietly merged the two trust domains, making my backups deletable by the exact system they're supposed to survive.

Sometimes good architecture is refusing to connect things.

Before adding anything to your infrastructure, ask: what can reach it, and with which credentials? The answer decides whether you're building disaster recovery or an expensive convenience copy.

#security #architecture #disasterrecovery #devops
