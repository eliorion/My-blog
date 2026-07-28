---
angle: key lesson
post_number: 5
blog_post: 2026-07-04 - Caching everything through Nexus
generated: 2026-07-27T21:23:58.728277
---

A cache is a claim about the world.
And claims go stale.

Four CI fixes in one week taught me this. Each one was a different lie:

1. A health probe claimed my PyPI mirror was down. It was healthy — the probe checked a path the mirror 404s by design. CI silently paid for a mirror it never used.

2. A fallback cache claimed to be a cache. Measured throughput: 140 KB/s, while the primary moved at 3.6 MB/s from the same pods. That's not a cache, that's an anchor.

3. A cached Docker layer claimed to upgrade packages. BuildKit keys layers on RUN text + parent layer only — the upgrade hadn't executed in weeks. A CVE gate caught it.

4. A scanner's DB download claimed to be flaky. Really, it was the one artifact class not routed through the mirror. Consistency was the fix.

The countermeasures all have the same shape — verify the claim:
— probe a real package path, not a theoretical one
— measure actual throughput instead of assuming
— force cached layers to re-run on a schedule you control

Self-hosting CI means owning your supply chain. I thought that meant hosting a mirror.

It actually means becoming the person who checks that the mirror, the fallback, and the cache are each telling the truth.

#devops #cicd #platformengineering #selfhosted #supplychain
