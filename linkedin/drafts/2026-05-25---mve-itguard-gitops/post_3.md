---
angle: key lesson (security)
post_number: 3
blog_post: 2026-05-25 - mve-itguard-gitops
generated: 2026-07-27T19:10:18.019506
---

A stranger's pull request could have owned my production server.
Here's the isolation that prevents it.

My GitHub Actions runners are self-hosted, living on the production box itself. They have to be — GitHub-hosted runners can't reach a home server on a private network.

That's a scary setup. Any pull request can execute arbitrary code in CI. If that runner can talk to Docker, it can read secrets, inspect containers, touch production services.

So the runners are split:

runner-ci — lint and validation only. No Docker socket. No path to production. It can check out code and run linters. Nothing more.

runner-deploy — deployments only. It runs after CI passes on main, and it never touches the Docker socket directly. It goes through a socket proxy that allows exactly the API surface docker compose needs: containers, images, networks, volumes, info, ping.

Untrusted code gets a sandbox.
Trusted deploys get a narrow, proxied path.

If your self-hosted runner has direct Docker socket access on the same machine as production, that's not a pipeline. That's a backdoor waiting for its first PR.

#devsecops #githubactions #docker #cicd #security
