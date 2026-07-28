---
angle: tool spotlight
post_number: 5
blog_post: 2026-07-06 - One repo many versions
generated: 2026-07-27T21:25:04.402180
---

Most days, I never think about version numbers.

That's the whole point of this setup.

My platform repo has a dozen deployable components: scrapers, an orchestrator, admin UIs, a webapp, migration images, a JupyterLab image.

release-please handles versioning for all of them, per component:

1. I merge a fix with a conventional commit, like feat(fbref): scrape past Cloudflare via a FlareSolverr solver

2. release-please works out which component changed and updates that component's rolling release PR

3. Merging the release PR tags the release and kicks off the image build

4. A bump-chart job rewrites that component's image tag in the Helm chart values with a [skip ci] commit

The Git log reads like a release ledger:

feat(fbref): scrape past Cloudflare via a FlareSolverr solver
chore: release main
chore(chart): bump fbref image to fbref-scraper-v0.8.0 [skip ci]

Each component moves at its own pace. The chart always points at real released images. No hand-edited versions anywhere.

Fair warning: it's not free. It broke for me twice — once fighting my own lockfile check, once from a leftover bootstrap pin. Both fixable, and fixed as a class, not an instance.

Worth it.

#releaseplease #githubactions #monorepo #homelab #devops
