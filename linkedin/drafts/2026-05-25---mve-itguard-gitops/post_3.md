---
angle: key lesson
post_number: 3
blog_post: 2026-05-25 - mve-itguard-gitops
generated: 2026-05-26T14:29:18.964974
---

My deploy pipeline doesn't trigger on git push.
It triggers when CI completes successfully. That difference matters.

In a single pipeline where deploy is a downstream job, one wrong `if:` condition and you're deploying unvalidated code. It's happened to me before.

With GitHub's `workflow_run` event, the pipelines are physically separate:

on:
  workflow_run:
    workflows: ["CI"]
    types: [completed]
    branches: [main]

CI must complete and pass. Only then does deploy start. No exceptions.

The CI pipeline runs two jobs:
1. Lint — yamllint, shellcheck, ansible-lint, no plaintext .env check
2. Validate — `docker compose config` with the CI overlay

The deploy pipeline runs two jobs:
1. Rotate — AGE encryption key rotation if needed
2. Deploy — decrypt secrets, pull images, `docker compose up`

Neither pipeline knows about the other's internals. The deploy pipeline doesn't understand what CI checked. It just knows CI passed.

There's also a `workflow_dispatch` trigger for manual redeploys — useful when a service needs restarting without a new commit.

Decoupling pipelines is one of those things that feels like overhead until the day it stops a bad deploy.

#githubactions #cicd #devops #gitops #automation
