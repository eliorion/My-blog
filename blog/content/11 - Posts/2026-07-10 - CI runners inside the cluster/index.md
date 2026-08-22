---
title: "CI Runners Inside the Cluster: ARC on Talos"
date: 2026-07-10T09:00:00+02:00
draft: false
aliases: ["/11---posts/2026-07-10---ci-runners-inside-the-cluster/"]
topics:
  - Homelab
  - DevOps
  - Kubernetes
tags:
  - arc
  - github-actions
  - ci-cd
  - talos
  - kubernetes
  - dind
  - nexus
  - flux
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
  alt: ARC self-hosted runners on Talos
  caption: ""
  relative: true
  hidden: true
  hiddenInList: true
  hiddenInSingle: false
---

## Why the Runners Moved In

The scraping platform's CI pipeline does not just build images — it deploys against a disposable cluster, runs end-to-end tests, and its releases feed the real cluster through GitOps. All of that lives behind my private network. GitHub-hosted runners cannot reach it, and I have no intention of exposing the cluster so they can.

The standard answer is self-hosted runners, and the standard question is *where*. Running them on a separate VM means another hand-managed host — exactly the thing the homelab has been eliminating. So the runners run where everything else runs: on the cluster itself, as Kubernetes pods, managed by **Actions Runner Controller (ARC)**, deployed by Flux like any other workload.

---

## ARC: Runners as Ephemeral Pods

ARC's `gha-runner-scale-set-controller` (0.14.2) watches GitHub's job queue and spins runner pods up on demand. The per-repo scale set scales between **0 and 2 runners** — when nothing is queued, nothing runs, and the cluster's RAM goes back to actual workloads. Each runner pod carries a **dind** (Docker-in-Docker) sidecar so jobs can build images, and authentication to GitHub uses a PAT stored in a SOPS-encrypted secret, like every other credential in the repository.

Ephemeral runners have a security property I care about: every job gets a fresh pod, and whatever a job does to its environment dies with it.

---

## Splitting Infrastructure in Two

Adding ARC forced a structural change that was overdue. The `infrastructure/` tier split into:

```
infrastructure/
├── controllers/   # CRD providers: cert-manager, cnpg, arc
└── services/      # platform workloads: cloudflare, keycloak,
                   # renovate, nexus, arc-runner-set
```

The reason is ordering. ARC's runner scale set is a **custom resource** that cannot exist until ARC's controller has installed its CRDs — the same relationship cert-manager has with `Certificate` and CNPG has with `Cluster`. Before the split, everything reconciled in one bucket and CRD races were survived by retry luck.

Now a dedicated `infrastructure-services` Flux Kustomization carries an explicit `dependsOn` the controllers Kustomization. Flux will not even attempt the services until every CRD provider is ready. Retry luck became declared ordering.

---

## The Cache Next Door

CI running inside the cluster has a nice side effect: the dependency cache can live one network hop away. The same change added **Nexus** (via the `stevehipwell/nexus3` 5.22.0 chart) with a `pypi-proxy` repository and anonymous read access — all provisioned declaratively by the chart's config job, so a rebuilt Nexus configures itself.

Runner pods pull Python packages from Nexus instead of PyPI: faster, immune to upstream rate limits, and one less way for CI to fail for reasons that have nothing to do with the code.

---

## Talos Says No: Pod Security

Talos ships with Pod Security Admission enforced, and dind is exactly the kind of thing PSA exists to stop — the sidecar needs privileged mode to run its own Docker daemon. Runner pods were rejected until the `arc-runners` namespace carried an explicit privileged PSA label.

I like this friction. On K3s, the runners would have silently gotten whatever they asked for. On Talos, the privilege is visible in Git: one labeled namespace, scoped to exactly the workload that needs it, with the rest of the cluster still restricted.

---

## The XL Pool: Capacity Planning on 50Gi

The heavy job in the pipeline is the k3d end-to-end leg — an entire disposable Kubernetes cluster inside dind. On the default pool it was starving, and worse, it could be evicted by whatever else CI was doing. The fix was a second, dedicated scale set: `self-hosted-arc-xl`. Nearly every line of its configuration exists because something on a small cluster can starve something else:

- **minRunners 1 / maxRunners 3** — one XL runner always warm, so the e2e leg never waits for scale-up; up to three PRs in parallel.
- **dind sidecar: 4Gi request, 10Gi limit** — the k3d cluster gets guaranteed memory, with headroom capped.
- **Hard one-pod-per-node podAntiAffinity** — three XL runners means three nodes; two e2e clusters never share a node's memory.
- **Default pool trimmed 5/15 → 2/8** — the RAM the XL pool reserves had to come from somewhere; the general pool shrank to pay for it.
- **Default dind bounded to 6Gi** — previously BestEffort, meaning a runaway build could balloon and OOM-evict a co-located XL e2e run mid-test. Bounded, it kills only itself.
- **CPU limits on the XL dind** — on this cluster **all three nodes are control planes**, and kubelet has no system-reserved carve-out. An uncapped dind churning through an e2e build can steal enough CPU to make etcd miss heartbeats, and an unhappy etcd is a cluster-wide event. The CPU limit is not about fairness between jobs; it is armor for the control plane.

The rollout had its own small trick: the repo variable that routes e2e jobs to the XL pool stayed unset until the XL listener had registered, so jobs kept falling back to the default pool during the transition. No red CI while the new pool came up.

---

## Capacity Planning Is the Job

It is tempting to read that commit as fiddly tuning. I read it as the actual work. On 50Gi spread across three nodes that are simultaneously control planes, worker fleet, and CI farm, there is no slack to hide mistakes: every request is a promise taken from someone else, every missing limit is an eviction waiting for the worst moment, and the scheduler only balances what you have told it about.

Cloud CI hides all of this behind someone else's capacity planning. Running the runners myself put every one of those tradeoffs in a YAML file I had to justify line by line — which is, after all, why the runners moved in.
