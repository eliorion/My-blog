---
angle: key lesson
post_number: 3
blog_post: 2025-09-15 - Architecture-learning-project
generated: 2026-05-26T14:16:59.937710
---

Tutorials teach you Kubernetes concepts.
Breaking your own cluster teaches you Kubernetes.

Docs are great. But they skip the boring, critical parts:
— Who actually manages the network?
— How does the load balancer route traffic?
— How do you reach your cluster securely from outside?

Cloud providers hide all of this. That's their product. But it's your knowledge gap.

My solution: build a home lab that forces me to answer every question myself.

One physical machine. Proxmox hypervisor. Multiple VMs acting as separate servers.
Every network decision is mine. Every security boundary is mine to draw.

When something breaks, I can't open a support ticket. I have to understand it.

That's the fastest path I've found from 'I know what a pod is' to 'I understand why this cluster is misbehaving.'

If you're serious about Kubernetes: don't just use managed services.
Build something you actually have to manage.

#Kubernetes #Homelab #SelfHosted #LearningInPublic
