---
angle: hot take
post_number: 1
blog_post: 2026-05-25 - mve-itguard-gitops
generated: 2026-05-26T14:29:18.928589
---

You don't need Kubernetes to do GitOps.
Docker Compose + GitHub Actions is enough.

The GitOps principle is simple:
— Git is the single source of truth
— No change happens outside of Git
— Automation applies what Git declares

That's it. No mention of Kubernetes, FluxCD, or ArgoCD.

I run a home security system — cameras, automations, sensors — on a single server. A full Kubernetes cluster would be overengineering. Docker Compose fits the workload.

So I applied the GitOps principle without the ecosystem:
→ Every config change goes through a pull request
→ CI validates before merge
→ GitHub Actions deploys on merge to main
→ The server's running state always reflects what's in the repo

No manual deployments. No "quick fixes" pushed directly. No configuration drift.

The workflow:
1. Edit config locally
2. Open PR → CI runs automatically
3. Merge → deploy triggers within seconds
4. Server updates without touching it

The tooling is simpler. The principle is identical.

If you've been thinking GitOps is out of reach without Kubernetes — it isn't.

#gitops #docker #homelab #cicd #devops
