---
title: "Postgres Backups That Actually Restore: CNPG + R2"
date: 2026-07-08T09:00:00+02:00
draft: false
topics:
  - Homelab
  - DevOps
  - Kubernetes
tags:
  - cnpg
  - postgres
  - backup
  - disaster-recovery
  - barman
  - cloudflare-r2
  - longhorn
  - kubernetes
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
  alt: CNPG backups to Cloudflare R2
  caption: ""
  relative: true
  hidden: true
  hiddenInList: true
  hiddenInSingle: false
---

## A Backup Is a Liability Until You Restore It

Everyone agrees that databases need backups. Far fewer people have ever restored one. Until you have, a backup is not protection — it is a checkbox that makes you *feel* protected while quietly hiding whatever is wrong with it.

My homelab found out the difference three times in two weeks: once by losing data it could not recover, once by recovering data it nearly lost, and once by cleaning up the mess the recovery left behind. This post walks through all three, because together they taught me more about disaster recovery than any documentation did.

---

## The Setup: CNPG, Barman, and Cloudflare R2

The cluster's databases run on **CloudNativePG (CNPG)**, the Postgres operator. Its backup model has two parts, handled by Barman under the hood:

- **Base backups** — a full snapshot of the cluster's data directory, taken on a `ScheduledBackup` (03:00 in my case)
- **WAL archiving** — every write-ahead-log segment is shipped continuously to object storage

Both land in a **Cloudflare R2** bucket (`s3://asp-cnpg-staging`). A restore replays the newest base backup, then applies WAL on top, which gives point-in-time recovery: you lose at most the seconds since the last WAL segment shipped.

That is the theory. The practice had sharper edges.

---

## Lesson One: The First Backup Must Be Immediate

The first incident was mundane: a staging node got renamed. That was enough to orphan the local-path PVs (this was before Longhorn), which forced a fresh re-bootstrap of the CNPG cluster.

No problem — that is what backups are for. Except recovery was impossible, because **no base backup existed yet**. The cluster had been shipping WAL faithfully since bootstrap, but WAL alone is useless: it is a diff stream with nothing to apply it to. The first *base* backup was still waiting for the 03:00 schedule.

A freshly bootstrapped CNPG cluster with a `ScheduledBackup` has a multi-hour window in which it has **no recovery point at all** — while looking, from the outside, fully backed up.

The fix is one line:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: ScheduledBackup
spec:
  immediate: true   # take a base backup as soon as the cluster exists
  schedule: "0 0 3 * * *"
```

With `immediate: true`, every (re)creation of the cluster takes its base backup right away, and the WAL stream has an anchor from minute one. I added it to both databases, staging and production. It is the cheapest insurance in the whole repository.

---

## The Real Test: Volume Loss

On 2026-06-11, during the HA expansion of the cluster, a disk-UUID mismatch chain ended with the Longhorn volumes being reformatted. The database volumes were simply gone — not corrupted, not stale: empty.

This is the moment a backup strategy either exists or does not. The application database, `asp-db`, bootstrapped straight into **recovery mode** from its own Barman archive: newest base backup pulled from R2, WAL replayed on top, cluster back with its data.

One detail in that restore matters more than it looks:

```
restore source:  s3://asp-cnpg-staging/asp-db/      (read-only)
new archive:     s3://asp-cnpg-staging/asp-db-r1/   (the recovered cluster writes here)
```

The recovered cluster archives under a **new serverName** (`asp-db-r1`), so the archive it was restored *from* stays untouched. If the restore had gone wrong halfway, the source would still have been intact for a second attempt. Never let a recovering database write into the archive that is currently saving its life.

---

## The Contrast: The Database With No Backups

The same storm took out a second database, `fbref-db` — the football statistics store. It had no Barman configuration, no base backups, no WAL archive.

There was nothing to restore. The only option was deleting the `Cluster` resource and recreating it fresh, then re-scraping the data from scratch.

Two databases, same cluster, same day, same failure. One came back with its data; one came back empty. The entire difference was configuration that had felt optional when the data "did not matter yet". Data starts mattering before you decide it does.

---

## The Cleanup: One Archive, Not Two

Recovery leaves debt behind. After the restore, the bucket held two prefixes — the old `asp-db/` source and the new `asp-db-r1/` archive — and the manifests pointed at the `-r1` name forever.

When the staging database later ran a fresh `initdb`, I repointed the Barman `serverName` back to plain `asp-db` to collapse the bucket to a single prefix. That step has a trap: the stale `asp-db/` prefix had to be **purged before reconciling**, because a brand-new Postgres cluster starts on timeline 1 and generates WAL segment names that collide with the old archive's timeline-1 segments. Mixing WAL from two different cluster generations under one prefix silently poisons the archive — the backup would look healthy and restore garbage.

Purge first, reconcile, verify the new archive is healthy, then drop the orphaned `asp-db-r1/`. Archive hygiene is unglamorous, but a backup you cannot trust is exactly as useful as no backup.

---

## What I Keep From This

The whole story compresses into four rules I now treat as defaults:

1. **`immediate: true` on every ScheduledBackup.** A cluster without a base backup is unprotected, whatever its WAL stream says.
2. **Restore into a new serverName.** The archive you restore from is read-only until the recovery is proven.
3. **Never reuse a WAL prefix across cluster generations.** Timeline-1 names collide; purge before you repoint.
4. **A backup that has never been restored is a hope**, not a plan. The `asp-db` restore succeeded because the archive had exactly the shape a restore needed — and I only know that because the restore actually ran.

The volume loss cost me an afternoon. The database with backups came back; the one without taught me why the other one had them.
