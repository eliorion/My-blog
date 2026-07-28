---
angle: personal story
post_number: 1
blog_post: 2026-07-02 - A scraper that survives its own death
generated: 2026-07-27T21:22:52.308261
---

My scraper workers kept dying. I spent weeks trying to stop it.
Then I realized I was solving the wrong problem.

A scraper worker is one of the most fragile things you can run. It drives a real browser that crashes, talks to sites that fight back, holds long-lived sessions, and eats memory unpredictably.

Early on, I chased every death one by one: driver crashes, database cold-starts, OOM kills.

That work mattered. But it taught me something bigger:

On Kubernetes, death is not the failure mode to eliminate. Pods WILL be OOM-killed, SIGKILLed, and watchdog-restarted no matter how careful your code is.

The real goal: make every death boring.

A dead worker should cost nothing. No lost work. No stuck queue. No late-night intervention.

So I rebuilt around that idea:

- Liveness probes that measure real progress, not stale files
- A Postgres queue that treats every claim as a lease, so a dead worker's URL returns to the pool on its own
- Rate-limit jails handled as weather, not damage

The platform stopped needing me the day the question changed from "why did this worker die?" to "did anything notice?"

The answer was no.

If you run anything on Kubernetes: stop trying to keep your pods alive. Make their deaths cheap instead.

#kubernetes #devops #sre #reliability #homelab
