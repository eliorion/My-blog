---
angle: key lesson
post_number: 3
blog_post: 2026-07-02 - A scraper that survives its own death
generated: 2026-07-27T21:22:52.308735
---

Kubernetes restarted my perfectly healthy pod every five minutes.
The pod wasn't broken. My liveness probe was lying.

The setup was textbook: the worker touches a heartbeat file, the probe checks the file's age. Simple.

Except one crawler loop never touched the file.

So the probe did exactly what it was told: about five minutes after every boot, it declared the worker dead and restarted it. Forever. The worker was healthy the whole time — the probe had no way to know.

Two lessons came out of the fix:

1. Put the heartbeat at the top of every loop iteration, in the same module the probe executes. If worker and probe share the same code path, they can never drift apart.

2. The heartbeat must also fire while the worker is PAUSED. A paused worker is alive, not stuck. A probe that can't tell the difference turns your pause button into a restart loop.

The principle I keep coming back to:

A liveness probe should measure "is the loop making progress" — not "did someone remember to update a file."

Restart stuck pods. Never busy ones. And never paused ones.

Your probes are only as honest as the code that feeds them.

#kubernetes #sre #devops #reliability #observability
