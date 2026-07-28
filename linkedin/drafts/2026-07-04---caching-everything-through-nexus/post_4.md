---
angle: hot take
post_number: 4
blog_post: 2026-07-04 - Caching everything through Nexus
generated: 2026-07-27T21:23:58.728166
---

My Dockerfile ran apk upgrade on every build. My images stayed unpatched for weeks.
Both things were true at once.

Here's the trap: BuildKit keys a cached layer on the RUN text plus the parent layer. Nothing else.

My migration images run `apk upgrade --no-cache` to pick up Alpine security fixes at build time. But once that layer landed in the remote build cache, it was reused unchanged on every build. The upgrade never actually ran again.

The result: libexpat frozen at 2.7.5-r0 while Alpine shipped 2.8.1-r0. The trivy HIGH gate tripped on CVE-2026-45186 — in an image whose Dockerfile looked like it patched itself on every build.

The caching that made CI fast had quietly disabled the step that kept images secure. Worse: a flaky vulnerability-DB download had been masking the real failure on earlier attempts.

The fix is almost embarrassing:

A dated `# security-refresh` comment inside the RUN instruction. Change the date, the layer key changes, the layer re-runs against current Alpine repos.

Same latent bug existed in two images. Found once, fixed twice.

If your Dockerfile "updates packages" and you use a persistent build cache: check when that layer last actually executed. It might be older than you think.

#docker #security #buildkit #supplychain #devsecops
