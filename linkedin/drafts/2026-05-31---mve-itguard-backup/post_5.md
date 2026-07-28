---
angle: behind-the-scenes
post_number: 5
blog_post: 2026-05-31 - mve-itguard-backup
generated: 2026-07-28T16:39:59.650175
---

The best parts of my backup system are the features I refused to build.
No replication. No failover. No dashboard. On purpose.

After designing a multi-node backup for my home infrastructure, the list of things I said no to matters as much as what I shipped:

No cross-node replication. The server pushes to each node independently. Nodes don't know each other exist. No mesh, no consensus protocol to debug.

No automated failover. A failed node gets logged and triggers a Home Assistant notification. I investigate manually. Automating rare events means maintaining code that almost never runs — and fails exactly when you need it.

No real-time backup. Daily at 3 AM. If the server dies at 2:59, I lose 24 hours of sensor history. Acceptable. Home automation doesn't need sub-daily recovery points.

No monitoring dashboard. Results go to the systemd journal and Home Assistant. The system the backup protects is also its alerting channel.

Why so stubborn?

Because backup systems fail at 3 AM, and 3 AM is when you'll be fixing them. Every component you add is a component you'll debug half-asleep while your data hangs in the balance.

Complexity is a cost you pay every day. Simplicity is a feature you appreciate exactly when things break.

The right question isn't 'what could this system do?' It's 'what can I still fix at 3 AM?'

#architecture #backup #homelab #devops #simplicity
