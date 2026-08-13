// Runs in the page: measures every element in screen pixels and flags defects.
// Shared by ../server.mjs (the cluster service n8n calls) and
// ../../scripts/svg-preview.mjs (the local CLI), so both report the same
// findings. It is serialised into the browser by page.evaluate, so it must
// close over nothing.
export const audit = () => {
  const svg = document.querySelector("svg");
  const canvas = svg.getBoundingClientRect();
  const box = (el) => el.getBoundingClientRect();
  const texts = [...svg.querySelectorAll("text")].map((el) => ({
    el,
    r: box(el),
    s: (el.textContent || "").trim().slice(0, 40),
  }));
  const out = [];

  for (const { r, s } of texts) {
    if (!s) continue;
    const over = [
      r.left < canvas.left - 0.5 && "left",
      r.right > canvas.right + 0.5 && "right",
      r.top < canvas.top - 0.5 && "top",
      r.bottom > canvas.bottom + 0.5 && "bottom",
    ].filter(Boolean);
    if (over.length) out.push(`text "${s}" spills off canvas (${over.join(", ")})`);
  }

  // A text whose centre sits inside a small shape but whose box does not fit it
  // is overflowing its chip / button / badge.
  const shapes = [...svg.querySelectorAll("rect, ellipse, circle")]
    .map((el) => ({ el, r: box(el) }))
    .filter(({ r }) => r.width < canvas.width * 0.6 && r.height < canvas.height * 0.6);
  for (const { r, s } of texts) {
    if (!s) continue;
    const cx = r.left + r.width / 2;
    const cy = r.top + r.height / 2;
    for (const sh of shapes) {
      const inside = cx > sh.r.left && cx < sh.r.right && cy > sh.r.top && cy < sh.r.bottom;
      if (!inside) continue;
      const dx = Math.max(sh.r.left - r.left, r.right - sh.r.right);
      const dy = Math.max(sh.r.top - r.top, r.bottom - sh.r.bottom);
      if (dx > 1 || dy > 1)
        out.push(
          `text "${s}" overflows its ${sh.el.tagName} by ${Math.max(dx, dy).toFixed(1)}px`,
        );
    }
  }

  for (let i = 0; i < texts.length; i++)
    for (let j = i + 1; j < texts.length; j++) {
      const a = texts[i].r, b = texts[j].r;
      const w = Math.min(a.right, b.right) - Math.max(a.left, b.left);
      const h = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
      if (w > 2 && h > 2)
        out.push(`text "${texts[i].s}" overlaps "${texts[j].s}" (${w.toFixed(0)}x${h.toFixed(0)}px)`);
    }

  // A font-family the renderer cannot resolve silently changes every metric
  // above. document.fonts.check() lies for unknown families, so probe by width:
  // a missing family measures identically to the generic it falls back to.
  const ctx = document.createElement("canvas").getContext("2d");
  const probe = "MMMWWWiiill1 0Oo";
  const width = (fam) => {
    ctx.font = `32px ${fam}`;
    return ctx.measureText(probe).width;
  };
  const absent = (f) =>
    ["monospace", "serif"].every(
      (g) => Math.abs(width(`"${f}", ${g}`) - width(g)) < 0.01,
    );
  const missing = new Set();
  for (const { el } of texts) {
    const stack = (el.getAttribute("font-family") || el.style.fontFamily || "")
      .split(",")
      .map((x) => x.trim().replace(/^['"]|['"]$/g, ""))
      .filter((f) => f && !/^(serif|sans-serif|monospace|cursive|fantasy|system-ui)$/.test(f));
    if (stack.length && stack.every(absent)) missing.add(stack.join(", "));
  }
  // Warning, not an error: the stack may well resolve on another machine, it
  // just means the render seen here is not the render everyone else gets.
  const warn = [...missing].map(
    (stack) => `no installed font in stack "${stack}" — render here uses a fallback`,
  );

  return { errors: out, warnings: warn };
};
