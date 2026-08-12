---
title: "Moving My Blog and LinkedIn Automation into n8n"
date: 2026-08-12T09:00:00+02:00
draft: false
topics:
  - Homelab
  - DevOps
tags:
  - n8n
  - github
  - ai-gateway
  - datatable
  - tailnet
  - ci-cd
  - git
  - homelab
projects:
  - blog
categories:
  - IT
  - Homelab
weight: 2
cover:
  image: cover.svg
  alt: "A screenshot of an n8n workflow with GitHub, Code, and AI nodes connected in a flow"
  caption: ""
  relative: true
  hidden: true
  hiddenInList: true
  hiddenInSingle: false
---

## Moving My Blog and LinkedIn Automation into n8n

I used to run my blog and LinkedIn automation as a messy patchwork: two Python scripts, a Kubernetes CronJob for daily triggers, and three separate GitHub Actions workflows for linting, building, and posting. It worked, but it was fragile. Every morning, I’d push a `[skip ci]` commit just to bump the queue state in Git frontmatter. Then, if my laptop and CI tried to push to `dev` at the same time, I’d get a rebase-retry loop—three attempts max—before the whole thing stalled. It was dumb, but it was mine.

I ported the whole thing into n8n. Not as a tutorial. As a replacement. One automation hub. No more CronJob. No more GitHub Actions splitting logic across repos. Just n8n running on my Proxmox homelab, talking to my Tailnet, and calling my internal AI gateway.

First win: the LinkedIn queue state. It used to live in git frontmatter—one marker commit per day. Now it’s in an n8n Data Table. A simple key-value store inside the n8n instance. No more `[skip ci]` commits. No more push contention between my laptop and CI. The table holds the next post slug, the LinkedIn post text, and a status flag. When the workflow runs, it reads the row, processes it, and moves to the next. Clean. Atomic. No git noise.

Second win: AI calls. I swapped hardcoded model names like `gpt-4o` or `claude-3-sonnet` for tier names: `ai/low`, `ai/normal`, `ai/high`. These map to models in my internal `ai-gateway` service. If I want to switch from OpenAI to Anthropic tomorrow, I change one config file in the gateway. Zero workflow edits. That’s the kind of indirection I wish I’d added years ago.

Now the gotchas.

Gotcha 1: the n8n GitHub node doesn’t have a “create branch” operation. I spent 20 minutes staring at the node UI, convinced I was missing something. Nope. To create a branch, you have to: GET `git/ref/heads/dev` to get the latest SHA, then POST to `git/refs` with `{ "ref": "refs/heads/post/<slug>", "sha": "<sha-from-get>" }`. I built that as two separate HTTP Request nodes. It’s not elegant, but it works. I wrapped it in a sub-workflow called “Create Git Branch” so I don’t have to think about it again.

Gotcha 2: n8n form URLs are public by default. My blog post form is only reachable via my Tailnet (Tailscale), so I dropped Basic Auth. But if you expose n8n to the internet without auth? That’s a footgun. Anyone can submit a form and trigger your workflows. I added a note in my instance docs: "If you ever open port 5678 to WAN, re-enable auth immediately."

Gotcha 3: my first test run had empty inputs. The workflow cheerfully created a branch named `post/null`, committed an empty Markdown file, and opened a PR titled "Add post/null". GitHub Actions ran lint on an empty file and passed. It was a silent failure. I added a Code node right after the form trigger that checks: if `title === "" || notes === "" || body === ""`, throw new Error("Missing required fields: title, notes, or body"). Now it fails fast. No ghost branches.

Gotcha 4: `ai/high` was resolving to a free-tier model on my gateway—probably a rate-limited fallback—and hitting 112s latency. The sub-workflow timeout is 180s, but with retries and overhead, it still blew through. I didn’t realize the gateway was falling back to a smaller model under load. I added a timeout check in the AI node and logged the actual model being used. Now I monitor the gateway’s model mapping and manually promote `ai/high` to a paid tier when I need reliability. No more silent downgrades.

The whole thing now runs in n8n: form submission → validation → branch creation → AI generation (via gateway) → commit → PR → LinkedIn drip (queued in Data Table) → merge on approval. It’s slower to set up than a cron job, but it’s visible, traceable, and I can tweak any step without touching YAML or rebasing.

I still have the old Python scripts archived. Just in case. But I haven’t touched them in three weeks. The Data Table is empty of marker commits. The GitHub history is clean. And for the first time, my LinkedIn posts go out at 8 a.m. sharp—not because CI raced my laptop, but because n8n told it to.
