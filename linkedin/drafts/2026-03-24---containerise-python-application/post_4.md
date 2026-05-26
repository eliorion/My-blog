---
angle: key lesson
post_number: 4
blog_post: 2026-03-24 - Containerise Python application
generated: 2026-05-26T14:25:07.686828
---

New developer joins the team. Up and coding in minutes, not days.
That's not magic — it's a devcontainer.

Here's how I set one up for a Python DevSecOps project:

The devcontainer runs from a custom Dockerfile:
→ Base: ubuntu-24.04 devcontainer image
→ Mise installed as binary and activated in bash + zsh

A postCreateCommand runs a setup script that:
→ Installs all tools from mise.toml (Python 3.13, uv, Trivy, pre-commit)
→ Sets up Commitizen for conventional commits
→ Installs pre-commit hooks including commit-msg validation

Docker-in-Docker is enabled — so you can build and run containers inside the devcontainer itself.

The result: any developer (or yourself on a new machine) gets the exact same environment. Python version, tooling, git hooks — all locked and reproducible.

I manage these with DevPod alongside my dotfiles. Works cleanly across projects.

Reproducible environments aren't a luxury. They're the baseline for serious DevOps work.

#devcontainer #devops #docker #developerexperience
