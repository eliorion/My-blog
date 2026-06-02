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

To **see** the rendered site, use the `preview-blog` skill (`.claude/skills/preview-blog/`):
it serves the blog and screenshots key pages at desktop/mobile widths into
`screenshots/` for visual inspection.

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

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
