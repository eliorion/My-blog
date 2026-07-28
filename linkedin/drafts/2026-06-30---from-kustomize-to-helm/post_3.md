---
angle: technical deep-dive
post_number: 3
blog_post: 2026-06-30 - From Kustomize to Helm
generated: 2026-07-27T20:08:38.664195
---

My Helm chart commits to its own repo.
Every release, CI rewrites the image tags in values.yaml and pushes.

Sounds cursed. It's actually the most useful thing to come out of my Kustomize-to-Helm migration.

The setup: values.yaml is the canonical state — what production actually runs. A bump-chart job in the build pipeline updates images.<service>.tag on every release and commits it back.

Three details keep it from exploding:

- A PAT, so the commit is attributable instead of anonymous CI noise.

- [skip ci] in the commit message, so the bump doesn't trigger a rebuild that bumps the chart that triggers a rebuild.

- A rebase-and-retry, so two concurrent releases don't clobber each other's push.

What it buys:

The chart is always deployable at HEAD. The Git log doubles as a release ledger — every tag bump is a commit: attributable, revertable, searchable.

And GitOps gets trivial. Flux points a HelmRelease at the chart inside the app repo. The app repo owns the chart; the GitOps repo just picks a version and supplies values.

Local dev lives in values-dev.yaml: local :dev images, pullPolicy: Never, and the tailscale proxy lanes scaled to zero — a laptop cluster has no tailnet egress.

A values file that's always true beats a wiki page that's sometimes true.

#gitops #helm #cicd #kubernetes #devops
