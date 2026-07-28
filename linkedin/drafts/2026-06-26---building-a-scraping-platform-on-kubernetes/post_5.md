---
angle: behind-the-scenes
post_number: 5
blog_post: 2026-06-26 - Building a scraping platform on Kubernetes
generated: 2026-07-27T20:04:57.618474
---

My front end was Flutter. Then React + Vite. Then Next.js. Three rewrites — and the product barely changed.

The public webapp of my scraping platform went through more iterations than any other service.

Version 1: Flutter web with a Keycloak-authenticated backend.
Version 2: React + Vite SPA.
Version 3: Next.js, where it finally settled — multilingual UI, advanced search, a multi-step buying guide.

Meanwhile the backend around it barely moved. Workers scraped. The orchestrator assigned URLs. Postgres stored rows.

The takeaway isn't "Next.js is better." It's that I over-committed early on decisions I didn't have to make yet.

The front end changed shape several times before the product did. Every early architectural bet on it was placed with the least information I'd ever have.

Now I keep the expensive commitments stable — data model, migrations, release process — and let the cheap ones stay disposable as long as possible.

Rewrites aren't failures. Premature certainty is.

#nextjs #softwarearchitecture #webdev #buildinpublic
