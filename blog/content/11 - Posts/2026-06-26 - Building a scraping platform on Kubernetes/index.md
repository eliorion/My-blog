---
title: "Building a Scraping Platform on Kubernetes"
date: 2026-06-26T09:00:00+02:00
draft: false
topics:
  - Homelab
  - DevOps
  - Kubernetes
tags:
  - kubernetes
  - helm
  - scraping
  - postgres
  - flyway
  - release-please
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
  alt: asp scraping platform
  caption: ""
  relative: true
  hidden: true
  hiddenInList: true
  hiddenInSingle: false
---

## Why Build My Own Scraping Platform

My homelab exists to learn Kubernetes and DevSecOps properly, not just to run a few self-hosted apps. To do that I needed a real workload — something with multiple services, a database, external dependencies, and enough moving parts that the operational side actually matters.

**asp** is that workload. It is a containerized web-scraping platform that collects listings and football statistics, stores them in Postgres, and exposes the results through a web app. On the surface it scrapes data. Underneath, it is an excuse to build a production-shaped system: a Helm chart, a full CI/CD pipeline, database migrations, per-component releases, and everything running on the cluster the way a real product would.

This post is an overview of what the platform is and the decisions behind it.

---

## What asp Is

The platform started as a single scraping container and grew, service by service, into a small ecosystem:

- **scraper engine** — the workers that fetch and parse pages
- **orchestrator** — assigns URLs to workers, tracks progress, retries failures
- **admin-ui** — an operator dashboard to watch throughput and manage the queue
- **analyzer** — turns raw scraped rows into queryable data
- **webapp** — the public Next.js front end with search and a buying guide
- **fbref-scraper** — a dedicated pipeline for football statistics
- **lab** — an in-cluster JupyterLab sandbox for ad-hoc analysis

Everything runs as containers on the cluster, packaged in one Helm chart, and deployed through GitOps from the homelab repository.

---

## The Services

### Scraper engine and orchestrator

The first version merged what were originally two separate services — a URL crawler and a content scraper — into a single engine. Keeping them apart added coordination overhead without buying anything, so they became one worker that crawls and extracts in the same loop.

The orchestrator sits in front of the workers. It hands out URLs, records their state in Postgres, and — importantly — reclaims stale `in_progress` URLs when a worker dies mid-job. Without that, a crashed pod would silently strand everything it had claimed. Each worker also beats a liveness heartbeat inside its crawl loop, so Kubernetes restarts a truly stuck pod instead of one that is merely busy.

### admin-ui

Operating a scraper blind is painful, so the orchestrator ships with a dashboard. It shows scraped-items-per-minute throughput, average rates, and lets an operator retry or clear the failed queue without touching the database by hand. It started as a Streamlit UI bolted onto the orchestrator image as a second process, and later became its own service that talks directly to the database.

### webapp

The public front end went through more iterations than anything else in the project. It began as a Flutter web app with a Keycloak-authenticated backend, moved to a React + Vite SPA, and finally settled as a Next.js app. Along the way it gained a multilingual UI, advanced search, and a multi-step buying guide rebuilt as a customer-discovery questionnaire.

The lesson from those rewrites was less about frameworks and more about not over-committing early: the front end changed shape several times before the product did.

### fbref-scraper

A second, independent pipeline scrapes football statistics from FBref. It lives in its own namespace with its own release identity, crawls the A-Z player index and per-player match logs, and covers the big-5 European leagues with matches and queryable views.

FBref sits behind Cloudflare, which blocks naive scrapers. The pipeline gets past it with a **FlareSolverr** solver that resolves the challenge, plus adaptive pacing so the scraper slows itself down instead of hammering the site into a ban.

### lab

Finally, a per-project JupyterLab sandbox runs in the cluster with cross-namespace access to the databases. It is the place to poke at scraped data interactively without exporting anything off the cluster.

---

## Getting Past Anti-Bot Defenses

Scraping at any real volume runs straight into rate limits and IP bans. Two mechanisms handle this.

**Multi-proxy lanes.** Rather than routing every worker through one IP, the chart generates per-pod scraper "lanes" from a matrix of *sites × proxies*. Each lane is a worker bound to a specific egress proxy, so load spreads across many source IPs. The lane list is data in the Helm values — adding a proxy or a site is a values change, not a code change.

**FlareSolverr for Cloudflare.** Sites protected by Cloudflare's challenge page get their own lane that routes through FlareSolverr, which solves the challenge and returns a usable session. This is heavier than a plain HTTP fetch, so it only runs where it is actually needed.

---

## The Data Layer

Everything lands in Postgres. Schema changes are managed with **Flyway** migrations shipped as their own image, so the database schema is versioned and applied the same way in every environment — no hand-run SQL, no drift between staging and production.

This mattered most during recovery. When a database volume was lost, the schema healed itself by re-running the Flyway tier on a fresh init, instead of depending on a stale bootstrap `init.sql`. Treating migrations as a first-class, idempotent step made the database reproducible rather than precious.

---

## Packaging: From Kustomize to Helm

The deploy layer started with Kustomize and moved to a single Helm chart. The reason was templating: with a dozen services, several of them generated from a *sites × proxies* list, Kustomize overlays became repetitive fast. Helm lets the whole scraper fleet be driven by a values list — the chart became project-agnostic, generating services from data rather than duplicating manifests.

The chart also wires in the operational safety net: readiness probes and Helm test hooks that let the CD system auto-rollback a bad release, admin UIs that can be exposed by flipping a Service type in values, and Grafana visualization wired to the scrapers.

---

## Releases and CI/CD

With many services in one repository, releasing them together would be wrong — a change to the webapp should not bump the scraper. The project uses **release-please** to give each component its own version, changelog, and image tag. That independence took real tuning: unpinning stale `release-as 0.1.0` values, keeping `uv.lock` in sync on release PRs, and making sure a component only releases when it actually changes.

The CI pipeline builds every image, runs security gates — semgrep, eslint, syft, detect-secrets, trivy — and validates the whole stack end-to-end on a disposable **k3d** cluster before anything reaches the real one. To keep that fast and reliable, image and package pulls route through a **Nexus** mirror, which sidesteps Docker Hub rate limits (`docker.io 429`) and caches pip, npm, and Maven artifacts.

The guiding rule was zero drift between what runs locally and what runs in CI: the same lint, the same scans, the same build, so a green pipeline means the same thing everywhere.

---

## What I Took Away From It

asp was never really about the data. It was about building something big enough that the hard parts of running software — releases, migrations, rollbacks, caching, isolation — stopped being abstract.

The parts that paid off most were the boring ones: versioned migrations that made the database reproducible, per-component releases that kept services independent, and an e2e gate that caught broken configs before they reached the cluster. The scraping was the easy half. Operating it well was the point.
