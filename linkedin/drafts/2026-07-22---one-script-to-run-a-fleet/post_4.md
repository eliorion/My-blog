---
angle: hot take
post_number: 4
blog_post: 2026-07-22 - One script to run a fleet
generated: 2026-07-27T21:35:33.819886
---

The most valuable file in my infrastructure repo is a bash script with a case statement.
Not the Nix. Not the CI. The bash.

Hot take: for a small fleet, you don't need a platform. You don't need Kubernetes, an orchestrator, or a golden-path portal. You need one entrypoint where your lessons accumulate.

Mine is called 'fleet'. It wraps nixos-anywhere, deploy-rs, sops, ZFS unlocks, and Garage cluster operations behind a dozen subcommands. Run it with no arguments and it prints live fleet status above a numbered menu, for the days I don't remember the exact verb.

None of it is clever engineering. The value isn't in the code — it's in WHERE the dangerous logic lives:

— the check that refuses to wipe a disk until the new node can provably decrypt its own secrets
— the warning that a first deploy has no rollback baseline
— the ZFS passphrase that travels only on ssh stdin — never argv, never an env var, never visible in any process table
— the detached switch that survives restarting the VPN it's deployed over

Boring tech plus guardrails beats clever tech plus a runbook.

Your infrastructure doesn't need to be impressive. It needs to be un-brickable at 11pm.

#bash #devops #homelab #infrastructureascode
