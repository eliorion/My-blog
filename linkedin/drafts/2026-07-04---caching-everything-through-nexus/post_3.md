---
angle: behind-the-scenes
post_number: 3
blog_post: 2026-07-04 - Caching everything through Nexus
generated: 2026-07-27T21:23:58.728056
---

"CI feels slow today" is not a bug report.
So I made the pipeline diagnose itself.

The setup: BuildKit layer caches live in an in-cluster registry. When that cache is down, builds fall back to GitHub's type=gha cache. And those fallback builds were mysteriously, dramatically slow.

Instead of tolerating the mystery, I added a probe that measures actual numbers.

The gha V2 cache backend is Azure Blob Storage. Measured from my ARC runner pods:
— Azure Blob: ~140 KB/s
— ghcr and PyPI from the same pods: ~3.6 MB/s

25x slower. The "cache" was moving at dial-up speed.

The probe script measures ghcr-versus-Azure throughput, records the BuildKit version (an older BuildKit silently uses a deprecated, throttled legacy cache endpoint), and prints it all as GitHub notices.

It's non-fatal and always exits 0. It exists purely so the next slow build explains itself in its own logs.

Turning "feels slow" into a number in the job output is cheap. And it ends the guessing forever.

If a fallback path matters to you, measure it before you need it.

#cicd #buildkit #githubactions #devops #performance
