---
angle: technical deep-dive
post_number: 2
blog_post: 2026-02-26 - First GitOps implementation
generated: 2026-05-26T14:23:38.763011
---

kubectl apply is manual. FluxCD makes your cluster self-healing.
Here's how the reconciliation loop actually works.

FluxCD runs inside your Kubernetes cluster and watches a Git repository.

Every time you push a change to Git:

1. Flux detects the change
2. Builds Kubernetes manifests using Kustomize
3. Applies them to the cluster
4. Removes resources you deleted from Git

That last point matters.

With prune: true, Git is truly the source of truth. Nothing lives in the cluster that isn't declared in Git.

This mirrors how Kubernetes itself works — you declare desired state, the system converges to match it.

Flux extends that idea. Git becomes the declarative interface.

My repo structure:

apps/          → cluster applications
clusters/      → Flux bootstrap + Kustomization objects
infrastructure/ → ingress, cert-manager, etc.
monitoring/    → Prometheus, Grafana

Three Kustomization objects each point to a path. Flux reads it, runs kustomize build, applies the result.

The loop runs continuously. The cluster always matches Git.

Once you see it working, kubectl apply -f feels like a step backwards.

#FluxCD #GitOps #Kubernetes #DevOps #K3s
