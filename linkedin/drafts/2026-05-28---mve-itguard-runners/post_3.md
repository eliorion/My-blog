---
angle: key lesson
post_number: 3
blog_post: 2026-05-28 - mve-itguard-runners
generated: 2026-07-28T16:37:35.483025
---

All three of my CI runners are built from the same Docker image.
One of them can deploy to production. One can't even reach Docker.

The difference isn't what's installed — it's what each container is allowed to touch.

runner-ci handles pull requests. Lint and validation, nothing else. No Docker socket, no proxy, no volumes, no-new-privileges set. Untrusted PR code executes here and finds an empty room.

runner-deploy brings services up. It runs as a non-root service account and talks to Docker through a filtering proxy that exposes a fraction of the API.

runner-rotate re-encrypts secrets. It runs as root — because /etc/sops/age/keys.txt is root-owned with mode 600 and there's no honest way around that. But that's its only mount, and it has no Docker access at all.

Here's the detail I like most: the docker CLI is installed in all three runners, including the CI one. Doesn't matter. Without a socket or a DOCKER_HOST pointing somewhere, the CLI is inert.

Capabilities don't come from what's on disk.
They come from what the configuration grants.

Least privilege isn't uninstalling tools. It's making sure the tools have nowhere to go.

#security #leastprivilege #cicd #docker #devops
