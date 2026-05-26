---
angle: personal story
post_number: 1
blog_post: 2026-02-23 - Why learn linux before containerisation
generated: 2026-05-26T14:21:55.373488
---

My Mac had plenty of free RAM. My container still got killed by the Linux kernel.
3 days of debugging. Wrong layer the whole time.

I switched from Docker Desktop to Rancher Desktop to experiment with K3s and get closer to real production environments. Everything in the course worked perfectly.

Then I went back to my homelab devcontainer. It failed.
My dotfiles bootstrap container failed too.

I reviewed scripts. Inspected logs. Questioned my Chezmoi config. Nothing.

Eventually I found it: the OOM killer was terminating my process mid-run.

But why? My Mac had memory to spare.

Here's what I missed:

On macOS, containers don't run on the host kernel. Both Docker Desktop and Rancher Desktop use a Linux VM under the hood. But Rancher Desktop makes resource allocation explicit — and mine was set to 2 GB.

Inside that 2 GB VM I had:
- A K3s cluster
- Kubernetes experiment containers
- My devcontainer environments

All sharing the same 2 GB limit.

The kernel ran out of memory. It killed my process.
The script was fine. The infrastructure was the problem.

Once I deleted the K3s cluster, everything worked.

The real lesson: when you change tools or runtimes, the failure domain changes too. I was debugging at the application layer when the problem lived at the virtualization layer.

That mismatch cost me 3 days.

Lesson: always identify your resource boundaries before diving into code.

#linux #devops #containers #debugging #kubernetes
