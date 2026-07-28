---
angle: technical deep-dive
post_number: 2
blog_post: 2026-07-02 - A scraper that survives its own death
generated: 2026-07-27T21:22:52.308546
---

My favorite piece of code in my scraping platform doesn't detect failures.
It just refuses to believe any worker is still alive.

The setup: my scraping queue lives in Postgres. A worker claims a URL, the row flips to in_progress, and when the work finishes, the row is marked done.

The problem: what happens when the worker dies mid-URL? OOM kill, watchdog timeout, SIGKILL.

The row stays in_progress forever. Nothing ever finishes it, and claim() only looked at pending rows.

Every dead pod silently leaked a URL. The queue drained toward a pile of orphans.

My first instinct was a monitor: a cleanup job that detects dead workers and resets their rows. I even built one for part of the platform.

But the better fix needed no monitor at all.

I made the claim itself defensive: claim() now also re-claims in_progress rows whose lock is older than 15 minutes.

No cleanup job. No health checks. No human.

A URL can never be lost to a dead pod, because holding a claim is not a fact — it's a lease that expires.

The queue doesn't detect death. It just assumes every worker is already dead and demands ongoing proof otherwise.

That inversion — from "detect failure" to "expire trust" — is the most reliable pattern I've shipped. It works precisely because it has no moving parts that can themselves fail.

#postgres #distributedsystems #kubernetes #webscraping #softwareengineering
