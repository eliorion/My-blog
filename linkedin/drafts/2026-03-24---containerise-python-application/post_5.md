---
angle: behind the scenes
post_number: 5
blog_post: 2026-03-24 - Containerise Python application
generated: 2026-05-26T14:25:07.687454
---

Most tutorials show you how to containerize an app.
Few show what happens between 'it works locally' and 'safe to ship'.

Here's the full loop I built while learning DevSecOps:

1. Code in a devcontainer — reproducible environment, Docker-in-Docker, all tools pre-installed via Mise

2. Commit with standards — Commitizen enforces Conventional Commits via a git hook. No more "fix stuff" in the history.

3. Build the container — multi-stage Dockerfile: builder stage with uv for deps, final stage with only the venv and a non-root user

4. Scan before shipping — Trivy on the final image. CRITICAL and HIGH CVEs must be addressed before this image goes anywhere.

5. Iterate on the base image — python:latest → slim → alpine. Each step cuts size and reduces attack surface.

This is the shift from "Dev" to "DevSec": security becomes a gate in your local workflow, not a surprise in production.

None of this is complicated once it's wired up. The hard part is building the habit.

#devsecops #devops #docker #python #security
