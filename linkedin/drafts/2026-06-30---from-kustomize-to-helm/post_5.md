---
angle: tool spotlight
post_number: 5
blog_post: 2026-06-30 - From Kustomize to Helm
generated: 2026-07-27T20:08:38.664449
---

A Helm chart that can't render should never reach a cluster.
Two cheap CI jobs guarantee mine never does.

After migrating my deploy layer from Kustomize to Helm, the chart became a single point of failure. A broken template doesn't fail politely — it fails at deploy time, in the cluster, at the worst moment.

So the pipeline got two gates:

1. helm lint — catches structural and metadata mistakes.

2. A template smoke test — renders the chart twice, once with default values, once with the dev values file. If either render fails, the pipeline stops.

Then the e2e suite became a two-phase deploy that mirrors production:

Phase 1: dev infrastructure via Kustomize
kubectl apply -k k8s/manifests/dev

Phase 2: the app via Helm
helm upgrade --install asp k8s/charts/asp -f values-dev.yaml

That split isn't arbitrary. It's exactly how my homelab consumes the platform: infrastructure from one mechanism, the app from a Flux HelmRelease pointing at the chart in the app repo. The e2e suite rehearses the real deployment path on every push.

Total cost: a few seconds of CI time.

What it buys: the chart stays deployable at HEAD, forever, without anyone remembering to check.

The best deploy safety nets are the boring ones that run on every commit.

#cicd #helm #kubernetes #devops #gitops
