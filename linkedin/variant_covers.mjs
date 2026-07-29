// Build post_N.png variant covers for LinkedIn drafts.
// Base = the draft's cover.svg (common theme per blog post), plus a bottom
// badge strip showing the variant's angle and index (distinct per variant).
// Skips published/skipped posts and existing PNGs. Zero AI tokens.
//
// Usage: node linkedin/variant_covers.mjs   (from repo root or anywhere)
import { readdirSync, readFileSync, existsSync, writeFileSync, rmSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve, join } from "node:path";
import { tmpdir } from "node:os";

const HERE = dirname(fileURLToPath(import.meta.url));
const DRAFTS = resolve(HERE, "drafts");
const { chromium } = await import(
  resolve(HERE, "../.claude/skills/preview-blog/node_modules/playwright/index.mjs")
);

// Angle → accent color (stable hash so same angle = same color everywhere)
const PALETTE = ["#4dabf7", "#51cf66", "#ffd43b", "#ff922b", "#cc5de8", "#20c997", "#ff6b6b", "#74c0fc"];
const accent = (s) => PALETTE[[...s].reduce((a, c) => a + c.charCodeAt(0), 0) % PALETTE.length];

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 800, height: 360 }, deviceScaleFactor: 2 });

let made = 0;
for (const dir of readdirSync(DRAFTS).sort()) {
  const dpath = join(DRAFTS, dir);
  const cover = join(dpath, "cover.svg");
  if (!existsSync(cover)) continue;

  const posts = readdirSync(dpath).filter((f) => /^post_\d+\.md$/.test(f)).sort();
  for (const post of posts) {
    const md = readFileSync(join(dpath, post), "utf-8");
    const fm = md.split("---")[1] ?? "";
    if (/^published:/m.test(fm)) continue; // already out or skipped
    const png = join(dpath, post.replace(".md", ".png"));
    if (existsSync(png)) continue;

    const angle = (fm.match(/^angle:\s*(.+)$/m)?.[1] ?? "post").trim();
    const num = post.match(/post_(\d+)/)[1];
    const color = accent(angle);
    const coverData = Buffer.from(readFileSync(cover)).toString("base64");

    const html = `<!doctype html><style>
      *{margin:0;box-sizing:border-box}
      body{width:800px;height:360px;background:#fff;font-family:'DejaVu Sans',sans-serif}
      .cover{width:800px;height:300px;display:flex;align-items:center;justify-content:center;overflow:hidden}
      .cover img{max-width:100%;max-height:100%}
      .strip{width:800px;height:60px;background:#1a2744;display:flex;align-items:center;padding:0 24px;gap:14px}
      .dot{width:14px;height:14px;border-radius:50%;background:${color}}
      .angle{color:#fff;font-size:20px;font-weight:bold;text-transform:lowercase}
      .idx{margin-left:auto;color:#adb5bd;font-size:16px;font-family:'DejaVu Sans Mono',monospace}
    </style>
    <div class="cover"><img src="data:image/svg+xml;base64,${coverData}"></div>
    <div class="strip"><div class="dot"></div><div class="angle">${angle}</div>
    <div class="idx">${dir.slice(0, 10)} · ${num}/${posts.length}</div></div>`;

    const tmp = join(tmpdir(), "variant-cover.html");
    writeFileSync(tmp, html);
    await page.goto(`file://${tmp}`);
    await page.screenshot({ path: png });
    rmSync(tmp, { force: true });
    made++;
  }
}
console.log(`${made} variant covers written`);
await browser.close();
