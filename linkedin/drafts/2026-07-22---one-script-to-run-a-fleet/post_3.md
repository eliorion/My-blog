---
angle: key lesson
post_number: 3
blog_post: 2026-07-22 - One script to run a fleet
generated: 2026-07-27T21:35:33.819434
---

An ops tool earns its keep the day the dangerous paths become the scripted paths.
Not the fast ones. The dangerous ones.

Provisioning a node in my backup fleet used to involve two scripts, a README section, and a mental checklist: generate the age key, add its recipient, re-encrypt the secrets, commit, run the installer, seed the key, unlock the pools, join the cluster layout.

Each step easy. The sequence was the hazard.

Forget to re-encrypt before installing? The freshly wiped node can't decrypt its own secrets. Deploy before committing? The flake silently builds without your changes.

So it all collapsed into one tool: a single 'fleet' script with a subcommand per lifecycle operation. new, install, deploy, rollback, unlock, status.

Nothing stops me from running nixos-anywhere or sops by hand. But the moment the scripted route became the EASIEST route, the guardrails started actually running: the pre-wipe recipient check, the first-deploy warning, the passphrase that only ever travels on stdin.

One entrypoint means one place to encode every lesson. Each near-miss in this project turned into a die or a warn in one bash file.

The script isn't automation for speed. It's memory — the fleet's accumulated scar tissue, executable.

#devops #automation #bash #homelab
