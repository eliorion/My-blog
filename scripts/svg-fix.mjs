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

const MAX_GAP = 24; // above this the rects are a diagram, not a chip row
const PADS = [13, 11, 9]; // tried in order until the row fits the canvas
const GAPS = [10, 8];

// Runs in the page. Returns attribute patches keyed by element index.
const plan = ({ MAX_GAP, PADS, GAPS }) => {
  const svg = document.querySelector("svg");
  const vb = svg.viewBox.baseVal;
  const rects = [...svg.querySelectorAll("rect")];
  const texts = [...svg.querySelectorAll("text")];
  const patches = [];
  const notes = [];

  // Pair every rounded rect with the centred label sitting inside it.
  const chips = [];
  rects.forEach((rect, ri) => {
    const rx = parseFloat(rect.getAttribute("rx") || 0);
    const x = parseFloat(rect.getAttribute("x") || 0);
    const y = parseFloat(rect.getAttribute("y") || 0);
    const w = parseFloat(rect.getAttribute("width") || 0);
    const h = parseFloat(rect.getAttribute("height") || 0);
    if (!rx || w > 300 || h > 60) return;
    const inside = texts
      .map((t, ti) => ({ t, ti }))
      .filter(({ t }) => {
        if (t.getAttribute("text-anchor") !== "middle") return false;
        const tx = parseFloat(t.getAttribute("x") || 0);
        const ty = parseFloat(t.getAttribute("y") || 0);
        return tx > x && tx < x + w && ty > y && ty < y + h;
      });
    if (inside.length !== 1) return;
    chips.push({ ri, x, y, w, h, ti: inside[0].ti, text: inside[0].t });
  });

  // Group into rows, then keep only rows that are packed tightly enough to be chips.
  const rows = new Map();
  for (const c of chips) {
    const key = Math.round(c.y);
    if (!rows.has(key)) rows.set(key, []);
    rows.get(key).push(c);
  }

  for (const row of rows.values()) {
    // A lone badge has no neighbours to push, so just grow it around its centre.
    if (row.length === 1) {
      const c = row[0];
      const need = Math.ceil(c.text.getBBox().width) + 10;
      if (need <= c.w) continue;
      const cx = c.x + c.w / 2;
      const x = Math.max(vb.x + 2, Math.min(cx - need / 2, vb.x + vb.width - need - 2));
      patches.push({ tag: "rect", i: c.ri, attrs: { x, width: need } });
      patches.push({ tag: "text", i: c.ti, attrs: { x: x + need / 2 } });
      continue;
    }
    row.sort((a, b) => a.x - b.x);
    const gaps = row.slice(1).map((c, i) => c.x - (row[i].x + row[i].w));
    if (gaps.some((g) => g > MAX_GAP || g < 0)) continue; // diagram, not a chip row

    const start = row[0].x;
    const limit = vb.x + vb.width - Math.min(start - vb.x, 25);
    const size0 = parseFloat(getComputedStyle(row[0].text).fontSize);
    const measure = (px) => {
      row.forEach((c) => c.text.setAttribute("font-size", px));
      const ws = row.map((c) => c.text.getBBox().width);
      row.forEach((c) => c.text.setAttribute("font-size", size0));
      return ws;
    };

    // Loosest layout that still fits: keep the type size if at all possible,
    // then tighten padding, then the gap, and only then shrink the label.
    let fit = null;
    for (const size of [size0, size0 - 1, size0 - 2].filter((s) => s >= 10)) {
      const labels = measure(size);
      for (const pad of PADS)
        for (const gap of GAPS) {
          const widths = labels.map((lw) => Math.ceil(lw) + 2 * pad);
          const end = widths.reduce((a, b) => a + b, 0) + gap * (row.length - 1) + start;
          if (end <= limit) {
            fit = { widths, gap, size: size === size0 ? null : size };
            break;
          }
        }
      if (fit) break;
    }
    if (!fit) {
      notes.push(`row at y=${Math.round(row[0].y)} cannot fit ${row.length} chips — fix by hand`);
      continue;
    }

    let cursor = start;
    row.forEach((c, i) => {
      const w = fit.widths[i];
      if (Math.abs(w - c.w) > 0.5 || Math.abs(cursor - c.x) > 0.5 || fit.size) {
        patches.push({ tag: "rect", i: c.ri, attrs: { x: cursor, width: w } });
        const t = { x: cursor + w / 2 };
        if (fit.size) t["font-size"] = fit.size;
        patches.push({ tag: "text", i: c.ti, attrs: t });
      }
      cursor += w + fit.gap;
    });
  }

  // Captions: wrap anything running off the right edge, keeping the type size.
  const canvas = svg.getBoundingClientRect();
  const ctx = document.createElement("canvas").getContext("2d");
  texts.forEach((t, ti) => {
    if (t.getAttribute("text-anchor") === "middle") return;
    if (t.querySelector("tspan")) return; // already wrapped
    const box = t.getBoundingClientRect();
    if (box.right <= canvas.right + 0.5) return;

    const cs = getComputedStyle(t);
    const size = parseFloat(cs.fontSize);
    const x = parseFloat(t.getAttribute("x") || 0);
    const y = parseFloat(t.getAttribute("y") || 0);
    const avail = vb.x + vb.width - Math.min(x - vb.x, 25) - x;
    ctx.font = `${cs.fontStyle} ${cs.fontWeight} ${size}px ${cs.fontFamily}`;

    const lines = [];
    let line = "";
    for (const word of t.textContent.trim().split(/\s+/)) {
      const next = line ? `${line} ${word}` : word;
      if (line && ctx.measureText(next).width > avail) {
        lines.push(line);
        line = word;
      } else line = next;
    }
    if (line) lines.push(line);
    if (lines.length < 2) {
      notes.push(`caption at y=${y} overflows but will not wrap — shorten it by hand`);
      return;
    }

    const lead = Math.round(size * 1.25);
    patches.push({
      tag: "text",
      i: ti,
      attrs: { y: y - lead * (lines.length - 1) },
      lines: { x, lead, lines },
    });
  });

  return { patches, notes };
};

