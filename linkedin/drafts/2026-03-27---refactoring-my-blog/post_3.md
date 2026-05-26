---
angle: hot take
post_number: 3
blog_post: 2026-03-27 - Refactoring my blog
generated: 2026-05-26T14:25:59.673369
---

Solo project with automated translation, branch strategy, and multi-stage pipeline.
Yeah, that was me.

I built a CI/CD setup for my personal blog that would've made sense for a team of 10.

There was a dev branch. A merge job. A Hugging Face LLM translating my posts. A separate deploy stage.

For a blog. Written by one person.

Here's what I think happens: we learn something cool at work, and we drag it into personal projects without asking whether it fits.

The refactor was humbling. I removed the translation entirely (nobody's asking for French posts yet). Killed the branch strategy. Kept build → deploy.

Two jobs. Done.

If you're maintaining infrastructure for features nobody uses yet, that's a signal.

Ship the post, not the pipeline.

#DevOps #CICD #SoftwareEngineering #SideProjects
