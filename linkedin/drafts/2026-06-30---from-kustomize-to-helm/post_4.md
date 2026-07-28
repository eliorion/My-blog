---
angle: behind-the-scenes
post_number: 4
blog_post: 2026-06-30 - From Kustomize to Helm
generated: 2026-07-27T20:08:38.664325
---

The first commit of my Helm migration contained zero Helm.
It was a Kustomize refactor that looked completely pointless.

I reorganized k8s/manifests into base/asp and staging/asp — mirroring the exact relative paths my homelab GitOps repository uses. From the outside: shuffling folders.

The actual point: making the manifests verbatim copy-paste sources for the GitOps repo. The app repo declares what the services are. The homelab repo consumes them. Same paths, same structure, zero translation step.

The same refactor cleaned up two things hiding in the base:

- Dev-only Postgres instances moved out — they were never production's business.

- The old initdb migrations mount became a Flyway Job, with baselineOnMigrate keeping existing volumes safe. Verified on k3d: V1 through V5 applied against a fresh Postgres, schema and flyway_schema_history checked over psql.

Only then did the actual Helm work start.

Why bother? Because migrating a mess just moves the mess. If the old layout is tangled, your shiny new chart faithfully reproduces the tangle — except now it's hidden behind templates.

Clean the source. Prove it still works. Then translate.

The boring prep commit is the one doing the heavy lifting.

#kubernetes #gitops #devops #homelab
