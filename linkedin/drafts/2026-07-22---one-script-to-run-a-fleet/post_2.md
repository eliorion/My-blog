---
angle: technical deep-dive
post_number: 2
blog_post: 2026-07-22 - One script to run a fleet
generated: 2026-07-27T21:35:33.819011
---

My deploy tool's auto-rollback — the safety feature — is what bricked the node.
Here's why, and the systemd trick that fixed it.

deploy-rs has 'magic rollback': if a deploy breaks reachability, the node auto-reverts in about 30 seconds. Brilliant for 95% of changes.

The other 5%: changes to Tailscale itself.

A normal deploy rides an SSH session over the tailnet. So when the deploy restarts tailscaled mid-switch:

1. The SSH session drops.
2. The activation dies half-done.
3. Rollback kicks in.
4. Rolling back a version bump downgrades tailscaled onto a state file written by the newer version — which the old version can't parse.

Node off the mesh. Garage can't bind its RPC listener. The rollback did the bricking.

The fix: a --detached deploy mode.

Build the closure locally. nix copy it to the node over the tailnet. Then launch switch-to-configuration as a transient systemd unit owned by PID 1, via systemd-run.

The command returns immediately. When the switch restarts tailscaled and SSH drops, the switch keeps running to completion under systemd. The node only ever moves forward — so a version bump self-heals instead of half-reverting.

The lesson that stuck: know exactly which failure your safety net was built for. Outside that envelope, the net itself can be the hazard.

#nixos #tailscale #devops #sre #deployment
