---
angle: technical deep-dive
post_number: 2
blog_post: 2026-05-25 - mve-itguard-gitops
generated: 2026-07-27T19:10:18.019096
---

One docker-compose.yaml was quietly putting my production data at risk.
Now I use three.

docker-compose.yaml — the base. What the services ARE: images, safe environment variables, config mounts from the repo.

docker-compose.prod.yaml — the production overlay. Exposed ports, absolute paths for persistent data, secrets from environment variables, the Cloudflare tunnel container.

docker-compose.ci.yaml — the CI overlay. Same shape as prod, different ports, so validation never collides with production bindings on the same machine.

Why bother splitting?

Run docker compose up with just the base file and you get a working local stack. No port clashes with a running production deployment. No risk of accidentally touching production data volumes.

And one flag ties it together:

-p mve-itguard-prod

Naming the Compose project explicitly means the CI stack and the production stack live in completely separate namespaces — even on the same host.

Small pattern. It removed an entire class of "oops, that was prod" mistakes.

#docker #dockercompose #devops #homelab
