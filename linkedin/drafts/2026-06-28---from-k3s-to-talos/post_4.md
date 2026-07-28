---
angle: hot take
post_number: 4
blog_post: 2026-06-28 - From K3s to Talos
generated: 2026-07-27T20:05:58.381033
---

Hot take: SSH access to your servers is a liability, not a feature.

My homelab ran on K3s for over a year. K3s was never the problem. The problem was underneath it: a general-purpose Linux VM that I installed by hand and had to patch, secure, and keep consistent forever.

Every package on that host was attack surface.
Every quick SSH fix was drift no Git repository knew about.

Meanwhile the cluster itself was fully GitOps: nothing reached it except through a Git repo. Declarative on top, hand-managed underneath. The contradiction bugged me.

So I switched to Talos Linux.

No SSH. No shell. No package manager. The entire OS is configured declaratively and managed through an API. It does exactly one thing: run Kubernetes.

At first that sounds terrifying — how do you debug without a shell? But it removes a whole category of problem: the slow, invisible drift of a hand-managed host. You can't make an undocumented change if there's no shell to make it in.

If Git is the source of truth for your cluster, the nodes underneath should be declarative too.

Otherwise you've built a glass house on a foundation of 'I think I configured that once.'

#talos #kubernetes #gitops #infrastructure #devops
