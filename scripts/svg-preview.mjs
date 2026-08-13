// Render an SVG to PNG and report visual defects, so an SVG can be inspected
// (and fixed) before it ships. Uses the chromium already installed for the
// preview-blog skill.
//
// Usage: node scripts/svg-preview.mjs <file.svg> [more.svg ...] [--scale 2]
// Writes <file>.preview.png next to each source and prints lint findings.
import { readFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
import { audit } from "../svg-render/lib/svg-audit.mjs";

const HERE = dirname(fileURLToPath(import.meta.url));
const { chromium } = await import(
  resolve(HERE, "../.claude/skills/preview-blog/node_modules/playwright/index.mjs")
);

const argv = process.argv.slice(2);
const scaleFlag = argv.indexOf("--scale");
const scale = scaleFlag === -1 ? 2 : Number(argv[scaleFlag + 1]);
const files = argv.filter(
  (a, i) => !a.startsWith("--") && !(scaleFlag !== -1 && i === scaleFlag + 1),
);

if (!files.length) {
  console.error("usage: node scripts/svg-preview.mjs <file.svg> [...] [--scale 2]");
  process.exit(1);
}

const browser = await chromium.launch();
let bad = 0;

for (const f of files) {
  const src = resolve(f);
  if (!existsSync(src)) {
    console.error(`${f}: not found`);
    bad++;
    continue;
  }
  const svg = readFileSync(src, "utf8");
  const m = svg.match(/viewBox="[\d.\-]+ [\d.\-]+ ([\d.]+) ([\d.]+)"/);
  const [w, h] = m ? [Number(m[1]), Number(m[2])] : [800, 600];

  const page = await browser.newPage({
    viewport: { width: Math.round(w), height: Math.round(h) },
    deviceScaleFactor: scale,
  });
  await page.setContent(
    `<!doctype html><style>html,body{margin:0;background:#fff}svg{display:block}</style>${svg}`,
  );
  await page.evaluate(() => document.fonts.ready);

  const png = src.replace(/\.svg$/i, ".preview.png");
  await page.locator("svg").screenshot({ path: png });

  const { errors, warnings } = await page.evaluate(audit);
  console.log(`\n${f} → ${png}  (${w}x${h} @${scale}x)`);
  for (const x of errors) console.log(`  ! ${x}`);
  for (const x of warnings) console.log(`  ~ ${x}`);
  if (errors.length) bad++;
  else if (!warnings.length) console.log("  ok — nothing off");
  await page.close();
}

await browser.close();
process.exit(bad ? 1 : 0);
