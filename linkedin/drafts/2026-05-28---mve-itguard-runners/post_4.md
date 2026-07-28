---
angle: behind-the-scenes
post_number: 4
blog_post: 2026-05-28 - mve-itguard-runners
generated: 2026-07-28T16:37:35.483149
---

Docker-out-of-Docker has a trap that produces zero error messages.
Just services that start with empty config directories.

The setup: my deploy runner is a container, but it talks to the host's Docker daemon. When it runs docker compose up, it's the daemon that creates the service containers — not the runner.

The trap: volume paths.

The runner passes ./config/homeassistant to the daemon. The daemon resolves that to an absolute path — on the HOST filesystem. It has no idea what the runner's internal filesystem looks like.

If the workspace lives at one path inside the runner and that path doesn't exist on the host, Docker happily bind-mounts a nonexistent directory. Services start. Config directories are empty. Nothing crashes where you're looking.

The fix is one rule: mount the workspace at the SAME absolute path on both sides.

/opt/mve-itguard-work inside the runner.
/opt/mve-itguard-work on the host.

Now every path the daemon resolves exists in both worlds, and bind mounts land where they should.

It's a small detail. It's also the single requirement that makes DooD deployments work at all.

#docker #devops #cicd #homelab
