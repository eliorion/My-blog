---
angle: key lesson
post_number: 3
blog_post: 2026-05-29 - mve-itguard-bootstrap
generated: 2026-07-27T20:03:40.273531
---

The best decision in my server bootstrap wasn't technical.
It was splitting the work into two phases.

Phase 1 — repository setup. Done once, on my dev machine:
- Generate the AGE encryption key
- Create the GitHub App
- Encrypt every credential into the repo

Phase 2 — server bootstrap. Runs on every new machine:
- Copy two files
- Run one command
- Wait 3 to 5 minutes

Why the split matters:

Phase 1 outputs are durable. The encrypted repo becomes the single source of truth for the whole system.

Phase 2 is repeatable. OS reinstall? Second machine? Disaster recovery? Same two steps, same result, every time.

And it's idempotent by design. Package installs are guarded, Ansible uses declarative state, persistent data is never touched. Re-running bootstrap on a live server changes nothing that's already correct. Home Assistant history, camera recordings — untouched.

Most setup scripts fail because they mix these phases. They generate keys during provisioning, mutate state that should be fixed, and produce a slightly different server each run.

Separate what you decide once from what you repeat often.

That's the whole lesson.

#devops #ansible #infrastructureascode #homelab
