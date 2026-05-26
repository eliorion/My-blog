---
angle: hot take
post_number: 1
blog_post: 2026-05-24 - mve-itguard
generated: 2026-05-26T14:28:03.157377
---

Your Ring camera footage isn't yours.
It lives on Amazon's servers, behind a subscription, until they decide it doesn't.

I'm not saying that to scare you.
I'm saying it because I made a different choice — and I want to explain why.

When I started building a home security system, I looked at Ring, Nest, all the usual options.

Then I thought about what I was actually buying:
→ Monthly subscription to access my own footage
→ Data on someone else's infrastructure
→ A system that stops working if the company changes pricing or shuts down

That's not ownership. That's renting access to your own security.

So I built mve-itguard instead.

It runs on a single Debian server in my home.
Cameras stream via RTSP — locally, always.
AI detection runs on-device using Frigate.
Notifications flow through Home Assistant.
Remote access works through a Cloudflare Tunnel — no open ports, no exposed IP.

The footage never leaves my server.
The system requires no subscription.
If I stop paying Cloudflare (free tier), I lose remote access — but the local system keeps running.

That's the difference between owning a system and licensing one.

I'm writing a full series on how this was built — GitOps, secrets management, CI runners, backups.

First post is live. Link in comments.

#selfhosted #homelab #privacy #homeautomation
