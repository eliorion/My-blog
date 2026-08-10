# Plan: run the LinkedIn auto-post job on the homelab K8s cluster

> ## ⚠️ Superseded — do NOT deploy `k8s/linkedin-drip/`
>
> The job now runs as an **n8n workflow** in the homelab cluster, not as the
> CronJob in `k8s/linkedin-drip/`. That directory stays here as the reference the
> workflow was ported from; deploying it as well would publish the same queue
> twice.
>
> - homelab: `documentations/n8n-workflows/linkedin-drip.json` + its README
> - platform it runs on: `documentations/10-n8n-automation.md`
>
> Everything below is still accurate about **why** the job left GitHub-hosted
> runners and **how the publisher behaves** — that is why the file is kept. Only
> "Deployment steps" and "Rollback" changed; both are corrected in place.

Audience: a Claude session working in the homelab / cluster project. Self-contained —
it carries every fact needed from the blog repo side.

**Nothing in this repo needs deploying.** `linkedin/publish.py` remains the tool for
minting tokens (`auth`), checking the queue (`status`) and one-off manual posts
(`publish <file>`); only the scheduled weekday run moved into n8n.

## Why the job must run in the cluster

The blog repo (`github.com:eliorion/My-blog`) publishes one LinkedIn post per weekday.
It ran on GitHub-hosted runners and hit two walls:

1. **Images blocked by IP.** `POST /rest/images?action=initializeUpload` returns an HTML
   400 (WAF page) from GitHub's datacenter ranges — reproduced 2026-07-30 and 2026-07-31.
   An explicit `User-Agent` changed nothing; the same call succeeds from the home
   connection. Posts therefore went out text-only through the script's fallback.
2. **Cron latency.** GitHub `schedule` fired up to ~2h20 late or was dropped entirely
   on three consecutive days.

The cluster sits on the home ISP address, so both problems disappear: uploads are
accepted and `CronJob` timing is exact. No Tailscale or egress gateway is involved —
that is deliberate; routing this namespace through a VPN exit would reintroduce a
datacenter IP and bring back the WAF block.

## How the publisher works (already built, do not reimplement)

`linkedin/publish.py` — standard library only, no dependencies to install.

- `python linkedin/publish.py next`
  - picks the oldest `linkedin/drafts/*/post_N.md` whose frontmatter has no `published:`
  - exits early with "Already published today" if any draft was published today —
    the guard that makes retries and overlapping triggers idempotent
  - uploads the matching `post_N.png` through the Images API and attaches it; if the
    upload fails it logs the response body and publishes text-only rather than aborting
  - on success writes `published:` and `post_urn:` into that draft's frontmatter
- `python linkedin/publish.py status` — queue state, safe to run anywhere
- Credentials come from the environment: `LINKEDIN_ACCESS_TOKEN`, `LINKEDIN_PERSON_URN`

Queue state lives in git (the frontmatter marker), so the job clones `dev`, publishes,
commits the marker and pushes back. Branch layout: default branch is `main`, the drip
queue and its markers live on `dev`, `main` is merged forward regularly.

## The superseded CronJob (reference only — not deployed)

`k8s/linkedin-drip/cronjob.yaml`, summarised. The n8n workflow reproduces its
behaviour exactly; this is what it was ported from:

- schedule `47 7 * * 1-5`, `timeZone: Europe/Paris`, `concurrencyPolicy: Forbid`
- image `python:3.13-alpine`; `apk add --no-cache git` at start (the only runtime install)
- clones `dev` shallow into an `emptyDir`, runs `publish.py next`, commits the marker,
  pushes with up to three rebase retries because laptop and CI also push to `dev`
- secret `linkedin-drip` mounted with `envFrom`

## Where it actually runs now

An n8n workflow in the homelab cluster. Setup lives in the homelab repo — see
`documentations/n8n-workflows/README.md` there for the full runbook. Summary of what
differs from the CronJob above:

