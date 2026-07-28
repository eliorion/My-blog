---
angle: hot take
post_number: 1
blog_post: 2026-05-25 - mve-itguard-gitops
generated: 2026-07-27T19:10:18.018764
published: 2026-07-28T12:34:15.698191  # posted manually
---

Everyone says GitOps needs Kubernetes.
Mine runs on Docker Compose and a single server.

GitOps is a principle, not a tool:

Git is the single source of truth.
No change happens outside of Git.
Automation applies what Git declares.

For my home security system, a full Kubernetes cluster would be overengineering. A handful of services, one machine, and operational simplicity matters more than scalability.

So I built the same guarantees with Docker Compose + GitHub Actions:

- Every change goes through a pull request
- CI lints and validates before anything ships
- The deploy pipeline triggers only when CI passes on main
- docker compose up -d --remove-orphans --pull always reconciles the server to match the repo

No ArgoCD. No FluxCD. No cluster.

Same outcome: the server's running state is always a consequence of what the repository declares.

If your workload fits on one machine, you don't need Kubernetes complexity to get GitOps discipline.

Keep the principle. Skip the platform.

#gitops #docker #devops #homelab
