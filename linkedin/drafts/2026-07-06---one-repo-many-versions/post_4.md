---
angle: key lesson
post_number: 4
blog_post: 2026-07-06 - One repo many versions
generated: 2026-07-27T21:25:04.401770
---

Release automation doesn't fail at setup time.

It fails weeks later, in the parts that looked done.

I run per-component releases in a monorepo with release-please: a dozen components, each with its own version, changelog, tag, and image build. The setup worked on day one. Then it broke twice, and both failures taught me more than the setup did.

Failure one: release PRs blocked by our own lockfile check, because the version bump invalidated a generated file the automation didn't know about.

Failure two: a bootstrap config value documented as "remove after first release" that I left in place. Twice. Once it silently stopped a component from releasing. Once it crashed on a tag collision.

Two rules came out of this:

1. Whatever the version bump invalidates, the automation must regenerate. A release PR that fails its own repo's gates is automation fighting itself.

2. One-shot configuration is a loaded trap. If a value must be removed after it fires, the removal has to ship in the same motion — not sit in the docs as an intention.

The first failure teaches you the trap exists.

The second proves it was never about luck.

#devops #automation #monorepo #cicd #lessonslearned
