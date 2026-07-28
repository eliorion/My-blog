---
angle: hot take
post_number: 1
blog_post: 2026-05-28 - mve-itguard-runners
generated: 2026-07-28T16:37:35.482569
---

Your self-hosted CI runner is a remote shell into your infrastructure.
Most setups treat it like a convenience feature.

GitHub-hosted runners are disposable VMs. They vanish after each job and never touch your network.

Self-hosted runners are different. They live on your hardware, connected to GitHub, waiting to execute whatever a workflow sends them.

Mine run on the production server of my homelab. The deploy runner needs Docker access to do its job — and a process that can talk to Docker can read any container's environment variables, mount any volume, stop any service, run any image.

The answer isn't "don't use self-hosted runners."
The answer is constraint:

— The runner that executes pull requests gets no Docker, no secrets, no production access. Untrusted code lands in a box with nothing in it.

— The runner that deploys talks to Docker only through a filtering proxy that blocks exec, build, and most of the API.

— The runner that rotates secrets gets root — for exactly one directory, and nothing else.

If pull requests from strangers execute on the same box that runs production, with the same permissions, you haven't automated your deployment.

You've built a backdoor and called it CI.

#devops #cicd #security #selfhosted #githubactions
