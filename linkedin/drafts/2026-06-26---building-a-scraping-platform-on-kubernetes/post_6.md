---
angle: tool spotlight
post_number: 6
blog_post: 2026-06-26 - Building a scraping platform on Kubernetes
generated: 2026-07-27T20:04:57.618948
---

One repo. Seven services. An independent version for each. release-please made it work — after a fight.

My scraping platform is a monorepo: workers, orchestrator, admin UI, analyzer, webapp, a football-stats pipeline, a Jupyter sandbox.

Releasing them together would be wrong. A webapp fix shouldn't bump the scraper's version and redeploy something that didn't change.

release-please gives each component its own version, changelog and image tag, driven by conventional commits.

But "install it and go" wasn't the reality. Making it behave took real tuning:

- Unpinning stale release-as values that froze components at 0.1.0
- Keeping uv.lock in sync on release PRs so builds match what ships
- Making sure a component only releases when it actually changes

Worth it. Now a merged PR produces exactly the releases it should — no more, no less — and every image tag traces back to a changelog entry.

If you run multiple services from one repo, per-component releases aren't a nice-to-have. They're what keeps the repo from becoming one giant lockstep deploy.

#releaseplease #monorepo #cicd #devops
