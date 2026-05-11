---
title: 'Creating an OpenClaw agent'
date: '2026-05-11'
draft: true
topics:
  - OpenClaw
  - AI tooling
tags:
  - openclaw
  - claude
  - agents
  - devops
  - tailscale
projects:
  - openclaw
categories:
  - IT
weight: 10 # Lower number = toper in the list
cover:
  image: "cover.svg"
  alt: 'Creating an OpenClaw agent'
  caption: ""
  relative: true
  hidden: true            # si true → pas de cover sur la page du post
  hiddenInList: true      # si true → pas de cover dans la liste des posts
  hiddenInSingle: false    # si true → pas de cover sur la page individuelle
---

## **Why a dedicated agent per project**

I started using OpenClaw as my main assistant on top of Claude. The first instinct is to keep one big session and dump every project into it. It is a bad idea. Conversation context bleeds across projects, memory mixes things that should never mix, and when I open `project-a` I do not want suggestions from `project-b` leaking in.

OpenClaw has a clean answer for that: **agents**. An agent is an isolated worker with its own workspace, state, and channel routing. One agent per project, and the rest follows from there.

This post walks through the mental model, the exact commands I use, and the gotchas I hit while setting this up on my own Linux host.

## **Mental model**

Three terms get thrown around. Worth pinning down before touching the CLI:

* **Agent** — isolated worker. Has a workspace directory, a model, its own session store, and routing rules for messaging channels. Use **one per project**.
* **Session** — a single conversation thread inside an agent. An agent can have many sessions (e.g. one per channel).
* **Subagent** — a short-lived helper spawned by the agent itself for delegation (search, refactor, code review). Not something you create up-front.

So when I say "I want a session for `My-blog`", what I actually want is an **agent** named `my-blog`, with the workspace pointing at the cloned repo.

## **The CLI surface**

OpenClaw exposes agent management under `openclaw agents`:

```bash
openclaw agents list      # show configured agents
openclaw agents add       # create a new agent (interactive)
openclaw agents bind      # route a messaging channel to an agent
openclaw agents bindings  # show channel → agent mappings
openclaw agents delete    # remove an agent (and its workspace, see below)
```

For day-to-day use, `add` and `bind` are the two that matter.

## **Creating an agent**

The non-interactive form is what I want from scripts:

```bash
openclaw agents add my-blog \
  --workspace /home/clowcode/repos/github/eliorion/My-blog \
  --model anthropic/claude-opus-4-6 \
  --non-interactive
```

A few things to know about this:

* The name is **normalized**. I passed `My-blog` and OpenClaw stored it as `my-blog`. Always reference the normalized id afterwards.
* The workspace **must exist** and ideally already be a git repo. OpenClaw does not clone for you. I clone first with `gh repo clone`, then point the agent at the directory.
* The agent gets its own dir under `~/.openclaw/agents/<id>/`, which holds its session store and per-agent state. The actual project files stay in the workspace.

After this, `openclaw agents list` shows the new agent and `~/.openclaw/openclaw.json` has a new entry under `agents.list`.

## **Channel routing — what works and what doesn't**

The reason agents are useful is that you can route incoming channels to them independently. If WhatsApp is bound to `my-blog`, anything I message myself on WhatsApp lands in the `my-blog` agent context, with the blog repo as the working directory.

```bash
openclaw agents bind --agent my-blog --bind whatsapp
openclaw agents bindings
```

The catch I did not see coming: **only messaging channels are routable this way**. WhatsApp, Telegram, Slack, Discord and friends, yes. The **TUI and the Control UI are not channels** in the routing sense — they always talk to whatever default agent the gateway resolves, or pick an agent through their own client-side switcher (Control UI has one; the TUI does not at all).

In practice, this means:

| Surface | Agent switching |
|---|---|
| WhatsApp / Telegram / Slack | `openclaw agents bind --agent <id> --bind <channel>` — works fully in band |
| Control UI | Open the agent switcher in the web UI |
| TUI | Not switchable live. Restart needed, with no `--agent` flag yet |

If you live in the TUI, this is annoying. The honest workaround is to use the Control UI for project work, or run the TUI from inside a small wrapper that sets the right defaults before launch.

## **Letting CLAUDE.md do the rest**

OpenClaw runs the agent through the `claude-cli` backend by default. That means the standard Claude conventions still apply: a `CLAUDE.md` at the root of the workspace is picked up automatically, and so is `.claude/settings.json`. I keep one `CLAUDE.md` per project that documents stack, commands, conventions, and a short rolling log of recent non-obvious changes. Both the agent and Claude Code on my laptop read the same file, which makes shared work between the two painless.

## **A helper script to glue it together**

Manually running `gh repo clone` then `openclaw agents add` then `openclaw agents bind` got old fast. I wrote a small `oc-project` helper that wraps the workflow:

```bash
oc-project clone <name|owner/repo>   # gh repo clone into ~/repos/github/<owner>/<repo>
oc-project ensure <name>             # clone if missing + create agent if missing
oc-project switch <name>             # bind current channel to the agent
oc-project back                      # bind back to main
oc-project list                      # agents + bindings
```

Defaults live in `~/.config/oc-project/config`:

```bash
OC_PROJECT_ROOT="$HOME/repos/github/eliorion"
OC_DEFAULT_OWNER="eliorion"
OC_DEFAULT_MODEL="anthropic/claude-opus-4-6"
```

A bare name like `my-app` resolves to `eliorion/my-app`. Pass `owner/repo` to override.

## **Gotcha I hit: `agents delete` deletes the workspace**

This one stung. `openclaw agents delete <id>` is described as "delete an agent and prune workspace/state". Reading the docs casually, I assumed "state" meant the per-agent session store. It does not. **It also wipes the workspace directory** — meaning every file in your project, gone, including untracked work.

The fix is simple but worth saying out loud: **always commit and push before deleting an agent**, or run `git stash` first. Better, treat `agents delete` like `rm -rf` on the workspace and act accordingly.

For the curious, I learned this by creating a `my-blog` agent on a fresh clone, deleting it ten seconds later because I wanted to keep blog work on `main`, and watching the `~/repos/github/eliorion/My-blog` directory disappear with it. Recovering was a single `gh repo clone` away, but uncommitted work would have been gone for good.

## **What I run when I start a new project**

The end-state for me looks like this:

```bash
# one-time install of the helper
chmod +x ~/bin/oc-project

# new project
oc-project ensure my-new-app
# if I want WhatsApp messages to land in that agent:
openclaw agents bind --agent my-new-app --bind whatsapp

# add a CLAUDE.md in the repo describing the stack + commands
$EDITOR ~/repos/github/eliorion/my-new-app/CLAUDE.md
```

That is the whole workflow. Per-project isolation, repo on disk, CLAUDE.md guiding the agent, and a single command to spin it up. Anything more elaborate has not been worth the maintenance so far.

## **Next steps**

A few things I want to wire next:

* Reverse direction: when I tell the agent "work on `<project>`" in chat, it should auto-resolve the repo, clone if needed, and rebind the channel. A small skill on the `main` agent can do this.
* A TUI wrapper that respects an `--agent` flag so I can stop relying on the Control UI for project switching.
* A `git pull --ff-only` prompt when re-entering an existing project, gated on a clean working tree.

I will write those up when they survive a few weeks of real use.
