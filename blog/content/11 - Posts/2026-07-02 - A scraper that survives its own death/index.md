---
title: "A Scraper That Survives Its Own Death"
date: 2026-07-02T09:00:00+02:00
draft: false
aliases: ["/11---posts/2026-07-02---a-scraper-that-survives-its-own-death/"]
topics:
  - Homelab
  - DevOps
  - Kubernetes
tags:
  - kubernetes
  - scraping
  - postgres
  - reliability
  - self-healing
  - liveness
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
  alt: self-healing scraper patterns
  caption: ""
  relative: true
  hidden: true
  hiddenInList: true
  hiddenInSingle: false
---

## Workers Die. Design for It.

A scraper worker is one of the most fragile things you can run. It drives a real browser that crashes, talks to sites that actively fight back, holds long-lived sessions, and chews memory unpredictably. Early in the asp project I spent my time trying to make workers *not die* — fixing driver crashes, database cold-starts, and OOM kills one by one.

That work mattered, but it taught me the more important lesson: on Kubernetes, death is not the failure mode to eliminate. Pods will be OOM-killed, SIGKILLed, and watchdog-restarted no matter how careful the code is. The real goal is different: **make every death boring**. A dead worker should cost nothing — no lost work, no stuck queue, no operator intervention.

This post collects the patterns that got the platform there, each one traceable to a specific incident.

---

## Heartbeats That Tell the Truth

The first tool Kubernetes gives you is the liveness probe, and the first way to get it wrong is to make it lie.

The scraper workers use a heartbeat file: the worker touches it, the probe checks its age. Simple — except the crawler loop never touched it. The probe on the `url-crawler-autoscout24` lane did exactly what it was told and restart-looped the pod about five minutes after every boot. The worker was healthy; the probe had no way to know.

The fix put `beat()` at the top of every loop iteration, in the same `healthcheck` module the probe execs, so worker and probe can never drift apart. One subtlety made the fix complete: the heartbeat also fires **while the worker is paused**. A paused crawler is alive, not wedged — a probe that cannot tell the difference turns an operator's pause button into a restart loop.

The principle: a liveness probe should measure "is the loop making progress", not "did someone remember to update a file". Restart stuck pods, never busy ones.

---

## The Queue Assumes You Are Already Dead

The scraping queue lives in Postgres. A worker claims a URL, the row flips to `in_progress`, and when the work finishes the row is marked done.

And when the worker dies mid-URL — watchdog timeout, OOM, SIGKILL? The row stays `in_progress` forever. Nothing ever finished it, and `claim()` only looked at `pending` rows. The asp side has an orchestrator monitor that resets stale rows, but the fbref pipeline has no such monitor, and there every dead pod silently leaked a URL. The queue drained toward a pile of orphans.

The fix made the claim itself defensive: `claim()` now also re-claims `in_progress` rows whose lock is older than `STALE_LOCK_S` (900 seconds by default). No monitor, no cleanup job, no human. A URL can never be lost to a dead pod, because holding a claim is not a fact — it is a lease that expires.

This is my favorite pattern of the whole platform. The queue does not detect death; it just refuses to believe any worker stays alive longer than its lease.

---

## Getting Jailed Is Not a Crash

Sports Reference throttles clients at roughly 10 requests per minute; cross the line and the IP lands in a temporary 429 jail. The first version of the workers treated any block like a failure: burn an attempt on the URL, count it toward a failure streak, eventually restart the pod. Every part of that response was wrong for a jail.

The rework started by classifying blocks properly — a status-aware, unit-testable `detect_block` that distinguishes a **429 rate-limit jail** from a **Cloudflare challenge**, because they need opposite reactions. Then the pacing became adaptive:

- start around 6 requests/minute
- creep toward a ~9/minute floor after clean streaks
- snap back to double spacing on any block

The pacer state is per-worker and in-process, which is exactly right once proxy lanes exist: each pod paces its own egress IP, because that IP is what the site is throttling.

On a jail, the worker now releases the URL **without burning an attempt**, widens its pace, and sleeps a long `JAIL_COOLDOWN_S` — interruptible, so a SIGTERM during the cooldown still drains cleanly. Crucially, it does *not* restart the browser session: the IP is throttled, not the session. Tearing down a healthy session to fix an IP-level problem just adds load at the worst moment.

The old fixed think-time knobs disappeared entirely, replaced by the `PACE_*` configuration. The scraper goes as fast as it safely can, and slows itself down before the site has to.

---

## Sometimes the Fix Is Just More Memory

Not every incident deserves a clever mechanism. The leboncoin content-scraper kept getting OOM-killed, and the honest fix was raising its memory limit to 3Gi in the homelab values. The queue lease made those kills harmless in the meantime — the URLs came back, another worker picked them up — but harmless is not the same as free, and a pod that dies every few minutes wastes real throughput.

That is the healthy division of labor: limits sized for reality, and a system that shrugs when reality misbehaves anyway.

---

## What I Took Away From It

Every pattern here was born from a specific failure: a probe that killed healthy pods, URLs orphaned by a SIGKILL, an IP jailed by over-eager pacing, a pod too small for its workload. None of the fixes try to prevent death. They make death **cheap**: the heartbeat restarts only truly stuck workers, the lease returns a dead worker's URL to the pool in fifteen minutes, the jail handler treats throttling as weather rather than damage.

The platform stopped needing me the day the question changed from "why did this worker die?" to "did anything notice?" — and the answer was no.
