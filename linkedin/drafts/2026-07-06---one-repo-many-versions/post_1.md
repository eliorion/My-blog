---
angle: hot take
post_number: 1
blog_post: 2026-07-06 - One repo many versions
generated: 2026-07-27T21:25:04.400180
---

One version number for a monorepo is a lie.

Here's why my repo has twelve of them.

My platform repo holds a dozen deployable components: scrapers, an orchestrator, admin UIs, a webapp, migration images.

One repo, because they form one platform and change together in review.

But one version? A webapp copy change shouldn't bump the scraper. A scraper fix shouldn't produce a new webapp image that differs by nothing.

So: release-please with per-component releases.

Each component gets:
- its own version
- its own changelog
- its own Git tag
- its own image build

release-please watches conventional commits, works out which components changed, and maintains a rolling release PR per component. Merging that PR tags the release and kicks off the image build.

The Git log becomes the release ledger:

feat(fbref): scrape past Cloudflare via a FlareSolverr solver
chore: release main
chore(chart): bump fbref image to fbref-scraper-v0.8.0 [skip ci]

Each component moves at its own pace. The Helm chart always points at real released images. Nobody hand-edits a version number anywhere.

Was it free? No. It broke twice in ways the docs didn't warn me about. But both failures taught me more than the setup did.

#monorepo #devops #cicd #releaseengineering #githubactions
