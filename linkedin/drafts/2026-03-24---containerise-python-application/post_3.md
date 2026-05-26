---
angle: technical deep-dive
post_number: 3
blog_post: 2026-03-24 - Containerise Python application
generated: 2026-05-26T14:25:07.684591
---

My first Python Docker image weighed 440MB.
One Dockerfile refactor changed everything.

The problem with a single-stage build: the final image keeps everything — build tools, package manager, cache. Your app only needs the binary to run.

Multi-stage builds solve this cleanly.

Stage 1 (builder): python:3.13-alpine + uv to install dependencies. Cache the dep layer separately so rebuilds are fast.

Stage 2 (final image): start fresh from python:3.13-alpine. Copy only the virtual environment from the builder. No uv, no build tools, no source code.

Two security bonuses:
→ Smaller image = smaller attack surface
→ Non-root user before CMD — one addgroup + adduser, then USER app

The result: an image that contains exactly what the app needs to run — nothing more.

Multi-stage builds feel like extra work the first time. But once the template exists, you just reuse it. The payoff in size, security, and build speed is consistent every time.

Start with python:latest. Then migrate. You'll see why immediately.

#docker #python #devsecops #containerization #devops
