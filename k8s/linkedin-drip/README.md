# linkedin-drip

Weekday CronJob that publishes the next queued LinkedIn draft from `linkedin/drafts/`.

It runs in the homelab cluster rather than on GitHub Actions because LinkedIn's WAF
rejects image uploads coming from GitHub's datacenter IPs — from the home connection
they succeed, so posts keep their cover image.

| File | Purpose |
| --- | --- |
| `namespace.yaml` | `linkedin-drip` namespace |
| `cronjob.yaml` | the job: clone `dev`, `publish.py next`, push the published marker |
| `secret.example.yaml` | template for the three required keys — encrypt before committing |
| `kustomization.yaml` | entry point for `kubectl apply -k` / GitOps |

Deployment steps, egress verification and rollback: see
[`plan-auto-post-linkedin.md`](../../plan-auto-post-linkedin.md) at the repo root.

Manual run:

```bash
kubectl create job -n linkedin-drip --from=cronjob/linkedin-drip drip-test
kubectl logs -n linkedin-drip -l job-name=drip-test -f
```
