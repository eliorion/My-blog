---
angle: personal story
post_number: 1
blog_post: 2026-03-27 - Refactoring my blog
generated: 2026-05-26T14:25:59.672027
---

I spent weeks building a CI/CD pipeline I was proud of.
Then I deleted all of it.

My blog pipeline was doing a lot:
- Auto-merge dev into main
- Call a Hugging Face LLM to translate posts
- Build and deploy to GitHub Pages

The problem? I was building for imaginary scale.

I'm the only contributor. No team. No multilingual audience yet.

So I rebuilt it as:
1. Push to main
2. GitHub Actions builds the site
3. GitHub Actions deploys it

That's it.

The pipeline was serving my ego, not my project.

On personal projects, complexity is a trap. It feels like progress. It isn't.

The real progress was stripping it down to what I actually need — and shipping posts faster because of it.

#CICD #SideProjects #DevOps #Hugo
