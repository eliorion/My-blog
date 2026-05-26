---
angle: behind-the-scenes
post_number: 4
blog_post: 2026-03-27 - Refactoring my blog
generated: 2026-05-26T14:25:59.673623
---

Creating a new blog post now takes one command.
Getting there required rethinking the entire project layout.

The command:
hugo new content -k default "posts/2026-03-27 - Refactoring my blog/index.md" -s blog

One line. Folder created. File pre-filled from template. Ready to write.

But that only works when the structure underneath is clean.

Before the refactor, Hugo files were mixed into the repo root. No clear separation between the site, future translation work, and anything else I might add later.

After:
/blog → Hugo site
/translation → future i18n (not implemented yet, but has a home)
/... → space for anything new without polluting root

This sounds like a small thing. It's not.

When the structure is messy, every new addition is a decision. When it's clean, the path is obvious.

Good structure makes good tooling possible. Good tooling makes writing frictionless.

#Hugo #StaticSite #DevExperience #Blogging #SideProjects
