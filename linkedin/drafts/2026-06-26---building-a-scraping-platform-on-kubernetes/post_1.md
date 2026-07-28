---
angle: personal story
post_number: 1
blog_post: 2026-06-26 - Building a scraping platform on Kubernetes
generated: 2026-07-27T20:04:57.616249
---

I didn't need the data. I needed a system big enough to break in interesting ways.

My homelab exists to learn Kubernetes and DevSecOps properly. But you can't learn operations by running three self-hosted apps that never change.

So I built asp: a web-scraping platform that collects listings and football stats, stores everything in Postgres, and serves it through a web app.

It started as one scraping container. It grew into seven services:

- workers that fetch and parse pages
- an orchestrator that assigns URLs and reclaims work from dead pods
- an admin dashboard for the queue
- an analyzer that turns raw rows into queryable data
- a Next.js front end
- a dedicated football-stats pipeline
- an in-cluster JupyterLab for ad-hoc analysis

All of it packaged in one Helm chart, deployed through GitOps, with per-component releases and versioned database migrations.

The scraping was never the point. Releases, rollbacks, migrations, caching — those stop being abstract when you run something with real moving parts.

If you're learning Kubernetes: build a workload complicated enough that the operational side actually matters. That's where the learning is.

#kubernetes #homelab #devops #selfhosted
