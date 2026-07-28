---
angle: key lesson
post_number: 3
blog_post: 2026-07-10 - CI runners inside the cluster
generated: 2026-07-27T21:27:15.737260
---

Talos rejected my CI runner pods.
Best thing that happened to my homelab that week.

Context: GitHub Actions runners need Docker-in-Docker to build images. And dind needs privileged mode to run its own Docker daemon.

Talos ships with Pod Security Admission enforced — and dind is exactly the kind of thing PSA exists to stop.

So my runner pods bounced. Rejected until I explicitly labeled the arc-runners namespace as privileged.

Here's why I like this friction:

On K3s, those runners would have silently gotten whatever privileges they asked for. No questions. No trace.

On Talos, the privilege is visible in Git:

• One labeled namespace
• Scoped to exactly the workload that needs it
• The rest of the cluster still restricted

Security that forces you to declare your exceptions beats security that grants them silently.

The rejection wasn't an obstacle. It was the system working.

#kubernetes #talos #security #devsecops #homelab
