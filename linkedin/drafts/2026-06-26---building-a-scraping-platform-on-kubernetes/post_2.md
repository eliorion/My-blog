---
angle: technical deep-dive
post_number: 2
blog_post: 2026-06-26 - Building a scraping platform on Kubernetes
generated: 2026-07-27T20:04:57.616951
---

Cloudflare blocks naive scrapers. Rate limits ban greedy ones. Here's how my platform handles both.

Two mechanisms, both boring on purpose.

1. Multi-proxy lanes.

Instead of routing every worker through one IP, my Helm chart generates per-pod scraper "lanes" from a matrix of sites × proxies. Each lane is a worker bound to a specific egress proxy, so load spreads across many source IPs.

The lane list is data in the Helm values. Adding a proxy or a site is a values change, not a code change.

2. FlareSolverr for Cloudflare.

Sites behind Cloudflare's challenge page get a dedicated lane that routes through FlareSolverr, which solves the challenge and returns a usable session.

It's heavier than a plain HTTP fetch, so it only runs where it's actually needed.

On top of both: adaptive pacing. The scraper slows itself down instead of hammering a site into a ban.

The pattern underneath it all: generate infrastructure from data. With a dozen services, several of them produced from a list, templating manifests from values beats copy-pasting YAML every single time.

#kubernetes #helm #webscraping #devops
