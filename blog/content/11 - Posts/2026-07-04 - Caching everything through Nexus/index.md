---
title: "When CI Cannot Pull: Caching Everything Through Nexus"
date: 2026-07-04T09:00:00+02:00
draft: false
topics:
  - Homelab
  - DevOps
  - CI/CD
tags:
  - nexus
  - ci-cd
  - docker
  - buildkit
  - trivy
  - supply-chain
  - github-actions
  - self-hosted
  - homelab
projects:
  - asp
categories:
  - IT
  - Homelab
weight: 2
cover:
  image: cover.svg
  alt: nexus mirror caching for CI
  caption: ""
  relative: true
  hidden: true
  hiddenInList: true
  hiddenInSingle: false
---

## The Day Docker Hub Said No

Self-hosted CI runners have one property nobody warns you about: every job on every runner leaves through the same IP address. Docker Hub does not see a small homelab politely building images — it sees one address hammering the registry, and it answers with `429 Too Many Requests`.

That is how the e2e pipeline started failing: not because of anything in the code, but because the image builds could no longer pull their base images. When you run CI on your own cluster, you own your supply chain — every upstream registry, package index, and vulnerability database becomes your problem.

The answer was to put an in-cluster **Nexus** mirror between CI and the internet, and then to keep widening what flows through it until nothing critical depended on an upstream being friendly. This post is that progression, including the two genuinely subtle bugs it surfaced along the way.

---

## Step One: Base Images Through the Mirror

The first fix was narrow: route the e2e image-build base pulls through the Nexus docker proxy. Base images are the highest-volume, most cacheable thing CI pulls — the same handful of tags, over and over, from every job. Once Nexus held them, the 429s stopped and the builds got faster as a side effect: pulls now travel across the cluster network instead of the internet.

---

## Step Two: The Probe That Always Said "Down"

The pipeline already had a Nexus pypi mirror — with a probe to check its health before using it, falling back to upstream PyPI if the mirror looked unreachable. Prudent design. Except the probe curled the bare `/simple` index root, and a Nexus pypi-proxy **404s that path by design**: it lazily proxies packages one at a time and never serves a browsable root.

So the probe reported "mirror unreachable" on every single run, and CI silently fell back to upstream PyPI even when the proxy was perfectly healthy. The mirror existed, cost resources, and served nothing. The fix probed a real package path — one Nexus resolves with a 200 — and the mirror finally started doing its job.

The same change widened the funnel to everything else CI downloads:

- **PyPI** — the uv Dockerfiles take an index ARG; the probe gates it, and an unhealthy mirror means uv quietly uses upstream.
- **npm** — same pattern with a registry ARG and its own probe.
- **Maven** — the Flyway images try the Nexus maven-proxy for the pgjdbc JAR, fall back to Maven Central, and verify the sha256 regardless of source.

The design rule everywhere: **zero hard dependencies on the mirror**. Every path is probe-gated or has an inline upstream fallback. A down mirror degrades to slow; it never degrades to broken.

---

## Step Three: Measure the Fallback Instead of Guessing

With Nexus healthy, BuildKit layer caches live in the in-cluster registry. When that cache is down, builds fall back to GitHub's `type=gha` cache — and those builds were mysteriously, dramatically slow.

Instead of tolerating the mystery, the pipeline gained a self-diagnosing probe. The gha V2 cache backend is Azure Blob Storage, and measured from the ARC runners it moved at roughly **140 KB/s**, while ghcr and PyPI moved at ~3.6 MB/s from the same pods. The probe script measures ghcr-versus-Azure throughput, records the BuildKit version (an older BuildKit silently uses the deprecated, throttled legacy cache endpoint), and prints it all as GitHub notices. It is non-fatal and always exits 0 — it exists purely so the *next* slow build explains itself in its own logs.

Turning "CI feels slow today" into a number in the job output is cheap, and it ends the guessing forever.

---

## Step Four: The Scanner's Own Downloads

The trivy security scanner turned out to have the same upstream problem as the builds. Scanning the Flyway image's JDBC driver requires trivy's Java vulnerability DB, and trivy's default repository list tries `mirror.gcr.io` **first** — a ~1.5 GB download from a registry that was not behind the Nexus mirror and failed intermittently. The main vulnerability DB never flaked, for exactly one reason: it was already routed through Nexus.

So the Java DB got the same treatment: Nexus ghcr-proxy first, ghcr.io as fallback, with the same health-filter shape — and never `mirror.gcr.io`. Consistency was the fix. If one artifact class bypasses the mirror, that class is where the flakes will live.

---

## The Cache That Lied About Security

The best bug of the batch had nothing to do with networking. The migration images run `apk upgrade --no-cache` to pick up Alpine security fixes at build time. But BuildKit keys a cached layer on the **RUN text plus the parent layer** — nothing else. Once that layer landed in the Nexus buildcache, it was reused unchanged on every build, and `apk upgrade` never actually ran again.

The result: `libexpat` sat frozen at 2.7.5-r0 while Alpine shipped 2.8.1-r0, and the trivy HIGH gate tripped on CVE-2026-45186 — in an image whose Dockerfile *looked* like it upgraded packages on every build. The caching that made CI fast had quietly disabled the step that kept images patched, and the flaky Java DB download had been masking the real failure on earlier attempts.

The fix is almost embarrassing: a dated `# security-refresh` comment inside the RUN instruction. Change the date, the layer key changes, the layer re-runs against current Alpine repos. The same latent bug existed in both the asp and fbref postgres images — found once, fixed twice.

---

## What I Took Away From It

Four commits, one theme: **a cache is a claim about the world, and claims go stale**. The pypi probe claimed the mirror was down when it was healthy. The gha fallback claimed to be a cache while moving at dial-up speed. The apk layer claimed to upgrade packages it had not touched in weeks.

The countermeasures are all the same shape — verify the claim: probe a real package path, measure the actual throughput, force the layer to re-run on a schedule you control. Owning the supply chain did not just mean hosting a mirror. It meant becoming the person who checks that the mirror, the fallback, and the cache are each telling the truth.
