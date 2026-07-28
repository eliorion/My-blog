---
angle: behind-the-scenes
post_number: 4
blog_post: 2026-06-29 - 124 fix commits
generated: 2026-07-27T20:07:09.960966
---

My Kubernetes cluster only accepts changes through Git.

Which means every single mistake I make is permanently on the record.

The cluster runs Flux — GitOps. Nothing reaches it except through a commit. That's the whole point: Git is the source of truth, the audit log, the rollback mechanism.

But there's a consequence I didn't appreciate when I started: the cluster becomes your test environment.

With no local validation step, the only way to know if a manifest works is:

edit YAML
commit
push
wait for Flux to reconcile
open k9s
read the error
repeat

On a bad day, that loop runs thirty times. And Git remembers all thirty.

The habits that finally killed the storms were boring ones:

- kustomize build locally before pushing, so syntax errors die on my machine instead of in the cluster
- YAML validation before it leaves the editor
- a staging environment, before production was even a concept in the repo

In my other projects those checks are enforced in CI now — precisely because I remember what it cost not to have them.

GitOps doesn't just make deployments declarative. It makes your learning curve public.

I'd still choose it every time.

#gitops #flux #kubernetes #devops #homelab
