---
angle: key lesson
post_number: 1
blog_post: 2026-06-30 - From Kustomize to Helm
generated: 2026-07-27T20:08:38.663833
---

I replaced my entire Kubernetes deploy layer in one commit.
It was safe because of everything I did before that commit.

The migration: Kustomize to Helm, for a scraping platform where workers are generated from a matrix of sites × proxies. Kustomize patches what exists. Helm generates from data. Wrong tool, right tool.

But the Helm part was the easy bit. What made it safe:

1. First, a refactor that looked pointless: reorganizing the Kustomize manifests to mirror the exact paths my GitOps repo consumes. Migrating a mess just moves the mess.

2. A hard definition of "done". Not "the chart deploys something that works" — my e2e tests and Grafana dashboards assert on specific resource names and labels. So the bar was: the chart renders the exact names and labels the old base did.

3. A render diff. Template the chart, diff against the old manifests. Either the YAML matches or it doesn't. A risky rewrite becomes a mechanical check.

When the diff came back clean, I deleted the old manifests in the same commit. No parallel maintenance period. No two sources of truth drifting apart.

The lesson generalizes far beyond Kubernetes:

When replacing a mechanism, don't rewrite. Translate, and prove the translation.

Equivalence first. Improvements after.

#kubernetes #helm #kustomize #gitops #devops
