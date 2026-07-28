---
angle: behind-the-scenes
post_number: 5
blog_post: 2026-07-22 - One script to run a fleet
generated: 2026-07-27T21:35:33.820277
---

The clearest sign my side project grew up wasn't a feature.
It was renaming six documentation files.

My backup fleet's design docs were numbered 09 through 14 — because they lived as an appendix inside another project's documentation. The prod cluster came first; the fleet was bolted onto its numbering.

Recently I renamed them 00 through 05, with a fresh 06 for the new buckets guide.

A tiny rename. An honest signal: the fleet stopped being an appendix of another project and became its own system, with its own doc zero.

The tooling grew up at the same time. The latest additions pull Garage-level configuration into the same declarative fold as the OS:

— S3 buckets and their access keys are declared in the repo; one command reconciles the running cluster against the declaration
— cluster layout — each node's zone and capacity — lives in the .nix host files, shown and applied in one step

No more hand-typed incantations on some node. The repo says what the cluster should look like; the script makes it so.

Behind the scenes, that's how homelab systems actually mature. Not a big rewrite. A rename, a new subcommand, one more piece of state pulled into the declaration.

Watch for the moment a project needs its own doc zero. That's when it deserves its own tooling, too.

#homelab #selfhosted #devops #nixos #documentation
