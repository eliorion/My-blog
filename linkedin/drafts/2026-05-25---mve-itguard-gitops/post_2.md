---
angle: technical deep-dive
post_number: 2
blog_post: 2026-05-25 - mve-itguard-gitops
generated: 2026-05-26T14:29:18.963154
---

One Compose file is a trap.
Here's the three-file pattern that solved my local/prod parity problem.

My Docker Compose setup splits into three files:

docker-compose.yaml       ← base: services, images, config mounts
docker-compose.prod.yaml  ← overlay: ports, data volumes, cloudflared
docker-compose.ci.yaml    ← overlay: alternate ports for CI

The base file defines what services *are*. Image versions, environment variables safe anywhere, config file mounts from the repo.

The production overlay adds what's environment-specific: exposed ports, persistent data paths on the host, secrets injected from env vars, and the Cloudflare tunnel that only runs in production.

The CI overlay mirrors prod but uses different port numbers — so validation jobs don't clash with services already running on the same machine.

The result:
→ Developers run `docker compose up` (base only) — no port conflicts, no touching prod data
→ CI validates with CI overlay — real validation, isolated namespace
→ Production deploys with prod overlay — explicit, separate project name via `-p mve-itguard-prod`

One config file means local dev bleeds into prod. Three files means each environment gets exactly what it needs.

Docker Compose supports this natively with `-f` overlays. Most people don't use it.

#docker #dockercompose #devops #homelab #selfhosted
