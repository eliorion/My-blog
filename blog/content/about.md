---
title: "About"
url: "/about/"
summary: "Who I am, what I run, and how I know it works"
---

I'm Samuel Kharitonoff. I build and operate infrastructure — a multi-node Kubernetes
cluster, a geo-distributed backup fleet, and the platform that runs on top of them — and
I write down what happens, including the parts that go wrong.

This blog is the record of that: 34 posts and roughly 34,000 words since August 2025,
covering six projects. Not tutorials. Post-mortems, design
decisions, and the failures that changed my mind.

---

## Background

**IT Project Lead** *(internship)* · French Ministry of Defence, Brétigny-sur-Orge ·
May → Nov 2025

Led the deployment of GLPI, a service management platform handling requests and
incidents: gathered requirements from business stakeholders, documented the target
architecture, planned the work, and delivered to production. Configured request routing,
queues and escalation paths for the support teams, and containerised the platform with
**rootless Podman** under the organisation's security constraints. Coordinated users,
security and infrastructure stakeholders, tracked dependencies to closure, trained the
business teams and wrote the user documentation.

**Real-time Software Developer, CI/CD** *(work-study)* · Thales, Cholet ·
Sept 2021 → Aug 2024

Automated unit testing inside a CI/CD pipeline, making build results a reliable release
gate for defence software deliverables. Developed and optimised signal-processing
algorithms in C/C++ for embedded targets under strict industrial standards; reviewed
peers' code and contributed to technical validation. Worked in a cross-functional squad
— hardware, software, test — on a production-sensitive product, growing over three years
from defect triage to full ownership of software modules.

**Chief Information Officer** · Junior ESIEE, Noisy-le-Grand · May 2022 → Apr 2023

Owned the IT architecture of the student-run consultancy and supervised the IS officers
across client engagements. Introduced a CI/CD chain and knowledge-capture practices —
documentation, guides, handover between mandates — and managed the application estate and
access control so service survived each change of team.

### Education

- **Master's in Engineering Management** · Université de Sherbrooke, Quebec ·
  Jan 2024 → Nov 2025 — planning and tracking technical projects under time and budget
  constraints, leading cross-functional teams, process optimisation (Lean, Six Sigma),
  decision-making aligned with business objectives
- **Engineering Degree, Embedded Systems** · ESIEE Paris · Sept 2021 → Aug 2024 —
  hardware and software architectures, Linux, real-time algorithms, microcontrollers and
  sensors; completed as a work-study programme at Thales
- **DUT, Electrical and Industrial Computer Engineering** · IUT de Nantes ·
  Sept 2019 → Sept 2021 — analog and digital electronics, control systems, first embedded
  software and supervision tools

**Six Sigma Green Belt**, Sept 2025. French native, English professional — every
technical project and all documentation, including this blog, in English. Basic Spanish.

---

There is a thread running from that CV into this blog, and it is not a coincidence.

At the Ministry of Defence I put GLPI into production under rootless Podman, inside a
security posture that did not negotiate. Months later I deployed GLPI again — this time
on my own Kubernetes cluster, split into an app and a MariaDB database. It took
**29 commits in one day**, and the commit fixing the database port has a typo in the
port. Same application, same person, a control plane I did not yet understand. That day
is [written up in full]({{< relref "/11 - Posts/2026-06-29 - 124 fix commits/index.md" >}}),
typos included, because the gap between *delivered it* and *understood it* is the
interesting part.

The CI/CD I automated at Thales was a release gate for defence software. The pipelines
here do the same job for my own systems — Trivy on the images, a render diff on the Helm
chart, `release-please` on the versions. The Linux and embedded work at ESIEE is why I
[learned the operating system before the container runtime]({{< relref "/11 - Posts/2026-02-23 - Why learn linux before containerisation/index.md" >}})
rather than the other way round.

---

## What I run

Three systems, each solving a problem the previous one exposed.

### The cluster

A **Talos Linux** Kubernetes cluster, driven end-to-end by **Flux**. Talos was a
deliberate replacement for K3s on a hand-installed VM: no SSH, no shell, no package
manager, the whole machine configured through an API. If Git is the source of truth for
the cluster, the nodes underneath it should be declarative too.

