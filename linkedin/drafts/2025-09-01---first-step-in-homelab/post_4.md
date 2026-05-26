---
angle: hot take
post_number: 4
blog_post: 2025-09-01 - First-step-in-homelab
generated: 2026-05-26T14:15:18.990316
---

Most engineers who use Kubernetes daily have never actually run their own cluster.
And it shows.

They provision infra through Terraform.
They deploy through CI/CD.
They never touch a node.

Fine for shipping. Terrible for understanding.

When production breaks at 2am — do you actually know what's happening inside the cluster?

I didn't. So I built a homelab.

300€. One mini PC. Proxmox + Talos Linux + a few VMs.

Now I understand node pressure, pod eviction, control plane failures — because I've caused all of them myself.

You don't learn Kubernetes by using it.
You learn it by breaking it.

Build the homelab. Break the cluster. Fix it. Repeat.

#Kubernetes #Homelab #EngineeringCulture #Infrastructure
