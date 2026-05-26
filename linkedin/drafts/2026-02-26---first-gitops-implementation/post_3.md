---
angle: key lesson
post_number: 3
blog_post: 2026-02-26 - First GitOps implementation
generated: 2026-05-26T14:23:38.763394
---

Git is already your source of truth for code.
Why isn't it your source of truth for infrastructure?

That's the question GitOps answers.

With FluxCD, every piece of my cluster state lives in a Git repository:

→ App deployments
→ Infrastructure configs
→ Monitoring stack
→ Namespace definitions

Nothing gets applied manually. Nothing exists outside Git.

If it's not in Git, it doesn't exist in the cluster.

This has concrete consequences:

→ Rollbacks are just git revert
→ Audits are just git log
→ Collaboration is just a pull request

I'm learning this on a single-node homelab, but the principles scale directly to production.

The complexity of Kubernetes often hides a simple truth:
declarative infrastructure + version control = reproducibility.

GitOps isn't a tool. It's a discipline.
FluxCD just makes following that discipline automatic.

#GitOps #DevOps #Kubernetes #FluxCD #InfrastructureAsCode
