# Blog repo — Hugo + PaperMod

## Stack

- Hugo 0.153.0 (local) / 0.158.0 (CI), theme: PaperMod
- Deploy: GitHub Actions → GitHub Pages (`https://eliorion.github.io/My-blog`)
- Tooling: mise, pre-commit, commitizen

## Commands

```bash
hugo server -s blog          # dev server
hugo build -s blog           # production build → blog/public/
pre-commit run --all-files   # lint
```

## Post location

`blog/content/11 - Posts/YYYY-MM-DD - Title/`

Each post = folder with:
- `index.md` — content
- `cover.svg` — optional cover image

## Frontmatter

```yaml
---
title: ""
date: YYYY-MM-DDTHH:MM:SS+02:00
draft: false
topics: []       # Homelab | Security | DevOps | ...
tags: []         # lowercase, specific tech
projects: []     # project slug
categories: []   # IT | Homelab | ...
weight: 10       # lower = higher in list
cover:
  image: cover.svg
  alt: ""
  caption: ""
  relative: true
  hidden: true
  hiddenInList: true
  hiddenInSingle: false
---
```

## Taxonomies

`categories` / `tags` / `topics` / `projects` — all defined in `blog/hugo.toml`

Permalinks: `/posts/:slug/`

## Commits

Commitizen enforced via pre-commit hook (`commit-msg` stage). Use conventional commits: `feat(post): ...`, `fix(posts): ...`

## Structure

```
blog/
  content/11 - Posts/   ← all posts
  archetypes/default.md ← new post template
  hugo.toml             ← site config
  themes/PaperMod/      ← submodule
scripts/
  setup_project         ← runs on mise enter
.github/workflows/hugo.yaml ← CI/CD
```
