# Plan: move the LinkedIn auto-post job onto the homelab K8s cluster (ARC)

Audience: a Claude session working in the homelab/cluster project. This document is
self-contained — it carries all context needed from the blog repo side.

## Why move

The blog repo (`github.com:eliorion/My-blog`) publishes one LinkedIn post per weekday
via the GitHub Actions workflow `.github/workflows/linkedin-drip.yaml`. Two problems
with GitHub-hosted runners:

1. **Images blocked.** LinkedIn's WAF returns an HTML 400 to `POST /rest/images?action=initializeUpload`
   from GitHub's datacenter IP ranges (confirmed 2026-07-30 and 2026-07-31; an explicit
   User-Agent did not help — it is IP-based). The same call succeeds from a residential IP.
   Result: posts publish text-only via the built-in fallback, never with their cover image.
2. **Cron latency.** GitHub `schedule` triggers fire up to ~2h20 late or get dropped
   (observed 2026-07-29 → 2026-07-31).

Running the job on an ARC (Actions Runner Controller) runner inside the homelab cluster
fixes (1) because egress uses the home ISP IP. It does NOT fix (2) by itself — the
`schedule` event is still evaluated by GitHub. Step 6 optionally fixes (2) with an
in-cluster CronJob that triggers the workflow at an exact time.

## Current state (blog repo side — do not re-implement, it all works)

- `linkedin/publish.py` — stdlib-only publisher. `python linkedin/publish.py next`:
  - picks the oldest `linkedin/drafts/*/post_N.md` without `published:` in frontmatter
  - exits early ("Already published today") if any draft was published today — the daily
    guard that makes multiple cron slots / retries idempotent
  - uploads `post_N.png` (same basename as the .md) via the LinkedIn Images API and
    attaches it; on upload failure it logs the error body and publishes text-only
  - on success writes `published:` + `post_urn:` into the draft's frontmatter
- `.github/workflows/linkedin-drip.yaml` — triggers: cron `47 7 * * 1-5`, cron
  `47 9 * * 1-5` (retry slot, no-ops via the daily guard), `workflow_dispatch`.
  Steps: checkout `dev` → setup-python 3.13 → `python linkedin/publish.py next` →
  commit the frontmatter mark back to `dev` (`[skip ci]`).
- Repo secrets (already set): `LINKEDIN_ACCESS_TOKEN` (member OAuth token,
  **expires 2026-09-26**, renew via `python linkedin/publish.py auth` locally),
  `LINKEDIN_PERSON_URN`. The script reads both from env.
- The repo is **public**. Default branch `main`; the queue lives on `dev` (main is
  merged forward regularly).

## Target architecture

```
GitHub schedule/dispatch ──► job "publish" ──► runs-on: <ARC scale set>
                                              pod in homelab cluster
                                              egress via home ISP IP
                                              └─ python publish.py next
                                                 ├─ Images API  ✓ (no WAF block)
                                                 └─ Posts API   ✓
(optional) k8s CronJob ──► gh workflow_dispatch at exact time, weekdays
```

## Implementation steps (cluster side)

### 1. Inventory the existing ARC install

```bash
kubectl get autoscalingrunnersets -A \
  -o custom-columns=NS:.metadata.namespace,NAME:.metadata.name,URL:.spec.githubConfigUrl
kubectl get pods -n <arc-system-namespace>   # controller + listeners
helm list -A | grep -i gha                   # chart + version
```

Record: controller namespace/version, the auth method in use (GitHub App vs PAT),
and the secret that holds it.

### 2. Add a runner scale set for My-blog

If the existing scale set's `githubConfigUrl` already covers `eliorion/My-blog`
(org-level URL), skip to step 3 and reuse its name.

Otherwise install a new `gha-runner-scale-set` release, following the cluster's
existing GitOps pattern (same chart version as the current install):