On it:

- **CloudNativePG** for Postgres — base backups and continuous WAL archiving to
  Cloudflare R2, which gives point-in-time recovery
- **Longhorn** for replicated block storage
- **Keycloak** as the identity provider, **cert-manager**, **Renovate**, and a **Nexus**
  pull-through cache
- **Actions Runner Controller** — ephemeral CI runners as pods, scaling 0→2, each with a
  dind sidecar, so pipelines reach private services without exposing the cluster
- **Tailscale** for the private network; **Cloudflare Tunnel** for the little that faces
  the internet
- Every credential encrypted with **SOPS + age**, committed to Git

The `infrastructure/` tier is split into `controllers/` and `services/` because CRD
providers must reconcile before the custom resources that depend on them. Before that
split, ordering was survived by retry luck.

### The backup fleet

The cluster backs itself up — etcd snapshots, CNPG WAL archives, Longhorn replicas. All
of it reachable *from the cluster*, with credentials that live *in* the cluster. Anything
that owns the cluster can delete every backup it made. That is a convenience copy, not
disaster recovery.

So **garage-fleet**: a 4-node [Garage](https://garagehq.deuxfleurs.fr/) S3 store on
**NixOS + ZFS**, provisioned with `disko` + `nixos-anywhere` + `deploy-rs` + `sops-nix`.
Three storage nodes in three physical locations, each its own Garage zone, plus a
zero-capacity gateway that only serves the S3 API. Everything binds to Tailscale
addresses — no public endpoint anywhere in the fleet.

Two properties matter more than the technology:

- **A separate trust domain.** Different OS, different identities, different age keys,
  different control plane. The prod cluster's credentials can *write* backups. They
  cannot administer the fleet, reach its nodes, or change its configuration. Full
  compromise of prod buys an attacker the ability to upload garbage, not to destroy
  history.
- **A snapshot moat.** `sanoid` takes scheduled read-only ZFS snapshots plus regular
  scrubs. S3 operations happen inside the castle; snapshots live outside its walls.
  Nothing short of root on the node can destroy one. Encrypted objects roll back with a
  single `zfs rollback`.

Root disks are **LUKS**, unlocked unattended by a TPM-sealed key under **Secure Boot**
via `lanzaboote` — so a stolen box is inert, but the fleet still boots without me.

### The platform

**asp**, a containerised scraping platform, exists to be a real workload: scraper engine,
orchestrator, admin dashboard, analyzer, a Next.js front end, a dedicated football-stats
pipeline, and an in-cluster JupyterLab. One Helm chart, per-component versioning through
`release-please`, database migrations in the pipeline, deployed by GitOps like everything
else.

The orchestrator reclaims stale `in_progress` URLs when a worker dies mid-job, and each
worker beats a liveness heartbeat *inside* its crawl loop — so Kubernetes restarts a
genuinely stuck pod rather than a merely busy one. That distinction cost me an outage to
learn.

---

## How I work

**I restore the backup.** My homelab lost a database because the CNPG cluster had been
faithfully shipping WAL since bootstrap with no base backup yet — WAL alone is a diff
stream with nothing to apply it to. A freshly bootstrapped cluster has a multi-hour window
with no recovery point at all, while looking fully backed up from outside. I found that by
losing data, and the fix went into the manifests the same day.

**I keep the evidence.** The homelab repository has 270 non-merge commits. 124 of them say
"fix". One bad day is 29 commits, the next is 21. I have not rewritten that history and I
do not intend to: the cluster *was* my test environment, and every `fix: change targetPort
name field` is a Kubernetes primitive I now understand because a real scheduler rejected
my guess.

**I write down the tradeoff, not the win.** node-A of the backup fleet is onsite and
doubles as my workstation — a compromise I named in the post rather than hiding, because
the honest version is more useful than the clean one. Same with the Nexus cache that
silently served stale vulnerability data, the `noauto` mount option that nearly left a
server unbootable, and the week `sops` refused to decrypt for three unrelated reasons in
sequence.

**I gate what ships.** Container images are built, scanned by Trivy on CRITICAL and HIGH,
and only then pushed to the registry. Accepted CVEs live in `.trivyignore` with a reason
and a date attached to each one.

---

## Why both halves

My Master's is in Engineering Management: planning under constraint, leading
cross-functional teams, Lean and Six Sigma, deciding with a budget attached. That
training is real, and on its own it is not enough. A plan built by someone who has never
restored the backup is a guess with a Gantt chart around it.

So I keep operating. I have lost a database to a backup that looked healthy from the
outside, spent a week on an error message that turned out to be three unrelated bugs, and
come one mount option away from an unbootable server. Those are the experiences that make
an estimate honest and a risk register something other than a formality — and they are
the reason I can sit between a security stakeholder and an infrastructure team without
either of them having to simplify for me.

Requirements, architecture, delivery, and the 3 a.m. failure are the same job seen from
four angles. I want to be credible at all four.

## Proof of work

Each project below has its own series. The posts are written as post-mortems — what I
built, what broke, and what the fix actually was.

**Kubernetes and the homelab** —
[from K3s to Talos]({{< relref "/11 - Posts/2026-06-28 - From K3s to Talos/index.md" >}}),
[Postgres backups that actually restore]({{< relref "/11 - Posts/2026-07-08 - Postgres backups that restore/index.md" >}}),
[CI runners inside the cluster]({{< relref "/11 - Posts/2026-07-10 - CI runners inside the cluster/index.md" >}}),
[Flux alerts to Telegram]({{< relref "/11 - Posts/2026-07-12 - Deploy failures to Telegram/index.md" >}}),
[124 fix commits]({{< relref "/11 - Posts/2026-06-29 - 124 fix commits/index.md" >}})

**garage-fleet — ransomware-resistant backups** —
[the design]({{< relref "/11 - Posts/2026-07-14 - A ransomware-resistant backup fleet/index.md" >}}),
[LUKS, TPM and Secure Boot]({{< relref "/11 - Posts/2026-07-16 - Unattended disk encryption with TPM and Secure Boot/index.md" >}}),
[one mount option from unbootable]({{< relref "/11 - Posts/2026-07-18 - One mount option from unbootable/index.md" >}}),
[three bugs deep in sops]({{< relref "/11 - Posts/2026-07-20 - Three bugs deep in sops/index.md" >}}),
[one script to run a fleet]({{< relref "/11 - Posts/2026-07-22 - One script to run a fleet/index.md" >}})

**asp — the platform** —
[building it]({{< relref "/11 - Posts/2026-06-26 - Building a scraping platform on Kubernetes/index.md" >}}),
[Kustomize to Helm]({{< relref "/11 - Posts/2026-06-30 - From Kustomize to Helm/index.md" >}}),
[a scraper that survives its own death]({{< relref "/11 - Posts/2026-07-02 - A scraper that survives its own death/index.md" >}}),
[caching everything through Nexus]({{< relref "/11 - Posts/2026-07-04 - Caching everything through Nexus/index.md" >}}),
[one repo, many versions]({{< relref "/11 - Posts/2026-07-06 - One repo many versions/index.md" >}})

**mve-itguard — GitOps without Kubernetes** —
[why I built it]({{< relref "/11 - Posts/2026-05-24 - mve-itguard/index.md" >}}),
[Compose + GitHub Actions]({{< relref "/11 - Posts/2026-05-25 - mve-itguard-gitops/index.md" >}}),
[secrets in Git without fear]({{< relref "/11 - Posts/2026-05-27 - mve-itguard-secrets/index.md" >}}),
[runners that cannot hurt production]({{< relref "/11 - Posts/2026-05-28 - mve-itguard-runners/index.md" >}}),
[one command to provision a server]({{< relref "/11 - Posts/2026-05-29 - mve-itguard-bootstrap/index.md" >}}),
[automated key rotation in CI]({{< relref "/11 - Posts/2026-05-30 - mve-itguard-key-rotation/index.md" >}}),
[multi-node backup with restic]({{< relref "/11 - Posts/2026-05-31 - mve-itguard-backup/index.md" >}})

---

Browse everything by [topic](../topics/) or [tag](../tags/), or dig through the
[archive](../archives/). I'm on
[LinkedIn](https://www.linkedin.com/in/samuel-kharitonoff/?locale=en_US).
