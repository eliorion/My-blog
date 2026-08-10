# linkedin-drip

> ## ⚠️ Not deployed — superseded by an n8n workflow
>
> These manifests are kept as the reference the homelab's n8n `linkedin-drip`
> workflow was ported from. **Do not `kubectl apply` them.** Both would publish
> the same queue, so the same draft would go out twice.
>
> Live version: `documentations/n8n-workflows/linkedin-drip.json` in the homelab
> repo. Context: [`plan-auto-post-linkedin.md`](../../plan-auto-post-linkedin.md).

Weekday CronJob that publishes the next queued LinkedIn draft from `linkedin/drafts/`.

It runs in the homelab cluster rather than on GitHub Actions because LinkedIn's WAF
rejects image uploads coming from GitHub's datacenter IPs — from the home connection
they succeed, so posts keep their cover image. That reasoning still holds; only the
mechanism changed.

| File | Purpose |
| --- | --- |
| `namespace.yaml` | `linkedin-drip` namespace |
| `cronjob.yaml` | the job: clone `dev`, `publish.py next`, push the published marker |
| `secret.example.yaml` | template for the three required keys — encrypt before committing |
| `kustomization.yaml` | former entry point — see the banner above, do not apply |

Egress verification and rollback: see
[`plan-auto-post-linkedin.md`](../../plan-auto-post-linkedin.md) at the repo root.

To publish one post by hand — the supported manual path, no cluster involved:

```bash
python linkedin/publish.py status   # what is next
python linkedin/publish.py next     # publish it, writes the marker locally
```
