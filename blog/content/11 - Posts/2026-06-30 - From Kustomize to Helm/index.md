---
title: "From Kustomize to Helm: Migrating the Deploy Layer"
date: 2026-06-30T09:00:00+02:00
draft: false
aliases: ["/11---posts/2026-06-30---from-kustomize-to-helm/"]
topics:
  - Homelab
  - DevOps
  - Kubernetes
tags:
  - kubernetes
  - helm
  - kustomize
  - gitops
  - ci-cd
  - self-hosted
  - homelab
projects:
  - asp
categories:
  - IT
  - Homelab
weight: 2
cover:
  image: cover.svg
  alt: kustomize to helm migration
  caption: ""
  relative: true
  hidden: true
  hiddenInList: true
  hiddenInSingle: false
---

## Why Touch a Deploy Layer That Works

The asp platform started its Kubernetes life on Kustomize. A `base/` directory held the manifests, overlays patched them per environment, and everything deployed fine. Kustomize is a good tool, and for a while it was the right one.

Then the scraper fleet stopped being a fixed set of Deployments. Lanes are generated from a matrix of *sites × proxies* — every new site or proxy adds another worker with its own ConfigMap, its own egress rules, its own image tag. Kustomize has no real templating; it patches what already exists. Generating N similar-but-not-identical Deployments meant either duplicating manifests or fighting the tool. Helm templates are built for exactly this: the whole fleet becomes a values list, and the chart loops over it.

So the deploy layer had to move. This post is the story of that single migration — and of the rule that made it safe: **prove equivalence before changing anything else**.

---

## Step One: Restructure Before Migrating

The migration did not start with Helm. It started with a Kustomize refactor that looked pointless from the outside: reorganizing `k8s/manifests` into `base/asp` and `staging/asp`, mirroring the exact relative paths the homelab GitOps repository uses.

The point was to make the manifests **verbatim copy-paste sources** for the homelab repo. Same paths, same structure — the app repo declares what the services are, the homelab repo consumes it. The base held the per-site scraper lanes, the orchestrator, the analyzer, and the frontend, with every DB consumer reading the same CNPG-style `asp-db-app` Secret. The staging overlay added the ghcr image pins, the SOPS-encrypted orchestrator secret, and a blanket image-pull-secret patch.

The same refactor moved the dev-only Postgres instances out of the base and replaced the old initdb migrations mount with a Flyway Job — `baselineOnMigrate` keeping existing volumes safe. Verified on k3d: the Flyway Job applied V1 through V5 against a fresh Postgres, schema and `flyway_schema_history` confirmed over psql.

Only once the layout was clean and proven did the actual migration begin. Migrating a mess just moves the mess.

---

## Step Two: The Chart, Proven by Render Diff

The next day, the app deploy moved to a single Helm chart at `k8s/charts/asp`.

The critical decision was what "done" meant. Not "the chart deploys something that works" — that bar is too low, because the e2e suite and the Grafana dashboards assert on specific resource names and `app`/`component`/`site` labels. If the chart renders different names, everything downstream breaks silently.

So the bar was: **the chart templates render the exact names and labels the old Kustomize base did**, verified by diffing the rendered output against the old manifests. A render diff turns a risky rewrite into a mechanical check. Either the YAML matches or it does not. When it matched, the old `base/asp` and staging overlay were deleted in the same commit — no parallel maintenance period, no drift between two sources of truth.

Kustomize did not disappear entirely. It keeps the job it is still best at: the dev-only infrastructure (Postgres, fbref-postgres, the Flyway Job) that never needed templating in the first place.

---

## The Values Split

The chart's configuration follows the same base/overlay thinking, expressed as values files:

- **`values.yaml`** — the canonical state: CI-bumped image tags plus staging defaults. This file is what production actually runs.
- **`values-dev.yaml`** — the k3d overrides: local `:dev` images, `pullPolicy: Never`, and the tailscale proxy lanes scaled to zero, because a laptop cluster has no tailnet egress.

The interesting part is who writes `values.yaml`. On every release, a new `bump-chart` job in the build pipeline rewrites `images.<svc>.tag` in the chart and commits it back — with a PAT so the commit is attributable, `[skip ci]` so it does not trigger a rebuild loop, and a rebase-retry so concurrent releases do not clobber each other. The chart is always deployable at HEAD, and the Git log doubles as a release ledger.

---

## CI Around the Chart

Two pipeline changes closed the loop.

First, the `scan-k8s` job gained `helm lint` plus a template smoke test that renders the chart with both the default and dev values. A chart that cannot render never reaches a cluster.

Second, the e2e suite became a **two-phase deploy** that mirrors real life:

```bash
# phase 1: dev infra (kustomize)
kubectl apply -k k8s/manifests/dev

# phase 2: the app (helm)
helm upgrade --install asp k8s/charts/asp -f values-dev.yaml
```

That is exactly the split the homelab uses — infrastructure from one mechanism, the app from the chart. The homelab side consumes it with Flux: a `GitRepository` pointing at the app repo and a `HelmRelease` pointing at `k8s/charts/asp`. The app repo owns the chart; the GitOps repo just picks a version and supplies values.

---

## What I Took Away From It

The migration itself was one commit. The reason it was *safe* in one commit was everything around it: the refactor that made the layout match its consumer first, the render diff that proved the chart was a faithful translation, and the CI gates that keep it rendering forever.

The lesson generalizes: when replacing a deploy mechanism, do not rewrite — **translate, and prove the translation**. Equivalence first, improvements after. Helm earned its place not because it is fancier than Kustomize, but because the fleet is generated from data, and generating YAML from data is what a template engine is for. Kustomize keeps the static parts. Each tool ended up doing the one thing it is best at.
