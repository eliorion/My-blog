---
angle: technical deep-dive
post_number: 2
blog_post: 2026-07-12 - Deploy failures to Telegram
generated: 2026-07-27T21:28:10.349397
---

One alert at 3 AM is easy to sleep through.
So my cluster sends two kinds.

Here's the weakness of event-based notifications: an event is a moment. Flux's notification-controller fires when a HelmRelease fails — but if that message arrives while I'm asleep, I scroll past it, and Flux won't re-send. From its perspective, nothing new happened.

So I run two independent alert paths to the same Telegram chat.

Path 1 — event-driven:
Flux notification-controller. A Provider pointing at the Telegram bot API, an Alert subscribed to HelmRelease events. Tells me the moment something breaks, with the error reason attached.

Path 2 — condition-driven:
A PodMonitor scrapes the flux-system controllers into Prometheus. A PrometheusRule fires whenever gotk_reconcile_condition reports Ready=False. Alertmanager routes it to Telegram — and keeps re-notifying on its schedule.

The difference is subtle but crucial: as long as the resource *stays* broken, path 2 stays firing.

One path tells me something broke.
The other refuses to let me forget it's still broken.

Between them, "silently broken" is no longer a state my cluster can be in.

#kubernetes #prometheus #alertmanager #flux #monitoring
