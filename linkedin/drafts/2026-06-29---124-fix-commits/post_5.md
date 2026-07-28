---
angle: key lesson
post_number: 5
blog_post: 2026-06-29 - 124 fix commits
generated: 2026-07-27T20:07:09.961065
---

You don't stop breaking your cluster.

You start breaking more interesting things.

I hoped the fix-commit storms in my homelab would end once I learned YAML. They didn't — they changed nature.

February: 29 commits in one day. Indentation errors. An '=' where a ':' should be. ConfigMap values that needed quotes. A Service selector matching zero pods.

June: 19 commits in one day. But now they're about SOPS-encrypted secrets, Cloudflare tunnel tokens, and credentials that can only be verified against the live cluster.

Same push-driven feedback loop. Completely different layer.

That's what progress actually looks like in infrastructure. It's not that failures stop — it's that they move up the stack.

Compare two commits from the same repo, three months apart:

'fix: intentation issue'

vs

'fix(asp-db): restore from R2 archive after volume loss' — with a full body explaining the root cause and a reference to the troubleshooting doc.

Same repository. Same author. The difference isn't fewer mistakes. It's better mistakes, and better records of them.

If everything you touch works on the first try, you're not learning. You're repeating.

#kubernetes #devops #gitops #infrastructure #learning
