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

## SVG images (covers, diagrams)

Never finish an SVG from the markup alone — render it and look at it:

```bash
node scripts/svg-preview.mjs path/to/cover.svg   # → cover.preview.png + lint
node scripts/svg-fix.mjs path/to/cover.svg       # auto-fix chip rows + long captions
```

Lints text spilling off canvas, text overflowing its chip/badge rect, overlapping
labels, and font stacks that resolve to nothing; then `Read` the PNG to judge the
design itself. Enforced on staged `.svg` by pre-commit. Only `DejaVu Sans`,
`DejaVu Sans Mono`, `DejaVu Serif` are installed — name one of those first in every
`font-family`. `*.preview.png` is gitignored.

Both CLI tools are thin wrappers. The algorithms live in
`svg-render/lib/svg-audit.mjs` (the lint) and `svg-render/lib/svg-repair.mjs`
(the fix); the service imports the same two files — edit them once, not per
caller. They sit under `svg-render/` so that changing either counts as changing
the image, which is what release-please watches.

The homelab n8n workflow `Blog - Draft and PR` carries the same repair as a
`Fix Cover SVG` Code node between `Build Post Files` and the commit — same algorithm,
but with DejaVu metrics baked in, since n8n has no browser to measure with. It reports
what it changed (and what it could not fix) in the PR body and in Telegram. Change one
side and the other drifts. `Blog - Cover Review` does not have this problem: it calls
`svg-render` instead.

## Changing a cover from Telegram

`Blog - Cover Review` (n8n, `LE945sdy1heKIbJQ`) is a chat loop over a draft's
`cover.svg`:

| You send | What happens |
| --- | --- |
| `/cover` | newest open `post/*` PR, its cover rendered back as a photo |
| anything else | ai-gateway redraws the cover with that change, `svg-render` repairs and lints it, n8n commits to the draft branch and replies with the new PNG |
| `/cover undo` | re-commits the previous version of the cover — read from git history, not a stack |
| `/cover done` | deletes the session row, links the PR |

Session state is one row per chat in the `cover_review` Data Table. Every proposal
is a real commit on the draft branch, so the PR always shows the current cover.

**It runs on its own bot.** Telegram allows one webhook per bot token, and the
`LinkedIn` workflow already holds a Telegram Trigger on the main bot — activating
a second one against the same token steals the webhook and the LinkedIn approval
loop goes quiet with no error. That bot also already owns `/review` and treats
bare text as "rewrite this post's commentary", which is why the cover commands are
`/cover`, not `/review`. Two bots, two webhooks, no overlap.

`svg-render/` is the service behind it — Playwright over HTTP, `/fix` and `/render`.
It runs in the cluster (`k8s/svg-render/`). See `svg-render/README.md`.

## Releases

`release-please` (`.github/workflows/release-please.yaml`, config in
`release-please-config.json`) watches `svg-render/` and nothing else. Commits are
assigned by path, so posts and drafts never open a release PR. Merging one tags
`svg-render-vX.Y.Z`, which is the only thing that runs
`.github/workflows/svg-render-image.yaml`: build, **Trivy gate on CRITICAL + HIGH**,
then push to `ghcr.io/eliorion/my-blog-svg-render`. Nothing unscanned reaches the
registry. Accepted CVEs live in `.trivyignore` with a reason and a date.

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
