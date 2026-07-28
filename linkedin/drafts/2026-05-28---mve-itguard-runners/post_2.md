---
angle: tool spotlight
post_number: 2
blog_post: 2026-05-28 - mve-itguard-runners
generated: 2026-07-28T16:37:35.482864
---

My deploy pipeline has Docker access, but I never mounted the Docker socket into it.
There's a firewall between them.

Mounting /var/run/docker.sock into a CI container is the standard move. It's also equivalent to giving that container root on the host.

Instead, tecnativa/docker-socket-proxy sits between the runner and the daemon:

runner-deploy → socket-proxy → dockerd

The proxy is an allowlist for the Docker API. Mine permits exactly what docker compose needs to deploy: containers, images, networks, volumes, POST, info, ping.

Everything else is blocked at the proxy layer:
· exec into containers
· the build API
· Swarm endpoints
· system events
· registry auth

The proxy lives on an internal-only Docker network that exactly one container can reach. The raw socket is mounted into exactly one place: the proxy itself.

What this buys me: if someone gets code execution inside the deploy runner, they can issue compose commands. They cannot exec into a running service to steal secrets. They cannot read another container's environment. They cannot touch the rest of the API surface.

Docker access doesn't have to mean all of Docker.

#docker #security #cicd #devops
