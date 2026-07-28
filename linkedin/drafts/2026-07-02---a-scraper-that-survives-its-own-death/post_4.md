---
angle: hot take
post_number: 4
blog_post: 2026-07-02 - A scraper that survives its own death
generated: 2026-07-27T21:22:52.308851
---

Hot take: if your scraper treats a rate limit like a crash, you're DDoSing yourself.

One site I scrape throttles clients at roughly 10 requests per minute. Cross the line and your IP lands in a temporary 429 jail.

My first version treated any block like a failure: burn an attempt on the URL, count it toward a failure streak, eventually restart the pod.

Every part of that response was wrong.

A jail isn't damage. It's weather. Here's what actually works:

1. Classify blocks properly. A 429 rate-limit jail and a Cloudflare challenge need OPPOSITE reactions. One means slow down. The other means your session is burned.

2. Pace adaptively. Start slow (~6 requests/min), creep faster after clean streaks, snap back to double spacing on any block. Each pod paces its own egress IP — because that IP is what the site is throttling.

3. On a jail: release the URL without burning an attempt, widen the pace, sleep a long cooldown.

4. Do NOT restart the browser session. The IP is throttled, not the session. Tearing down a healthy session to fix an IP-level problem just adds load at the worst possible moment.

The result: the scraper goes as fast as it safely can, and slows itself down before the site has to do it for you.

Respecting the throttle isn't just polite. It's faster.

#webscraping #ratelimiting #kubernetes #devops #softwareengineering
