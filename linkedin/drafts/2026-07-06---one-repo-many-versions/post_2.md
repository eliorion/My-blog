---
angle: personal story
post_number: 2
blog_post: 2026-07-06 - One repo many versions
generated: 2026-07-27T21:25:04.400859
---

I shipped the same bug twice in one week.

The second time was the useful one.

release-please starts every new package at 1.0.0. For a homelab platform that's honestly pre-1.0, the documented workaround is a bootstrap pin:

"release-as": "0.1.0"

With one instruction: remove it right after 0.1.0 ships. It's a one-shot device. Left in place, it freezes the version forever.

I left it in place. Twice.

First time: a migrations component quietly stopped releasing. No error, no red pipeline. Just a version that never moved while its twin advanced to 0.4.0. Everything looked green.

Second time, one day later: seven components carried the same latent pin. A fix merged, release-please computed 0.1.0 again, and tried to re-create an existing tag. "Validation Failed ... tag_name already_exists."

Same root cause, opposite symptoms. One fails silently, the other fails loudly.

The first time was a mistake. The second time was a diagnosis: the process itself had a gap.

A step that lives only in documentation — "remove this after it fires" — is a step that will be skipped, because nothing fails at the moment you forget it.

The real fix wasn't removing the pins. It was the rule behind it: if a config value must be removed after it fires, its removal has to be part of the same motion that ships it. Not a documented intention.

#devops #automation #cicd #postmortem #homelab
