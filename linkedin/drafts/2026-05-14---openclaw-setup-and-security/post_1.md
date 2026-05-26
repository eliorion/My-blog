---
angle: hot take
post_number: 1
blog_post: 2026-05-14 - OpenClaw setup and security
generated: 2026-05-26T14:26:53.180993
---

Running a self-hosted AI agent with shell access?
A password on a public endpoint is one bug away from RCE.

Your blog being public makes sense — it serves static files.
Worst case is defacement.

Your AI agent is different.
It can read SSH keys, run shell commands, push to your repos.
That's not a web app. That's a foothold.

I see people protect these with:
- A reverse proxy + basic auth
- A strong password on a public port
- "It's unlikely anyone will find it"

None of this is defense in depth.
It's one misconfiguration away from disaster.

What I do instead:
Bind my OpenClaw gateway directly on the Tailscale interface.

The gateway listens only on my private tailnet IP.
Never on 0.0.0.0. Public interface has nothing to expose.

Network layer rejects attackers before gateway code even runs.
No zero-day in my gateway matters if nobody can reach the socket.

The principle is simple:
Don't expose what you don't need to expose.

My AI agent is for me, on my devices.
There's no reason to make it reachable from the internet.

#homelab #security #selfhosted #AI #tailscale
