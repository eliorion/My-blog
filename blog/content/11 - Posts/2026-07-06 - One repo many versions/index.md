---
title: "One Repo, Many Versions: Living with release-please"
date: 2026-07-06T09:00:00+02:00
draft: false
aliases: ["/11---posts/2026-07-06---one-repo-many-versions/"]
topics:
  - Homelab
  - DevOps
  - CI/CD
tags:
  - release-please
  - monorepo
  - versioning
  - conventional-commits
  - ci-cd
  - github-actions
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
  alt: release-please per-component versioning
  caption: ""
  relative: true
  hidden: true
  hiddenInList: true
  hiddenInSingle: false
---

## One Version Would Be a Lie

The asp repository holds a dozen deployable components: scrapers, an orchestrator, admin UIs, a webapp, migration images, a JupyterLab image. One repository, because they form one platform and change together in review. But one *version* for all of them would be a lie — a webapp copy change should not bump the scraper, and a scraper fix should not produce a new webapp image that differs by nothing.

So the project uses **release-please** with per-component releases. Each component gets its own version, its own changelog, its own Git tag, and its own image build. Release-please watches conventional commits, works out which components changed, and maintains a rolling release PR per component; merging that PR tags the release and kicks off the image build.

That is the brochure version. This post is about the two ways it actually broke, because both failures taught me more than the setup did.

---

## Problem One: The Lockfile That Disagreed

The Python services pin their dependencies with `uv.lock`, and CI enforces `uv lock --check` so the lockfile can never drift from `pyproject.toml`.

Release-please, doing its job, bumps the version in `pyproject.toml` on every release PR. But `uv.lock` also records **each package's own version** — and release-please knows nothing about uv. Result: every single release PR failed the lockfile gate. The releases were blocked by the very hygiene check that kept the repo healthy, and the two tools were each doing exactly what they promised.

The fix taught the release workflow about the lockfile: a step that re-locks the bumped packages **on the release branch** and pushes the sync commit back. One wrinkle matters: the push uses a PAT rather than the default workflow token, because commits made with the default token do not trigger CI — and an untested sync commit on a release branch defeats the point.

The general shape is worth remembering: any generated file derived from a version — lockfiles, chart versions, manifests — must be regenerated *by the release automation itself*, or every release arrives broken by construction.

---

## Problem Two: The One-Shot Pin That Fired Twice

Release-please starts a brand-new package at version 1.0.0. For a homelab platform where everything is honestly pre-1.0, the documented workaround is a bootstrap pin:

```json
"release-as": "0.1.0"
```

with an equally documented instruction: **remove it right after 0.1.0 ships**. The pin is a one-shot device. Left in place, it freezes the computed version at 0.1.0 forever.

I left it in place. Twice.

The first occurrence was `fbref-db-migrations`. Its pin survived after 0.1.0 shipped, so the open release PR regenerated a perpetual `v0.1.0 → v0.1.0` no-op. Changes to the migration image quietly stopped releasing — no error, no red pipeline, just a component whose version never moved while its twin (asp's own db-migrations, which never had the pin) advanced normally to 0.4.0. The silence is what makes this failure nasty: everything *looked* green.

The second occurrence, one day later, was louder. Seven newer components had all shipped their 0.1.0 with the same latent pin still in config. When a scraper-engine fix merged, release-please computed 0.1.0 again — and this time tried to **re-create the tag**, failing with `Validation Failed ... tag_name already_exists`. Same root cause, opposite symptom: one form of the bug releases nothing silently, the other fails loudly on a tag collision.

The first time was a mistake. The second time was a diagnosis: the process itself had a gap. A step that lives only in documentation — "remove the pin after it fires" — is a step that will be skipped, because nothing fails at the moment of the omission. The cleanup got done properly the second time: every shipped component's pin removed in one commit, so the class of bug is gone rather than the instance.

---

## What It Buys When It Works

With both failure modes fixed, the release flow earns its keep. A merged fix produces exactly the releases it should: release-please computes the next version per component from the commit types, tags it, the build pushes the image, and a `bump-chart` job rewrites that component's tag in the Helm chart values with a `[skip ci]` commit.

The Git log itself becomes the release ledger — a readable interleaving of real changes and the automation reacting to them:

```
feat(fbref): scrape past Cloudflare via a FlareSolverr solver
chore: release main
chore(chart): bump fbref image to fbref-scraper-v0.8.0 [skip ci]
```

Each component moves at its own pace, the chart always points at real released images, and nobody hand-edits a version number anywhere.

---

## What I Took Away From It

Per-component releasing in a monorepo is worth it, but it is not free: release automation touches generated files and one-shot config, and both are places where correct-looking setups fail later.

Two rules came out of this. First, **whatever the version bump invalidates, the automation must regenerate** — a release PR that fails its own repo's gates is automation fighting itself. Second, **one-shot configuration is a loaded trap**: if a config value must be removed after it fires, its removal has to be part of the same motion that ships it, not a documented intention. The first failure teaches you the trap exists. The second one proves it was never about luck.
