---
title: "When a Deploy Fails, My Phone Buzzes: Flux Alerts to Telegram"
date: 2026-07-12T09:00:00+02:00
draft: false
topics:
  - Homelab
  - DevOps
  - GitOps
tags:
  - flux
  - telegram
  - alerting
  - prometheus
  - alertmanager
  - monitoring
  - gitops
  - homelab
  - self-hosted
projects:
  - HomeLab gitDevSecOps
categories:
  - IT
  - Homelab
weight: 2
cover:
  image: cover.svg
  alt: Flux deploy alerts to Telegram
  caption: ""
  relative: true
  hidden: true
  hiddenInList: true
  hiddenInSingle: false
---

## The Babysitting Problem

A homelab you have to babysit is a homelab you will eventually ignore. GitOps makes this worse in a sneaky way: because deploys happen automatically when a commit lands, nothing forces you to watch them land. You push, you close the laptop, and a HelmRelease can sit broken for days before you happen to open Grafana and notice.

The fix is not more dashboards. Dashboards are where information waits for you. I needed the opposite: failures that come find me. For me, "me" is Telegram — already on my phone, already has a bot API, costs nothing.

---

## Path One: Flux Tells Me Directly

Flux ships a **notification-controller** for exactly this. One `Provider` pointing at the Telegram bot API, one `Alert` subscribing it to HelmRelease events, and every reconciliation failure lands in my chat — with the actual error reason in the message, not just "something failed".

That last part matters more than it sounds. The difference between *"HelmRelease asp failed"* and *"upgrade retries exhausted"* with the reason attached is the difference between opening a laptop to investigate and knowing from the couch what the fix is.

---

## Path Two: The Metrics Keep Shouting

The event path has a weakness: an event is a moment. If the notification fires while I am asleep, one Telegram message at 03:00 is easy to scroll past, and Flux will not re-send it — from its perspective, nothing new happened.

So there is a second, independent path through the monitoring stack:

- A **PodMonitor** scrapes the flux-system controllers' metrics into Prometheus
- A **PrometheusRule** fires whenever `gotk_reconcile_condition` reports `Ready=False` for a resource
- **Alertmanager** routes the alert to the same Telegram chat, with the bot token mounted via `bot_token_file`

This path is condition-driven, not event-driven: as long as the resource *stays* broken, the alert *stays* firing, and Alertmanager re-notifies on its schedule. One path tells me the moment something breaks; the other refuses to let me forget it is still broken.

---

## The Secret Plumbing

The bot token is the only credential in the chain, and it exists in two namespaces — `flux-system` for the notification-controller and `monitoring` for Alertmanager. Both copies live SOPS-encrypted in Git like every other secret in the repository, and Alertmanager reads its copy from a file mount rather than inline config, so the rendered config carries no plaintext token.

---

## Alerts Plus Auto-Rollback

This alerting sits on top of the remediation the HelmReleases already carry: failed upgrades are armed to roll back automatically. Between the two, failures sort themselves into exactly two buckets:

1. **Self-healing** — the rollback restores the last good release, and the Telegram message is informational: something landed badly, production already recovered, fix it when convenient.
2. **Self-announcing** — the failure persists, and the metrics path keeps buzzing until I deal with it.

What no longer exists is the third bucket: silently broken.

---

## Small Change, Different Relationship

This was one of the smallest changes in the repository — a Provider, an Alert, a PodMonitor, a PrometheusRule — and it changed my relationship with the cluster more than most big ones. I stopped checking whether deploys worked. I now assume silence means success, because the system has proven that failure is loud.

That is the property worth building toward: not a cluster that never breaks, but one that never breaks quietly.
