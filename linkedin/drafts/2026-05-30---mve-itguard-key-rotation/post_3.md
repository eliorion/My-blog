---
angle: behind-the-scenes
post_number: 3
blog_post: 2026-05-30 - mve-itguard-key-rotation
generated: 2026-07-28T16:38:46.772545
---

My CI pipeline commits to main. That commit triggers CI. Which commits to main. Which triggers CI...
Two words saved me from an infinite loop: [skip ci]

Context: I automated AGE encryption key rotation inside my deploy pipeline. When it detects a new key, it re-encrypts all SOPS files and commits them back to main.

But a commit to main triggers the deploy workflow. Which would run rotation again. Which would commit again. Forever.

GitHub Actions has a built-in escape hatch: put [skip ci] in the commit message and no workflows run for that commit.

git commit -m "fix(security): rotate AGE encryption key [skip ci]"

Small details like this are where automation projects live or die. The re-encryption logic took an afternoon. The edge cases took longer:

- loop prevention on the commit-back
- atomic re-encryption (a failed file stays untouched, pipeline fails, next push retries)
- a self-referential file: the private key itself, encrypted with its own public key, which needs special handling during rotation
- temp file cleanup on every exit path, error or not

That's the unglamorous truth about CI automation: the feature is 20% of the work.

Making it safe to run unattended is the other 80%.

#githubactions #cicd #automation #devops
