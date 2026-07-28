---
angle: technical deep-dive
post_number: 2
blog_post: 2026-07-04 - Caching everything through Nexus
generated: 2026-07-27T21:23:58.727920
---

My CI had a health check that failed 100% of the time — on a perfectly healthy service.
For weeks, nobody noticed.

The setup was prudent: a Nexus PyPI mirror, with a probe checking its health before use. If the mirror looks down, fall back to upstream PyPI. Zero hard dependencies. Textbook.

One detail broke it all: the probe curled the bare /simple index root.

A Nexus pypi-proxy 404s that path by design. It lazily proxies packages one at a time and never serves a browsable root.

So the probe reported "mirror unreachable" on every single run. CI silently fell back to upstream PyPI. The mirror existed, cost resources, and served nothing.

The fix: probe a real package path — one Nexus actually resolves with a 200.

Then the same pattern went everywhere:
— PyPI: index ARG in the Dockerfiles, gated by the probe
— npm: registry ARG with its own probe
— Maven: try the Nexus proxy, fall back to Maven Central, verify sha256 either way

The design rule: a down mirror degrades to slow, never to broken.

The meta-lesson: a fallback that triggers silently is a fallback you can't trust. If your system can quietly route around failure, you need proof of which path it actually took.

#devops #cicd #nexus #python #observability
