---
name: preview-blog
description: Serve the Hugo blog locally and screenshot the rendered pages (home, posts, archives, search, about, tags) at desktop and mobile widths, then view the PNGs. Use when asked to preview the blog, screenshot the site, see the rendered blog, check how a blog change looks, or view the end product of blog/.
---

# Preview the blog (visual screenshots)

Produces real PNG screenshots of the live-rendered site so the visual end product can be
inspected — not just the HTML.

## First-time setup (once per machine)

```bash
cd .claude/skills/preview-blog
npm install
npx playwright install chromium   # ~150MB, one time
```

## Run

```bash
cd .claude/skills/preview-blog
node shoot.mjs
```

This starts `hugo server -s blog` on port 1313 (drafts included, `-D`), waits for it to be
ready, screenshots the key pages, then stops the server. Output lands in
`.claude/skills/preview-blog/screenshots/`:

- `home-desktop.png`, `home-mobile.png`
- `posts-desktop.png`, `archives-desktop.png`, `search-desktop.png`
- `about-desktop.png`, `tags-desktop.png`

## View

`Read` the PNG files in `screenshots/` to see the rendered site. A page that fails to load
is skipped with a warning rather than aborting the run.

## Notes

- Uses `--baseURL http://localhost:1313/` so internal links resolve locally (the production
  baseURL has a `/My-blog` path that would 404 on the dev server).
- Hugo version is pinned by the repo `mise.toml`.
- `screenshots/` and `node_modules/` are gitignored.
