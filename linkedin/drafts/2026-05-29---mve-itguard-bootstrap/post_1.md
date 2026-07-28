---
angle: hot take
post_number: 1
blog_post: 2026-05-29 - mve-itguard-bootstrap
generated: 2026-07-27T20:03:40.273025
published: 2026-07-28T12:34:15.698191  # posted manually
---

The worst infrastructure isn't the one that breaks.
It's the server nobody fully understands anymore.

Things got installed over time. Config changed in place. The mental model lives in one person's head.

If that server dies, rebuilding it is archaeology.

I built my homelab around the opposite idea: a fresh Debian machine goes from zero to fully operational with one command.

sudo bash ~/ops/bootstrap ~/keys.txt

3 to 5 minutes later:
- Users created
- Docker installed
- CI runners registered
- Services ready to deploy

The trick isn't the script. It's the discipline behind it:

Every credential lives encrypted in the repository (SOPS + age).
Every config decision is code (Ansible, declarative state).
The only things a new server needs: the repo and one AGE key.

The server is not special anymore. If the hardware dies, a replacement is minutes away.

That's the property that matters for a home server. Not high availability. Not zero-downtime deploys.

Just the confidence that a dead disk is an inconvenience, not a crisis.

How long would it take you to rebuild your most important server from scratch?

#homelab #devops #infrastructureascode #selfhosted
