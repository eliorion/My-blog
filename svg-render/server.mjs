// The browser n8n does not have.
//
// n8n's Code node cannot render an SVG, so `Fix Cover SVG` in "Blog - Draft and
// PR" guesses text widths from DejaVu metrics baked into the node. This service
// is the real thing: the same repair and the same lint the repo runs locally,
// over HTTP, measured in an actual browser. `scripts/svg-repair.mjs` and
// `scripts/svg-audit.mjs` are imported, not copied, so nothing can drift.
//
// POST /fix     {"svg": "<svg .../>"}
//   -> {"svg": "<repaired>", "changed": [...], "notes": [...], "errors": [...], "warnings": [...]}
// POST /render  {"svg": "<svg .../>", "scale": 2}
//   -> {"png": "<base64>", "width": 800, "height": 300}
// GET  /healthz -> ok
import { createServer } from "node:http";
import { chromium } from "playwright-core";
import { audit } from "./lib/svg-audit.mjs";
import { MAX_GAP, PADS, GAPS, plan, patchSource, describe } from "./lib/svg-repair.mjs";

const PORT = Number(process.env.PORT || 8080);
const MAX_BODY = 4_000_000;

// Nothing here should ever execute script or reach the network: the SVG comes
// from a language model, and this pod sits inside the cluster.
const declaw = (svg) =>
  String(svg)
    .replace(/<script[\s\S]*?<\/script>/gi, "")
    .replace(/<script\b[^>]*\/>/gi, "")
    .replace(/\son\w+\s*=\s*"[^"]*"/gi, "")
    .replace(/\son\w+\s*=\s*'[^']*'/gi, "");

const browser = await chromium.launch({ args: ["--no-sandbox"] });

const size = (svg) => {
  const m = String(svg).match(/viewBox="[\d.\-]+ [\d.\-]+ ([\d.]+) ([\d.]+)"/);
  return m ? [Number(m[1]), Number(m[2])] : [800, 600];
};

async function withPage(svg, scale, fn) {
  const [w, h] = size(svg);
  const page = await browser.newPage({
    viewport: { width: Math.round(w), height: Math.round(h) },
    deviceScaleFactor: scale,
  });
  page.setDefaultTimeout(15000);
  try {
    await page.route(/^https?:/, (route) => route.abort());
    await page.setContent(
      `<!doctype html><style>html,body{margin:0;background:#fff}svg{display:block}</style>${declaw(svg)}`,
    );
    await page.evaluate(() => document.fonts.ready);
    if (!(await page.locator("svg").count())) throw new Error("no <svg> element in the markup");
    return await fn(page, w, h);
  } finally {
    await page.close();
  }
}

// Repair first, then lint what came out — the findings describe the SVG the
// caller is about to commit, not the one it sent.
async function fix(svg) {
  const { patches, notes } = await withPage(svg, 1, (page) =>
    page.evaluate(plan, { MAX_GAP, PADS, GAPS }),
  );
  let out = svg;
  for (const p of patches) out = patchSource(out, p);
  const { errors, warnings } = await withPage(out, 1, (page) => page.evaluate(audit));
  return { svg: out, changed: describe(patches), notes, errors, warnings };
}

async function render(svg, scale) {
  return withPage(svg, scale, async (page, width, height) => ({
    png: (await page.locator("svg").first().screenshot()).toString("base64"),
    width,
    height,
  }));
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    let bytes = 0;
    const chunks = [];
    req.on("data", (c) => {
      bytes += c.length;
      if (bytes > MAX_BODY) {
        reject(new Error("body too large"));
        req.destroy();
        return;
      }
      chunks.push(c);
    });
    req.on("end", () => resolve(Buffer.concat(chunks).toString("utf8")));
    req.on("error", reject);
  });
}

const send = (res, code, body) => {
  const payload = JSON.stringify(body);
  res.writeHead(code, {
    "content-type": "application/json",
    "content-length": Buffer.byteLength(payload),
  });
  res.end(payload);
};

createServer(async (req, res) => {
  if (req.method === "GET" && req.url === "/healthz") {
    send(res, 200, { ok: true, connected: browser.isConnected() });
    return;
  }
  if (req.method !== "POST" || !["/fix", "/render"].includes(req.url)) {
    send(res, 404, { error: "POST /fix, POST /render or GET /healthz" });
    return;
  }
  try {
    const { svg, scale } = JSON.parse(await readBody(req));
    if (typeof svg !== "string" || !svg.trim()) {
      send(res, 400, { error: "svg is required" });
      return;
    }
    send(
      res,
      200,
      req.url === "/fix" ? await fix(svg) : await render(svg, Number(scale) > 0 ? Number(scale) : 2),
    );
  } catch (err) {
    send(res, 400, { error: String(err && err.message ? err.message : err) });
  }
}).listen(PORT, () => console.log(`svg-render listening on ${PORT}`));

for (const sig of ["SIGTERM", "SIGINT"]) {
  process.on(sig, async () => {
    await browser.close();
    process.exit(0);
  });
}
