---
angle: key lesson
post_number: 3
blog_post: 2026-05-31 - mve-itguard-backup
generated: 2026-07-28T16:39:59.649924
---

docker pause is the most underrated command in my backup script.
Not stop. Not restart. Pause.

Here's the problem it solves.

Home Assistant runs on SQLite. A live SQLite process writes to a WAL file and periodically checkpoints into the main database. Copy that file mid-checkpoint and you get a backup that's internally inconsistent — a mix of old and new state.

You won't notice at backup time. You'll notice at restore time. Which is the worst possible moment.

The obvious fix — stopping the container — means downtime, reconnections, missed automations.

docker pause does something better: it sends SIGSTOP to every process in the container. Everything freezes in place, mid-execution. Files sit in a consistent state on disk. Restic reads them while nothing moves.

Then docker unpause sends SIGCONT and execution resumes exactly where it stopped. No restart. No reconnection. No lost state.

Total freeze in my setup: 20 to 40 seconds, once a night at 3 AM. Nobody notices.

The lesson generalizes: a backup that runs isn't the goal. A backup that restores is. Every shortcut you take at backup time is a debt you pay at restore time, with interest.

#docker #sqlite #homeassistant #backup #devops
