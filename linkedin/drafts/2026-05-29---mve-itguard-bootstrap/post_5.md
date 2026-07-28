---
angle: behind-the-scenes
post_number: 5
blog_post: 2026-05-29 - mve-itguard-bootstrap
generated: 2026-07-27T20:03:40.273893
---

My deploy pipeline runs with zero sudo access.
On purpose. Here's the user model behind it.

When my bootstrap script provisions a server, Ansible creates exactly two users:

sysadmin (UID 1000)
- SSH entry point for humans
- Full passwordless sudo for maintenance
- Key-based login

mve-itguard (UID 1001)
- Service account, no sudo at all
- Member of the docker group
- Owns the app files and the runner workspace

The deploy runner — the thing that touches the server on every push — runs as the service account.

If that runner is ever compromised, the blast radius stops at UID 1001. It can mess with the app. It cannot escalate to root.

A few other details from the same playbook:

- Root SSH login disabled via a drop-in config file
- Runner workspace at a fixed path, owned by UID 1001, required for Docker-outside-of-Docker path matching
- Daily backups on a systemd timer: 03:00 with random jitter

None of this is enterprise-grade security theater. It's a homelab.

But least privilege costs almost nothing when you define it in Ansible from day one. Retrofitting it later costs a weekend.

Small design decisions, made early, compound.

#security #leastprivilege #homelab #devops #ansible
