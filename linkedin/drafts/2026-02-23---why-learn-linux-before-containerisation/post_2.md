---
angle: hot take
post_number: 2
blog_post: 2026-02-23 - Why learn linux before containerisation
generated: 2026-05-26T14:21:55.395803
---

Containers are not a tool you install.
They're Linux kernel features with a nice API on top.

Most people start with Docker before understanding what Docker actually does. I did too.

The CLI felt abstract and unintuitive at first. Commands worked but I didn't know why. When things broke, I had no mental model for where to look.

Then I started learning Linux seriously — processes, namespaces, cgroups, filesystems.

Everything clicked.

A container is:
- A process (or process tree)
- With namespace isolation (it can't see your other processes, networks, filesystems)
- With cgroup resource limits (CPU, memory, IO)
- With a layered filesystem

That's it. No magic.

Understanding this changed how I debug. Instead of googling error messages, I could reason about what was actually happening.

When my container died with no clear error, I knew to check memory limits — not re-read my script for the 10th time.

If you're learning DevOps or Platform Engineering, don't skip Linux to get to the "interesting" parts faster.

The interesting parts are built on Linux.

The foundation is the shortcut.

#linux #docker #devops #containers #platformengineering
