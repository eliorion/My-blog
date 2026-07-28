---
angle: personal story
post_number: 1
blog_post: 2026-06-29 - 124 fix commits
generated: 2026-07-27T20:07:09.960391
---

124 of my 270 git commits start with 'fix'.

Almost half of everything I've ever pushed to my Kubernetes homelab exists to repair something the previous push broke.

The worst day: 29 commits. The runner-up: the very next day, with 21 more.

Some are genuinely embarrassing to read now:

'fix: intentation issue'
'fix: change to string' (twice, same day)
'fix: add the port 3006 on the pod' — a typo in the commit fixing a port.

It would be easy to squash all of this into a clean, professional-looking log.

I won't. Two reasons.

First, it's the most honest record I have of what learning Kubernetes actually looks like. Courses show you the happy path. The real path is 29 commits in one day because a label selector silently matched nothing.

Second, the history IS the curriculum. When I read 'fix: database deployment label match', I remember exactly how a Service with empty endpoints behaves — because I spent an evening inside that failure.

Three months later, my commits have scopes, real bodies, root causes, and links to documentation. Nobody told me to do that. It happened because I eventually needed my own history to debug my own cluster.

If your git log is embarrassing, good. It means you were learning in public — even if the only audience was future you.

#kubernetes #homelab #learninginpublic #gitops #devops