// Rewrite one attribute inside the nth <tag ...> of the source, leaving every
// other byte — comments, indentation, attribute order — untouched.
const xml = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

const patchSource = (src, { tag, i: index, attrs, lines }) => {
  const re = new RegExp(`<${tag}\\b[^>]*>`, "g");
  let m,
    n = 0;
  while ((m = re.exec(src))) {
    if (n++ !== index) continue;
    let tagSrc = m[0];
    for (const [k, v] of Object.entries(attrs)) {
      const val = Number.isInteger(v) ? String(v) : String(Math.round(v * 10) / 10);
      const attrRe = new RegExp(`(\\s${k}=")[^"]*(")`);
      tagSrc = attrRe.test(tagSrc)
        ? tagSrc.replace(attrRe, `$1${val}$2`)
        : tagSrc.replace(`<${tag}`, `<${tag} ${k}="${val}"`);
    }
    let end = m.index + m[0].length;
    if (lines) {
      const close = src.indexOf(`</${tag}>`, end);
      if (close === -1) return src;
      tagSrc += lines.lines
        .map((l, li) => `<tspan x="${lines.x}"${li ? ` dy="${lines.lead}"` : ""}>${xml(l)}</tspan>`)
        .join("");
      end = close;
    }
    return src.slice(0, m.index) + tagSrc + src.slice(end);
  }
  return src;
};

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
  const wrapped = patches.filter((p) => p.lines).length;
  const chips = (patches.length - wrapped) / 2;
  const what = [chips && `${chips} chips`, wrapped && `${wrapped} captions`].filter(Boolean);
  console.log(`${dry ? "would fix" : "fixed"} ${f}  (${what.join(", ")})`);
}

await browser.close();
console.log(`\n${changed} file(s) ${dry ? "would change" : "changed"}`);
