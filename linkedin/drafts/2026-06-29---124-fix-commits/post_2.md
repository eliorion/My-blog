---
angle: technical deep-dive
post_number: 2
blog_post: 2026-06-29 - 124 fix commits
generated: 2026-07-27T20:07:09.960655
---

A Kubernetes Service with a wrong label selector doesn't throw an error.

It just quietly routes traffic to nothing.

I learned this during a 29-commit day deploying GLPI with a MariaDB backend. Here's what that day taught me, one one-line fix at a time:

1. A Service finds pods by label selector. If the selector matches nothing, the Service still exists — the endpoints list is just empty. No warning. No error. Traffic goes nowhere.

2. A named targetPort must match the port NAME in the pod spec, not the number. 'http' and '8080' are not interchangeable.

3. A Deployment with the wrong containerPort will happily report Running and still serve nothing.

4. A PVC name in a Deployment's volume block has to match the actual PVC — and the only symptom is a pod stuck in Pending.

None of this is exotic. It's all in the docs.

But there's a difference between reading 'Services select pods via labels' and spending an evening staring at an empty endpoints list, wondering which layer is lying to you.

You only internalize this stuff by getting it wrong with a real scheduler watching.

#kubernetes #devops #homelab #sre
