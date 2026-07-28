---
angle: personal story
post_number: 1
blog_post: 2026-07-22 - One script to run a fleet
generated: 2026-07-27T21:35:33.818374
---

One missing line in a YAML file almost left me with a wiped server I couldn't reach.
Here's the failure chain that taught me to script my paranoia.

My backup fleet runs NixOS. Provisioning a node means nixos-anywhere wipes the disk, installs, and seeds one age key — the node's only identity for decrypting its secrets.

Now imagine the secrets in the repo aren't encrypted to that key:

sops-nix fails at first boot.
No Tailscale authkey gets decrypted.
The node never joins the mesh.
And the ZFS unlock — only reachable over the mesh — becomes impossible.

Result: a freshly wiped box, offsite, that cannot be finished remotely.

None of these steps is hard. The sequence is the hazard. Generate the key, add the recipient, re-encrypt, commit, THEN install. Miss one, or reorder two, and an ordinary human mistake has disk-wiping consequences.

So I stopped trusting my checklist and scripted the paranoia. Before touching a disk, my install script now:

— reads the recipient out of the key file and greps .sops.yaml for it
— verifies the secrets file is actually encrypted, not a plaintext accident
— refuses to run if the secrets aren't committed (a flake only copies git-tracked files — an uncommitted secret simply doesn't exist)

Every check encodes a mistake I made, or could see myself making at 11pm.

The failure modes were never exotic bugs. Just ordering mistakes with expensive consequences.

#nixos #sops #homelab #devops #automation
