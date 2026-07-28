---
angle: personal story
post_number: 1
blog_post: 2026-07-10 - CI runners inside the cluster
generated: 2026-07-27T21:27:15.736116
---

My CI runners couldn't reach my cluster.
So I moved them inside it.

My scraping platform's pipeline doesn't just build images. It deploys against a disposable cluster, runs end-to-end tests, and feeds releases into the real cluster through GitOps. All of it behind my private network.

GitHub-hosted runners can't reach any of that. And I'm not exposing my cluster so they can.

The standard answer: self-hosted runners.
The standard question: where?

A separate VM would mean another hand-managed host — exactly the thing my homelab has been eliminating.

So the runners now run where everything else runs: on the cluster itself, as Kubernetes pods, managed by Actions Runner Controller (ARC), deployed by Flux like any other workload.

The details that make it work:

• Scale sets go from 0 to 2 runners — nothing queued, nothing running, RAM goes back to real workloads
• Every job gets a fresh pod — whatever it does to its environment dies with it
• Auth via a PAT in a SOPS-encrypted secret, like every other credential in the repo

The part nobody warns you about: once CI shares a cluster with real workloads, capacity planning stops being someone else's problem.

That turned out to be the most interesting part.

#kubernetes #githubactions #homelab #gitops #devops
