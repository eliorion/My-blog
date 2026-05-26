---
angle: key lesson
post_number: 4
blog_post: 2026-05-14 - OpenClaw setup and security
generated: 2026-05-26T14:26:53.188036
---

Most self-hosted security setups defend against the wrong threat.
They protect the app. They forget the network.

I built this the wrong way first.

My mental model: strong password + HTTPS = secure enough.
That works for a blog. Doesn't work for a process with shell access.

The wake-up was thinking through the failure modes:

Weak app auth? → attacker talks to your agent.
Gateway bug? → same.
Leaked token? → same.
Misconfigured nginx? → same.

All these failures exist because the endpoint is reachable in the first place.

The fix isn't better passwords.
It's making the endpoint unreachable to anyone not on your private network.

Now my OpenClaw agent is bound to my Tailscale interface only.

Attack surface from the public internet: zero.
Usability for me: unchanged.

The lesson I keep coming back to:
Network isolation is not a nice-to-have for powerful tools.
It's the baseline.

If your self-hosted agent can rm -rf, read SSH keys, or push to repos —
you need more than a password between it and the world.

#security #homelab #selfhosted #devops #AI
