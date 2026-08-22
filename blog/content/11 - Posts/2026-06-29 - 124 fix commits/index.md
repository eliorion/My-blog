---
title: "124 Fix Commits: Learning Kubernetes by Breaking It"
date: 2026-06-29T09:00:00+02:00
draft: false
aliases: ["/11---posts/2026-06-29---124-fix-commits/"]
topics:
  - Homelab
  - DevOps
  - GitOps
tags:
  - kubernetes
  - gitops
  - flux
  - yaml
  - learning
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
  alt: 124 fix commits retrospective
  caption: ""
  relative: true
  hidden: true
  hiddenInList: true
  hiddenInSingle: false
---

## The Numbers

My homelab repository has 270 non-merge commits. 124 of them have "fix" in the subject line.

Almost half of everything I have ever pushed to this cluster exists to repair something the previous push broke. The worst single day is 2026-02-27, with 29 commits. The runner-up is the very next day, with 21 more. Most of them are one line long, and some of them are genuinely embarrassing to read now.

This post is about why I am not cleaning that history up, and what it actually taught me.

---

## GitOps Makes Every Mistake Public

The cluster is driven by Flux: nothing reaches it except through Git. That is the whole point of the setup — Git is the single source of truth, the audit log, the rollback mechanism.

It also has a consequence I did not appreciate at the beginning: **the cluster is the test environment**. When I was starting out, I had no local validation step. The only way to find out whether a manifest worked was to commit it, push it, wait for Flux to reconcile, open k9s, and read the error. Every iteration of every debugging session is a commit. The feedback loop looked like this:

```
edit YAML → commit → push → wait for reconcile → read the error → repeat
```

On a bad day, that loop runs thirty times. And Git remembers all thirty.

---

## The GLPI Day: 29 Commits

On 2026-02-27 I was deploying GLPI, first as a single pod, then split into an app and a MariaDB database. The commit subjects tell the story better than I could:

```
fix: wrong containerPort
fix: change pvc db name
fix: add MARIADB_RANDOM_ROOT_PASSWORD to configmap
fix: add the port 3006 on the pod
fix: database deployment label match
fix: change targetPort name field
```

My favorite is `fix: add the port 3006 on the pod` — the commit fixing the database port has a typo in the port. Each of these one-liners encodes a lesson I now consider basic:

- A **Service finds pods by label selector**, and nothing warns you when the selector matches nothing. The Service exists, the endpoints list is just empty, and traffic goes nowhere.
- A **named targetPort** must match the port *name* in the pod spec, not the number.
- A Deployment with the wrong `containerPort` will happily report `Running` and still serve nothing.
- A PVC name in a Deployment's volume block has to match the actual PVC, and the error only shows up as a pod stuck in `Pending`.

None of this is exotic. It is exactly the kind of thing you only internalize by getting it wrong with a real scheduler watching.

---

## The Keycloak Day: 21 Commits

The next day I added Keycloak with a Postgres database, and the failure mode changed: it was no longer Kubernetes semantics, it was YAML itself.

```
fix: wrong charactere intentation
fix: change intentation
fix: intentation issue
fix: yaml '=' change to ':'
fix: change to string
fix: change to string
```

Three separate commits about indentation. One commit where I had written `=` instead of `:` — muscle memory from some other language. And `fix: change to string` **twice**, because ConfigMap values must be strings: `"true"` is valid where `true` is not, `"8080"` where `8080` is not, and the API server tells you this in the least helpful phrasing it can find.

The rest of that day is debugging by elimination, in public:

```
fix: test without prob
fix: desactivate request ressource
```

Disabling the probes to figure out whether the probe or the app was broken. Removing resource requests to see if scheduling was the blocker. It is not elegant. It is exactly how you isolate a variable when you do not yet know which layer is lying to you.

---

## The Storms Did Not Fully Stop

I would like to say the fix storms ended once I learned YAML. They did not — they changed nature. On 2026-06-03 there are 19 commits, almost all about credentials and encrypted secrets while bringing production up: `fix: cloudflare cred`, `fix: app enc file with right key`, `fix: gh auth`.

The difference is *why* the loop was long. Those failures were about SOPS-encrypted secrets and tunnel tokens that can only be verified against the live cluster — not about a missing space in a manifest. The feedback loop was still push-driven, but the mistakes had moved up a layer. That is what progress actually looks like: you do not stop breaking things, you break more interesting things.

---

## From Storms to Signal

Put an early commit and a recent one side by side:

```
fix: intentation issue
```

```
fix(asp-db): restore from R2 archive after volume loss

The 2026-06-11 HA-expansion storm reformatted the Longhorn volumes
(doc 07 troubleshooting: disk-UUID mismatch chain). asp-db bootstraps
via recovery from its own barman archive (base backup + WAL replay)...
```

Same repository, same author, three months apart. The recent commits have scopes, real bodies, root causes, and references to documentation. Nobody told me to do that — it happened because I eventually needed my own history to debug my own cluster, and `fix: intentation issue` helps nobody, including future me.

The habits that killed most of the storms were boring ones: running `kustomize build` locally before pushing, so syntax errors die on my machine instead of in the cluster; validating YAML before it leaves the editor; testing in staging before production existed as a concept in the repo. In my other projects those checks are now enforced in CI, precisely because I remember what it cost not to have them.

---

## Why I Keep the History

It is tempting to squash all of this into a clean, professional-looking log. I will not, for two reasons.

First, it is the most honest record I have of what learning Kubernetes actually looks like. Courses show you the happy path. The real path is 29 commits in one day because a label selector silently matches nothing.

Second, the history *is* the curriculum. When I read `fix: database deployment label match`, I remember precisely what a Service with empty endpoints behaves like, because I spent an evening inside that failure. The embarrassing commits are load-bearing.

I wrote once about being willing to become a beginner again. This log is what that decision looks like from the inside: 124 small repairs, each one a thing I did not know the day before.
