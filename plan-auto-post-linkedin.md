# Plan: run the LinkedIn auto-post job on the homelab K8s cluster

Audience: a Claude session working in the homelab / cluster project. Self-contained —
it carries every fact needed from the blog repo side.

Deliverable already committed in this repo: `k8s/linkedin-drip/` (namespace, CronJob,
secret template, kustomization). The work left is deploying it and wiring the secret.

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

## What is deployed

`k8s/linkedin-drip/cronjob.yaml`, summarised:

- schedule `47 7 * * 1-5`, `timeZone: Europe/Paris`, `concurrencyPolicy: Forbid`
- image `python:3.13-alpine`; `apk add --no-cache git` at start (the only runtime install)
- clones `dev` shallow into an `emptyDir`, runs `publish.py next`, commits the marker,
  pushes with up to three rebase retries because laptop and CI also push to `dev`
- secret `linkedin-drip` mounted with `envFrom`

## Deployment steps

### 1. Create the secret

Template: `k8s/linkedin-drip/secret.example.yaml`. Encrypt it with the cluster's usual
SOPS/age flow (same pattern as the mve-itguard secrets) — never commit plaintext.

| Key | Value | Where it comes from |
| --- | --- | --- |
| `LINKEDIN_ACCESS_TOKEN` | member OAuth token | `python linkedin/publish.py auth` on the laptop |
| `LINKEDIN_PERSON_URN` | `urn:li:person:DxKqhDF5zi` | printed by the same command |
| `GITHUB_TOKEN` | fine-grained PAT, **Contents: read and write** on `eliorion/My-blog` only | github.com/settings/personal-access-tokens |

The current LinkedIn token **expires 2026-09-26**. Renewal is manual: run the auth
command locally, then update this secret and the `LINKEDIN_ACCESS_TOKEN` repo secret.

### 2. Apply the manifests

Through the homelab GitOps repo, matching its existing structure:

```bash
kubectl apply -k k8s/linkedin-drip/     # or copy the directory into the GitOps tree
```

### 3. Verify egress before trusting the schedule

```bash
kubectl run ipcheck -n linkedin-drip --rm -it --restart=Never \
  --image=curlimages/curl -- curl -s https://ifconfig.me
```

Must print the home ISP address. If it prints a VPS/Cloudflare/Tailscale exit address,
this namespace is being routed through a tunnel — exempt it, otherwise images stay blocked.

### 4. Trigger one run manually

```bash
kubectl create job -n linkedin-drip --from=cronjob/linkedin-drip drip-test
kubectl logs -n linkedin-drip -l job-name=drip-test -f
```

Success looks like:

```
Published drafts/2025-09-02---network-configuration/post_4.md -> urn:li:share:74888...
```

with **no** `Image upload failed` line above it. If that line appears, the pod's egress
is still a datacenter IP — go back to step 3.

Then confirm on LinkedIn that the post carries its cover image, and that a
`chore(linkedin): mark draft as published [skip ci]` commit landed on `dev`.

Clean up: `kubectl delete job -n linkedin-drip drip-test`.

### 5. Nothing to disable on GitHub

Already done in this repo: `.github/workflows/linkedin-drip.yaml` no longer has a
`schedule:` trigger, only `workflow_dispatch`. That prevents a GitHub run from beating
the cluster to the next queued draft and publishing it without its image. It stays
available as a manual fallback (`gh workflow run "LinkedIn drip" --ref main`) if the
cluster is down — accepting a text-only post that day.

## Monitoring

The job is silent when healthy. Options, in order of effort:

- `kubectl get cronjob -n linkedin-drip` — `LAST SCHEDULE` should be today
- alert on `kube_job_status_failed` for the namespace if Prometheus is already scraping
  kube-state-metrics
- the blog repo shows daily `chore(linkedin): mark draft as published` commits on `dev`;
  a gap of more than a day means the job stopped

## Rollback

Suspend the CronJob and hand the schedule back to GitHub:

```bash
kubectl patch cronjob -n linkedin-drip linkedin-drip -p '{"spec":{"suspend":true}}'
```

then restore the `schedule:` block in `.github/workflows/linkedin-drip.yaml`
(`47 7 * * 1-5` and `47 9 * * 1-5`, UTC). Posts resume text-only.

## Optional hardening

`apk add git` at every run is the one fragile point (needs Alpine repos reachable) and
forces the container to start as root. Pre-baking a small image with `python:3.13-alpine`
plus `git` removes both: publish it to the homelab registry, swap the `image:` field,
drop the `apk` line, and add `runAsNonRoot: true`.

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
