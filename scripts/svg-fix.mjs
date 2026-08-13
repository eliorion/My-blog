// Fix the two layout faults these covers keep hitting: chips too narrow for
// their label, and a caption too long for the canvas.
//
// Chips — a rounded rect holding one centre-anchored text; a row is two or more
// sharing a baseline with small gaps. Widths were hand-guessed and are routinely
// too narrow, so the label bleeds through the border. This measures each label
// for real and rewrites the row: width = label + 2·padding, constant gap, first
// chip stays put. Diagram boxes (widely spaced, wired together by lines) are
// left alone — only tightly packed rows qualify.
//
// Captions — a left-anchored line running past the right edge is wrapped into
// tspans at the same type size, growing upward so the last line keeps its
// original baseline. No word is dropped.
//
// Usage: node scripts/svg-fix.mjs <file.svg> [...] [--dry]
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
import {
  MAX_GAP,
  PADS,
  GAPS,
  plan,
  patchSource,
  describe,
} from "../svg-render/lib/svg-repair.mjs";

const HERE = dirname(fileURLToPath(import.meta.url));
const { chromium } = await import(
  resolve(HERE, "../.claude/skills/preview-blog/node_modules/playwright/index.mjs")
);

const argv = process.argv.slice(2);
const dry = argv.includes("--dry");
const files = argv.filter((a) => !a.startsWith("--"));
if (!files.length) {
  console.error("usage: node scripts/svg-fix-chips.mjs <file.svg> [...] [--dry]");
  process.exit(1);
}

const browser = await chromium.launch();
let changed = 0;

for (const f of files) {
  const src = resolve(f);
  if (!existsSync(src)) {
    console.error(`${f}: not found`);
    continue;
  }
  let svg = readFileSync(src, "utf8");
  const page = await browser.newPage();
  await page.setContent(`<!doctype html><style>html,body{margin:0}</style>${svg}`);
  await page.evaluate(() => document.fonts.ready);
  const { patches, notes } = await page.evaluate(plan, { MAX_GAP, PADS, GAPS });
  await page.close();

  for (const n of notes) console.log(`  ? ${f}: ${n}`);
  if (!patches.length) continue;

  // Later patches must not shift earlier match offsets, so apply per element.
  for (const p of patches) svg = patchSource(svg, p);
  if (!dry) writeFileSync(src, svg);
  changed++;
  console.log(`${dry ? "would fix" : "fixed"} ${f}  (${describe(patches).join(", ")})`);
}

await browser.close();
console.log(`\n${changed} file(s) ${dry ? "would change" : "changed"}`);
