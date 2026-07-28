---
angle: hot take
post_number: 3
blog_post: 2026-06-29 - 124 fix commits
generated: 2026-07-27T20:07:09.960819
---

Unpopular opinion: stop cleaning up your git history.

Your embarrassing commits are load-bearing.

My homelab repo has 124 commits with 'fix' in the subject line. Three of them are about YAML indentation. One says 'fix: change to string' — and then another one says it again, because ConfigMap values must be strings and I refused to believe it the first time.

The pressure to squash this into a clean log is real. A tidy history looks professional. It photographs well.

But a squashed history lies about how the work actually happened.

'fix: test without prob' — that's me disabling health probes to figure out whether the probe or the app was broken.

'fix: desactivate request ressource' — that's me removing resource requests to see if scheduling was the blocker.

Not elegant. But that's exactly how you isolate a variable when you don't yet know which layer is lying to you.

Courses sell the happy path. Clean histories sell the happy path. The actual path is debugging by elimination, in public, one commit at a time.

Keep the mess. It's the most honest documentation you'll ever write.

#git #kubernetes #learninginpublic #softwareengineering
