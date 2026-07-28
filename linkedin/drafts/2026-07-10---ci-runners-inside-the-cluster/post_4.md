---
angle: tool spotlight
post_number: 4
blog_post: 2026-07-10 - CI runners inside the cluster
generated: 2026-07-27T21:27:15.737742
---

The most underrated upgrade in my CI pipeline this year:
a package cache one network hop from my runners.

When my GitHub Actions runners moved inside my Kubernetes cluster, it unlocked a side effect I hadn't planned for.

The dependency cache could live next door.

I deployed Nexus with a pypi-proxy repository and anonymous read access — all provisioned declaratively by the chart's config job. If Nexus gets rebuilt, it configures itself. No clickops.

Now runner pods pull Python packages from Nexus instead of PyPI:

• Faster — one hop inside the cluster instead of a round trip to the internet
• Immune to upstream rate limits
• One less way for CI to fail for reasons that have nothing to do with the code

That last point is the real win.

Every external dependency in your pipeline is a flake generator. Every one you pull inside your network is a whole category of red builds that just... disappears.

Small change. Boring tool. Disproportionate payoff.

#cicd #nexus #devops #kubernetes #python
