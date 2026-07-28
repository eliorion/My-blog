---
angle: hot take
post_number: 4
blog_post: 2026-06-26 - Building a scraping platform on Kubernetes
generated: 2026-07-27T20:04:57.618070
---

Scraping is the easy half of building a scraping platform. The hard half is everything around it.

Fetching pages and parsing HTML? A weekend.

What actually took months:

- Per-component releases, so a webapp change doesn't bump the scraper's version
- CI that builds every image, runs semgrep, trivy, syft and detect-secrets, then validates the whole stack on a disposable k3d cluster before anything touches the real one
- A Nexus mirror in front of Docker Hub, because a pipeline that dies on docker.io 429 rate limits isn't a pipeline
- Readiness probes and Helm test hooks so a bad release rolls back automatically
- An orchestrator that reclaims work from crashed pods instead of silently stranding it

None of this shows up in a demo. All of it decides whether the thing survives contact with reality.

My rule for the pipeline: zero drift between local and CI. Same lint, same scans, same build. A green pipeline has to mean the same thing everywhere, or it means nothing.

The features are the easy half. Operating them well is the product.

#cicd #devops #kubernetes #platformengineering
