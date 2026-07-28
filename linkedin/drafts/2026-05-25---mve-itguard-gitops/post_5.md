---
angle: tool spotlight
post_number: 5
blog_post: 2026-05-25 - mve-itguard-gitops
generated: 2026-07-27T19:10:18.019924
---

The most underrated GitHub Actions feature I use: workflow_run.
It turned my CI into a hard gate for production.

Most setups I see have deploy as just another job at the end of the pipeline.

Mine is a separate workflow entirely. It never runs on push:

on:
  workflow_run:
    workflows: ["CI"]
    types: [completed]
    branches: [main]

The deploy pipeline starts only when the CI workflow completes successfully on main. Lint, compose validation, the plaintext-secrets check — all of it becomes a gate you cannot accidentally skip with a config change.

Two extra wins:

workflow_dispatch on the same file gives me manual redeploys of the same commit — perfect for "just restart it" moments, no empty commit needed.

And the split maps cleanly onto runner isolation: CI runs on a locked-down runner with zero Docker access, deploy on a separate runner behind a Docker socket proxy.

One YAML trigger, and "nothing deploys unless CI passes" went from team discipline to physical impossibility.

If your deploy job lives in the same workflow as your tests: what happens when someone edits the needs: line?

#githubactions #cicd #devops #automation
