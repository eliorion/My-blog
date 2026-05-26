---
angle: personal story
post_number: 1
blog_post: 2026-03-24 - Containerise Python application
generated: 2026-05-26T14:25:07.649375
---

My git history looked like a crime scene.
"fix stuff", "changes", "final version" — I was the main culprit.

While building a containerized Python app for a DevSecOps course, I had to face this problem seriously.

The solution: Conventional Commits.

Instead of "bug fix login":
fix(auth): resolve login crash when password is empty

Instead of "update code":
feat(ui): add loading spinner to login button

One line. You know what changed. You know where. You know why.

But knowing the standard doesn't mean people follow it.

That's where Commitizen comes in. It hooks into git and guides (or forces) you to write proper commit messages — before the commit even lands.

Set it up once via a git hook. Every commit after that is structured, searchable, and meaningful.

The mindset shift: commit messages aren't for you right now. They're for you (or someone else) at 2am six months later, trying to understand why production broke.

Invest 10 minutes in the setup. Save hours of confusion later.

#git #devops #conventionalcommits #bestpractices
