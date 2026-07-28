---
angle: key lesson
post_number: 3
blog_post: 2026-06-26 - Building a scraping platform on Kubernetes
generated: 2026-07-27T20:04:57.617563
---

I lost a database volume in my cluster. The schema rebuilt itself. That wasn't luck.

Every schema change in my scraping platform ships as a Flyway migration, packaged in its own image, applied the same way in every environment.

No hand-run SQL. No drift between staging and production. No stale init.sql that only works on a fresh install from six months ago.

So when the volume died, recovery was: fresh Postgres, run the migration tier, done. The database healed itself because the schema was versioned code, not a precious artifact someone once set up by hand.

The lesson I keep relearning: make state reproducible, not precious.

If restoring your database schema requires remembering what you did, you don't have a schema — you have an archaeology site.

Versioned, idempotent migrations felt like ceremony when the project was a single container. They paid for themselves the first time something broke.

#postgres #flyway #devops #kubernetes