```yaml
# values — adjust names to cluster conventions
githubConfigUrl: https://github.com/eliorion/My-blog
githubConfigSecret: <existing ARC github secret, or a new one with the same App/PAT>
minRunners: 0
maxRunners: 1
runnerScaleSetName: blog-runner        # ← this is the `runs-on:` value
```

Notes:
- PAT scope needed for repo-level registration: `repo`. GitHub App needs
  Actions (read) + Administration (read/write) on the repo — same as the existing install.
- `minRunners: 0` — ephemeral pod spins up per job, nothing idles.
- Runner image must have `git`, and `python3` ≥ 3.10 available or installable;
  the default ARC runner image + `actions/setup-python` works.

### 3. Verify egress IP (critical — this is the whole point)

From a pod on the same node pool / egress path as the runners:

```bash
kubectl run ipcheck --rm -it --image=curlimages/curl --restart=Never -- \
  curl -s https://ifconfig.me
```

Must return the **home ISP IP**, not a VPN/tunnel datacenter exit. If cluster egress
routes through a VPS/Cloudflare/Tailscale exit node with a datacenter IP, exempt the
runner namespace from that route — otherwise the WAF block returns and the move is pointless.

### 4. Confirm the runner registers

```bash
# from any machine with gh authenticated to eliorion
gh api repos/eliorion/My-blog/actions/runners --jq '.runners[].name'
```

Scale-set runners are ephemeral: also check the listener pod logs show a successful
session for `blog-runner`.

### 5. Blog repo change (coordinate with a session in the blog repo, or do it here)

In `.github/workflows/linkedin-drip.yaml`, job `publish`:

```diff
-    runs-on: ubuntu-latest
+    runs-on: blog-runner
```

Keep everything else identical. Commit to `dev`, merge to `main` (cron reads main).

**Security hardening — required, the repo is public:**
- Repo → Settings → Actions → General → Fork pull request workflows:
  "Require approval for all outside collaborators".
- Leave the other workflows (`linkedin-generate`, `linkedin.yaml` CI, Hugo deploy)
  on `ubuntu-latest` — only the drip job needs the homelab IP; smaller attack surface.
- ARC ephemeral runners: verify `containerMode` is default (no privileged, no docker-in-docker
  needed for this job).

### 6. Optional: exact-time trigger (fixes GitHub cron latency)

Keep the GitHub crons as fallback (the daily guard makes double-triggers no-ops) and add
an in-cluster CronJob that calls the dispatch API at the desired local time:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: linkedin-drip-trigger
spec:
  schedule: "45 7 * * 1-5"        # cluster TZ; set spec.timeZone explicitly, e.g. Europe/Paris
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: Never
          containers:
            - name: trigger
              image: curlimages/curl
              envFrom: [{secretRef: {name: github-dispatch-token}}]   # PAT: actions:write on My-blog
              command:
                - sh
                - -c
                - >
                  curl -sf -X POST
                  -H "Authorization: Bearer $GH_TOKEN"
                  -H "Accept: application/vnd.github+json"
                  https://api.github.com/repos/eliorion/My-blog/actions/workflows/linkedin-drip.yaml/dispatches
                  -d '{"ref":"main"}'
```

### 7. End-to-end test

1. `gh workflow run "LinkedIn drip" --ref main` (or wait for the CronJob).
2. Job must be picked up by a `blog-runner` pod (check `kubectl get pods` during the run).
3. Run log must show `Published drafts/... -> urn:li:share:...`
   **without** a preceding `Image upload failed` line — that line means the WAF still
   blocks and the egress IP (step 3) needs fixing.
4. The published LinkedIn post shows the variant cover image.
5. The run's last step pushed a `chore(linkedin): mark draft as published [skip ci]`
   commit to `dev`.

## Rollback

Revert `runs-on:` to `ubuntu-latest` on `main`. Publishing continues (text-only images
fallback), nothing else depends on the cluster.

## Known dates

- LinkedIn member token expires **2026-09-26** — renew locally
  (`python linkedin/publish.py auth`), update repo secret `LINKEDIN_ACCESS_TOKEN`.
