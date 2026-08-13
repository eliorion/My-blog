# svg-render

The browser n8n does not have.

`Fix Cover SVG` in "Blog - Draft and PR" measures text from DejaVu metrics baked
into the Code node, because the n8n sandbox cannot render anything. That is good
enough to re-space a chip row from arithmetic, and useless for answering "does this
cover actually look right". This service answers both: it runs the repo's own
repair and the repo's own lint against a real browser.

Neither is a copy. `lib/svg-repair.mjs` and `lib/svg-audit.mjs` are imported by
this server *and* by `scripts/svg-fix.mjs` / `scripts/svg-preview.mjs`, so they
cannot drift — and because they live under this directory, a change to either one
counts as a change to the image for release-please. The Dockerfile also deletes
every font except DejaVu, so a render in the cluster matches a render in the dev
container.

## API

```
GET  /healthz -> {"ok": true, "connected": true}

POST /fix
     {"svg": "<svg viewBox=\"0 0 800 300\" ...>...</svg>"}
  -> {"svg": "<repaired markup>",
      "changed":  ["re-laid out 3 chips", "wrapped 1 captions"],
      "notes":    ["row at y=110 cannot fit 5 chips — fix by hand"],
      "errors":   ["text \"…\" overflows its rect by 12.4px"],
      "warnings": ["no installed font in stack \"Arial\" — render here uses a fallback"]}

POST /render
     {"svg": "...", "scale": 2}
  -> {"png": "<base64>", "width": 800, "height": 300}
```

`/fix` repairs first and lints the result, so the findings describe the markup the
caller is about to commit. `changed` is what it fixed, `notes` what it could not.
`errors` are geometry faults — text off canvas, a label bleeding through its chip,
two labels overlapping — and `warnings` are font-stack misses. Body limit 4 MB,
per-page timeout 15 s, `scale` defaults to 2.

## Who calls it

The `Blog - Cover Review` n8n workflow, at
`http://svg-render.svg-render.svc.cluster.local:8080`, once per proposal in the
Telegram loop: `/fix` before the commit, `/render` for the photo. Nothing else —
the Service is ClusterIP and there is no Ingress.

## How a new image gets made

Nothing here is built on a plain push. The chain is:

1. A conventional commit touching `svg-render/` lands on `main`.
2. `release-please` opens (or updates) a release PR for this package only — a
   blog post or a LinkedIn draft never triggers one, because commits are assigned
   by path and everything in the image lives under this directory.
3. Merging that PR bumps `package.json`, writes `CHANGELOG.md` and tags
   `svg-render-vX.Y.Z`.
4. The tag runs `.github/workflows/svg-render-image.yaml`: build once into the
   local daemon, **Trivy scans those exact bytes** (CRITICAL + HIGH, fixed only),
   and only then does it log in to ghcr and push `:X.Y.Z` and `:latest`. A failed
   scan means nothing is pushed. Accepted CVEs go in `/.trivyignore` with a reason.

Pull requests touching `svg-render/` build and scan without pushing, so a
vulnerability shows up before merge. Findings land in the repo's Security tab
either way. `workflow_dispatch` ships the version currently in
`.release-please-manifest.json` — that is the bootstrap path for the first push.

## Deploy

Make the ghcr package public once (or add a pull secret), then:

```bash
kubectl apply -k k8s/svg-render
kubectl -n svg-render rollout status deploy/svg-render
kubectl -n svg-render port-forward svc/svg-render 8080:8080   # to poke it by hand
```

The Deployment tracks `:latest` with `imagePullPolicy: Always`, so picking up a
release is `kubectl -n svg-render rollout restart deploy/svg-render`. Pin
`image:` to `:X.Y.Z` in `k8s/svg-render/deployment.yaml` instead if you would
rather the manifest say exactly what is running — release-please does not edit it.

## Running it locally

```bash
ln -s ../.claude/skills/preview-blog/node_modules svg-render/node_modules
node svg-render/server.mjs
```

## Notes

- Chromium runs with `--no-sandbox`. The pod is the boundary instead: ClusterIP
  only, all capabilities dropped, `RuntimeDefault` seccomp. The server also strips
  `<script>` and `on*` handlers from the SVG and aborts every http(s) request the
  page tries to make, so the markup a model wrote cannot execute or phone home.
- `/dev/shm` is an in-memory `emptyDir`. Chromium crashes on the 64 MiB a
  container gets by default.
- npm is deleted from the image after `npm install`. The container runs
  `node server.mjs` and nothing else, and npm's bundled dependencies were the
  entire CRITICAL/HIGH surface Trivy found — vulnerable code that would never
  have executed. Deleting it is cheaper than carrying it in `.trivyignore`.
- Build context is this directory: `docker build -t svg-render svg-render`.
