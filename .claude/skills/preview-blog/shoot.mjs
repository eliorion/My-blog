// Serve the Hugo blog and screenshot key pages so the rendered site can be seen.
// Usage: node shoot.mjs   (run from .claude/skills/preview-blog/)
import { spawn } from "node:child_process";
import { mkdirSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const HERE = dirname(fileURLToPath(import.meta.url));
const REPO = resolve(HERE, "../../..");
const OUT = resolve(HERE, "screenshots");
const PORT = 1313;
const BASE = `http://localhost:${PORT}`;

mkdirSync(OUT, { recursive: true });

let chromium;
try {
  ({ chromium } = await import("playwright"));
} catch {
  console.error("playwright not installed. Run: npm install (in this dir)");
  process.exit(1);
}

// Pages to capture: [path, name, viewport]
const DESKTOP = { width: 1280, height: 800 };
const MOBILE = { width: 390, height: 844 };
const SHOTS = [
  ["/", "home-desktop", DESKTOP],
  ["/", "home-mobile", MOBILE],
  ["/posts/", "posts-desktop", DESKTOP],
  ["/archives/", "archives-desktop", DESKTOP],
  ["/search/", "search-desktop", DESKTOP],
  ["/about/", "about-desktop", DESKTOP],
  ["/tags/", "tags-desktop", DESKTOP],
];

// Start hugo server with a clean local baseURL so links resolve on localhost.
const hugo = spawn(
  "hugo",
  ["server", "-s", "blog", "--baseURL", `${BASE}/`, "--appendPort=false", "-p", String(PORT), "-D"],
  { cwd: REPO, stdio: ["ignore", "pipe", "pipe"] },
);
hugo.stdout.on("data", (d) => process.stdout.write(`[hugo] ${d}`));
hugo.stderr.on("data", (d) => process.stderr.write(`[hugo] ${d}`));

const cleanup = () => { try { hugo.kill("SIGTERM"); } catch {} };
process.on("exit", cleanup);
process.on("SIGINT", () => { cleanup(); process.exit(130); });

async function waitForServer(timeoutMs = 30000) {
  const start = performance.now();
  while (performance.now() - start < timeoutMs) {
    try {
      const r = await fetch(BASE + "/");
      if (r.ok) return;
    } catch {}
    await new Promise((res) => setTimeout(res, 400));
  }
  throw new Error("Hugo server did not become ready in time");
}

try {
  await waitForServer();
  let browser;
  try {
    browser = await chromium.launch();
  } catch (e) {
    console.error("\nChromium missing. One-time setup: npx playwright install chromium\n");
    throw e;
  }
  for (const [path, name, viewport] of SHOTS) {
    const page = await browser.newPage({ viewport });
    const url = BASE + path;
    try {
      await page.goto(url, { waitUntil: "networkidle", timeout: 15000 });
      const file = resolve(OUT, `${name}.png`);
      await page.screenshot({ path: file, fullPage: true });
      console.log(`shot: ${name}.png  (${url})`);
    } catch (e) {
      console.warn(`skip ${name}: ${e.message}`);
    } finally {
      await page.close();
    }
  }
  await browser.close();
  console.log(`\nScreenshots in: ${OUT}`);
} finally {
  cleanup();
}