- **Same** schedule (`47 7 * * 1-5` Europe/Paris), same queue, same LinkedIn calls
  (`LinkedIn-Version: 202606`, the `linkedin-drip/1.0` User-Agent, the image
  `initializeUpload` → `PUT` → attach sequence, and the text-only fallback).
- **Different**: the `published:` marker is written through the GitHub Contents API
  instead of `git clone` / `commit` / `push`. The blob `sha` read seconds earlier is
  the concurrency token, so a concurrent edit 409s loudly rather than being clobbered
  — the three-attempt rebase loop is gone. No `apk add git`, no container to harden.
- **Credentials** live in n8n's own credential store, not a Kubernetes Secret:
  `LinkedIn Bearer` (Header Auth) and `GitHub My-blog PAT` (fine-grained, Contents:
  read and write, `eliorion/My-blog` only).

The Code nodes were diffed against `publish.py` over all 165 drafts — ordering, PNG
detection, the next-draft choice, the already-published-today guard, the full POST body
(byte-identical) and the frontmatter rewrite all match.

The current LinkedIn token **expires 2026-09-26**. Renewal is manual and unchanged:
run `python linkedin/publish.py auth` locally, then paste the new value into the
`LinkedIn Bearer` credential in the n8n UI (and the `LINKEDIN_ACCESS_TOKEN` repo secret
if you still want the GitHub fallback to work).

### Egress still matters just as much

The n8n namespace must keep leaving via the home ISP. Its Tailscale *Ingress* publishes
the UI and is inbound only, but routing the namespace's egress through Tailscale or any
VPN exit would reintroduce a datacenter IP and silently bring the image block back —
posts keep succeeding, just without their cover.

```bash
kubectl run ipcheck -n n8n --rm -it --restart=Never \
  --image=curlimages/curl -- curl -s https://ifconfig.me
```

Must print the home ISP address.

### Nothing to disable on GitHub

Already done in this repo: `.github/workflows/linkedin-drip.yaml` no longer has a
`schedule:` trigger, only `workflow_dispatch`. That prevents a GitHub run from beating
the cluster to the next queued draft and publishing it without its image. It stays
available as a manual fallback (`gh workflow run "LinkedIn drip" --ref main`) if the
cluster is down — accepting a text-only post that day.

## Monitoring

The job is silent when healthy.

- n8n **Executions** (filter: *Error*) — a failed run shows the actual API response.
  There are no push notifications by design; the homelab's only pushed n8n alert is
  `N8nDown`, for when n8n itself stops.
- this repo shows daily `chore(linkedin): mark draft as published` commits on `dev`;
  a gap of more than a day means the job stopped. That check needs no tooling and
  works even if n8n is unreachable.
- `python linkedin/publish.py status` — queue depth and what is next, from anywhere.

## Rollback

Deactivate the `linkedin-drip` workflow in n8n, then restore the `schedule:` block in
`.github/workflows/linkedin-drip.yaml` (`47 7 * * 1-5` and `47 9 * * 1-5`, UTC).
Posts resume text-only, with GitHub's cron latency.

Only ever have **one** of these three live at a time — the n8n workflow, the GitHub
schedule, or `k8s/linkedin-drip/` — or the same queue gets published more than once.

## Out of scope: draft generation

A separate workflow, `.github/workflows/linkedin-generate.yaml`, creates the drafts when
a new blog post is pushed. It runs the `claude` CLI and needs the repo secret
`CLAUDE_CODE_OAUTH_TOKEN` (produced by `claude setup-token`, one-year lifetime), which is
**not set yet** — until it is, that workflow fails fast with an explicit error and
generation stays manual:

```bash
python linkedin/generate.py generate   # writes drafts for any new blog post
node linkedin/variant_covers.mjs       # renders the missing post_N.png covers
```

Both are idempotent and skip existing work. This is unrelated to the cluster job —
the publisher only consumes what is already committed.
