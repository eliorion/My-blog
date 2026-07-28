---
angle: hot take
post_number: 2
blog_post: 2026-06-30 - From Kustomize to Helm
generated: 2026-07-27T20:08:38.664060
---

Helm didn't win because it's better than Kustomize.
It won because my YAML stopped being written and started being generated.

For a long time, Kustomize was the right call for my scraping platform. A base directory, overlays patching per environment, done. No templating language, no curly braces in my manifests.

Then the worker fleet changed shape.

Scraper lanes are now generated from a matrix: sites × proxies. Every new site or proxy means another Deployment with its own ConfigMap, egress rules, and image tag. Similar but not identical, times N.

Kustomize has no real templating. It patches what already exists. Generating N almost-identical Deployments meant duplicating manifests or fighting the tool.

Helm templates exist for exactly this. The whole fleet became a values list. The chart loops over it. New site? Add a list entry.

Here's the part people miss in the "Helm vs Kustomize" debate: I didn't drop Kustomize. It still deploys my dev-only infrastructure — Postgres, migration Jobs — the static stuff that never needed templating in the first place.

The debate framing is wrong. It's not versus.

Static manifests that need per-environment patches: Kustomize.
Resources generated from data: Helm.

Pick per problem, not per religion.

#kubernetes #helm #kustomize #devops
