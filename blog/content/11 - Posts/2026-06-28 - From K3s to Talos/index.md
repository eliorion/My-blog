---
title: "From K3s to Talos: Rebuilding the Homelab Cluster"
date: 2026-06-28T09:00:00+02:00
draft: false
aliases: ["/11---posts/2026-06-28---from-k3s-to-talos/"]
topics:
  - Homelab
  - DevOps
  - GitOps
tags:
  - talos
  - k3s
  - flux
  - gitops
  - cnpg
  - longhorn
  - tailscale
  - kubernetes
  - self-hosted
  - homelab
projects:
  - HomeLab gitDevSecOps
categories:
  - IT
  - Homelab
weight: 2
cover:
  image: cover.svg
  alt: homelab k3s to talos migration
  caption: ""
  relative: true
  hidden: true
  hiddenInList: true
  hiddenInSingle: false
---

## Where I Left Off

The first version of this homelab was a single-node K3s cluster driven by Flux, hosting Linkding behind a Cloudflare tunnel, with secrets encrypted by SOPS and age. That setup did its job: it taught me GitOps end to end, and it proved that a Git repository could be the only way anything reaches the cluster.

Then the homelab started carrying real workloads. It stopped being a demo running one bookmark manager and became the place where my scraping platform, a Keycloak identity provider, monitoring, and self-hosted CI runners all had to live at once. At that point K3s on a hand-installed VM stopped being enough, and the cluster had to grow up.

This post is about that second phase: the databases, the storage, the private network, and eventually retiring K3s for **Talos Linux**.

---

## Real Databases with CloudNativePG

The first thing that changed was how databases are run. Hand-managed Postgres pods with a PVC are fine until you need backups, failover, and recovery, then they are a liability.

The cluster moved to **CloudNativePG (CNPG)**, a Kubernetes operator that treats Postgres as a proper managed resource. Keycloak runs on CNPG with an auto-generated database password. The scraping platform's databases run on CNPG too, each in its own namespace with independent Flux units.

The part that mattered most was backups. CNPG streams base backups and WAL archives to **Cloudflare R2** object storage, and takes a base backup immediately whenever a cluster is created or recreated. That design earned its keep: after a volume loss, the database restored from its R2 archive instead of being gone for good. Backups you have never restored are just a hope. This one was tested by accident and held.

---

## Why Leave K3s

K3s was never wrong; it just carried assumptions I no longer wanted. It runs on a general-purpose Linux VM that I installed and now have to patch, secure, and keep consistent. Every package on that host is surface area, and every manual tweak is drift that no Git repository knows about.

**Talos Linux** takes the opposite stance. It is an immutable, API-driven operating system built for one thing: running Kubernetes. There is no SSH, no shell, no package manager. The whole machine is configured declaratively and managed through an API. That fits the homelab's whole philosophy: if Git is the source of truth for the cluster, the nodes underneath it should be declarative too.

---

## The Migration

Moving a running cluster is not a flag you flip. I built the new **Talos** cluster alongside the old one and moved tier by tier, keeping the K3s cluster alive until each layer was proven on Talos.

The order was deliberate:

1. **Storage first**, stand up Longhorn on Talos so stateful workloads have somewhere to land.
2. **Infrastructure controllers**: copy the Cloudflare tunnel, ingress, and cert tiers.
3. **Monitoring**, move the observability stack so the new cluster is visible from the start.
4. **Databases**: bring CNPG across, seeding from the R2 archives, with volumes on Longhorn.
5. **Apps and services**: move the scraping platform and the rest last, once everything they depend on already worked.

Talos enforces **Pod Security Admission** more strictly than K3s did, which surfaced every workload that quietly relied on privileges. Monitoring, the CI runner namespace, and Longhorn all needed explicit privileged PSA labels: annoying in the moment, but exactly the kind of thing that should be visible instead of implicit. When the last tier was on Talos, the K3s VM was deleted, its deploy key removed, and the R2 backup path collapsed to a single archive. Retirement complete.

---

## Distributed Storage with Longhorn

On the single K3s node, storage was just a local path. A real cluster needs storage that survives a node, so the migration brought in **Longhorn**, a distributed block storage system for Kubernetes.

Longhorn runs with three replicas (one per node) so a volume stays available even if a node goes down. It is the foundation the CNPG databases and other stateful apps sit on. Its own UI is exposed the same careful way everything else is: over the private network, never the public internet.

---

## A Private Tailnet with the Tailscale Operator

The original cluster exposed things through Cloudflare tunnels: great for a public app like Linkding, wrong for internal tools. Operator dashboards, the Longhorn UI, and the Kubernetes API should be reachable by me, not by the internet.

The **Tailscale Kubernetes operator** solved this cleanly. It puts services directly on my private tailnet, so they are reachable from my devices without any public exposure, port forwarding, or extra reverse proxy. It ended up doing three distinct jobs:

- **Expose internal UIs**: the admin UI, the Longhorn UI, and the JupyterLab sandboxes are published on the tailnet, always-on and tokenless, pulling from a private image.
- **Egress proxy pool**: the scraper's outbound traffic routes through dedicated Tailscale egress proxies, giving the scraping lanes their source IPs through the tailnet.
- **Kubernetes API on the tailnet**: the cluster's API server is reachable through the operator's API server proxy, so I can run `kubectl` from anywhere on my tailnet without opening the control plane to the world.

One mesh network, no public ports, and the same access model whether I am home or not.

---

## Self-Hosted CI on the Cluster

Because the scraping platform's pipeline needs to reach the private cluster, CI runs on the cluster itself with **Actions Runner Controller (ARC)**. There is a default runner pool plus a larger `self-hosted-arc-xl` pool for the heavier k3d end-to-end jobs.

Runners pull their dependencies through a **Nexus** cache running in the cluster, which keeps builds fast and dodges public registry rate limits. A recurring headache was image pull secrets across namespaces: solved with **Reflector**, which mirrors one central `ghcr-pull-secret` everywhere it is needed, with ordering set so the secret exists before anything tries to pull.

---

## Staying Notified

A homelab you have to babysit is a homelab you will eventually ignore. The monitoring stack sends **Telegram alerts** whenever a Flux HelmRelease fails, so a broken deploy reaches my phone instead of waiting to be discovered. Combined with Flux's armed remediation and the Helm test hooks on the apps, most failures either roll themselves back or announce themselves loudly.

---

## What This Phase Taught Me

The first homelab taught me GitOps. This phase taught me operations: what it takes to run stateful workloads you cannot afford to lose, and how much calmer the whole system becomes when the nodes are declarative too.

Talos removed a category of problem I had stopped noticing: the slow drift of a hand-managed host. CNPG and R2 turned "I hope the database is fine" into a tested restore. The tailnet made private things actually private. None of it was strictly necessary to keep Linkding online. All of it was necessary to trust the cluster with things that matter.

The homelab is no longer a place I experiment and rebuild by hand. It is infrastructure I can reason about: declared in Git, from the operating system up.
