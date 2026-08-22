---
title: "CI Runners That Cannot Hurt Production"
date: 2026-05-28T09:00:00+02:00
draft: false
topics:
  - DevOps
  - Security
  - Homelab
tags:
  - github-actions
  - self-hosted-runners
  - docker
  - security
  - ci-cd
  - homelab
projects:
  - mve-itguard
categories:
  - IT
  - Security
weight: 2
cover:
  image: cover.svg
  alt: Self-hosted CI runners isolation
  caption: ""
  relative: true
  hidden: true
  hiddenInList: true
  hiddenInSingle: false
---

## The Risk of Self-Hosted Runners

GitHub-hosted runners are ephemeral virtual machines managed by GitHub. They have no access to your infrastructure, they disappear after each job, and any damage they could cause is contained to the workspace they checked out.

Self-hosted runners are different. They are processes — or in this case, containers — that live on your own hardware, connected to GitHub and waiting for jobs. When a workflow runs on a self-hosted runner, it executes code on your machine with whatever permissions that runner has.

For mve-itguard, the runners live on the production server. The deploy runner needs Docker access to bring services up and down. That is a significant capability: a process that can talk to Docker can read any container's environment variables, mount any volume, stop any service, or pull and run arbitrary images.

The question is not whether to accept that risk — the deploy runner genuinely needs Docker access to do its job. The question is how to constrain it precisely, and how to ensure that the CI runner — which runs on pull requests and could execute untrusted code — has no access to any of that.

---

## Three Runners, Three Roles

The runner setup is three containers, each with a specific and limited purpose:

```
┌──────────────────┐  ┌───────────────────┐  ┌───────────────────────┐
│   runner-ci      │  │  runner-rotate    │  │   runner-deploy       │
│                  │  │                   │  │                       │
│  label: ci       │  │  label: rotate    │  │  label: deploy        │
│  user: runner    │  │  user: root       │  │  user: 1001:1001      │
│                  │  │                   │  │                       │
│  no Docker       │  │  no Docker        │  │  DOCKER_HOST:         │
│  no prod access  │  │  mounts:          │  │    tcp://socket-proxy │
│                  │  │  /etc/sops/age    │  │                       │
└──────────────────┘  └───────────────────┘  └──────────┬────────────┘
                                                         │
                                             ┌───────────▼────────────┐
                                             │    socket-proxy        │
                                             │  (proxy-net, internal) │
                                             │  unix socket → dockerd │
                                             └────────────────────────┘
```

Each runner only has the permissions it needs for its specific job. Nothing more.

---

## runner-ci: No Docker, No Excuses

The CI runner handles lint and validation. It needs to run `yamllint`, `shellcheck`, `ansible-lint`, and `docker compose config`. None of those require a live Docker daemon connection — `docker compose config` only parses and validates the YAML, it does not contact Docker.

The runner has no Docker socket, no socket proxy, no prod volumes, no special mounts:

```yaml
runner-ci:
  build: .
  restart: unless-stopped
  env_file:
    - common.env
    - ci.env
  security_opt:
    - no-new-privileges:true
```

`no-new-privileges:true` prevents any process inside the container from gaining additional Linux capabilities through `setuid` binaries. It is a defence-in-depth measure: even if something inside the runner tried to escalate, it cannot.

This runner handles pull requests. If a contributor submits a PR with malicious code in a shell script or Makefile, the CI runner executes it in a sandboxed environment with no path to production. It can read the repository. It cannot touch anything else.

---

## socket-proxy: A Docker API Firewall

Rather than mounting the raw Docker socket into the deploy runner, a socket proxy sits between them.

```yaml
socket-proxy:
  image: tecnativa/docker-socket-proxy:latest
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock
  environment:
    CONTAINERS: 1
    IMAGES: 1
    NETWORKS: 1
    VOLUMES: 1
    POST: 1
    INFO: 1
    PING: 1
  networks:
    - proxy-net
  security_opt:
    - no-new-privileges:true
```

The proxy exposes only what `docker compose` needs to deploy services. Everything else — the build API, exec into containers, Swarm endpoints, system events, registry auth — is blocked at the proxy layer.

The proxy is on a dedicated internal network (`proxy-net`) that only `runner-deploy` can reach. No other container on the host can speak to it. The Docker socket itself stays mounted only into the proxy, not into any runner.

```
runner-deploy ──TCP:2375──▶ socket-proxy ──unix socket──▶ host dockerd
                             (proxy-net, internal)
```

The practical effect: if someone obtained code execution inside `runner-deploy`, they could issue `docker compose` commands — they could not `exec` into a container to steal secrets, could not read environment variables from a running service, could not access the full Docker API surface.

---

## runner-deploy: Constrained Docker Access

The deploy runner runs as user `1001:1001` — the `mve-itguard` service account that owns the application files. It is not root. It connects to Docker through the socket proxy only, not the raw socket.

```yaml
runner-deploy:
  build: .
  user: "1001:1001"
  env_file:
    - common.env
    - deploy.env
  environment:
    DOCKER_HOST: tcp://socket-proxy:2375
  volumes:
    - /opt/mve-itguard-work:/opt/mve-itguard-work
  networks:
    - default
    - proxy-net
  depends_on:
    - socket-proxy
```

The volume mount requires explanation. When `runner-deploy` runs `docker compose up`, it passes volume paths to the Docker daemon. The daemon resolves those paths on the **host** filesystem, not inside the runner container. This is Docker-out-of-Docker (DooD): the runner is a container, but it is talking to the host's Docker daemon, which has no knowledge of the runner's internal filesystem.

The workspace volume `/opt/mve-itguard-work` is mounted at the **same path** on both sides — inside the container and on the host. When Docker resolves `./config/homeassistant` to an absolute path like `/opt/mve-itguard-work/mve-itguard/mve-itguard/app/config/homeassistant`, that path exists on the host and Docker can bind-mount it into the target service container.

If the paths differed between host and container, the bind mounts would point to nonexistent locations on the host. Services would start but find empty config directories, or fail to start entirely. Identical mount paths on both sides is the requirement that makes DooD work for this use case.

---

## runner-rotate: Root for a Reason

The rotation runner needs to write `/etc/sops/age/keys.txt` on the host. That file is owned by root with mode 600. No privilege escalation trick can get around that — the runner genuinely needs root.

```yaml
runner-rotate:
  build: .
  user: root
  env_file:
    - common.env
    - rotate.env
  environment:
    RUNNER_ALLOW_RUNASROOT: "1"
  volumes:
    - /etc/sops/age:/etc/sops/age
```

`RUNNER_ALLOW_RUNASROOT` is required by the GitHub Actions runner binary — it refuses to start as root unless that variable is set. The rotation runner is the only place this is used.

This runner has no Docker access. It has one job: compare the AGE key hash and re-encrypt secrets if there is a mismatch. That job requires root access to one specific directory, and nothing else.

---

## GitHub App Authentication: No Long-Lived Tokens

Runner registration with GitHub traditionally uses a PAT (Personal Access Token). PATs have two problems: they are tied to a user account, and they are long-lived. A leaked PAT gives an attacker persistent access until it is manually revoked.

The runners here authenticate with a **GitHub App** instead. The process is:

```
container start
       │
       ▼
sign JWT  (RS256, App private key, 10-minute expiry)
       │
       ▼
POST /app/installations/{id}/access_tokens  →  installation token (1 hour)
       │
       ▼
POST /orgs/{org}/actions/runners/registration-token
       │
       ▼
./config.sh --token ...  →  runner registered
       │
container stop
       │
       ▼
./config.sh remove --token ...  →  runner deregistered
```

The credentials in `common.env.enc` are the GitHub App private key (base64-encoded), the App ID, and the Installation ID. These are used to generate a short-lived JWT, which is exchanged for an installation token, which is exchanged for a runner registration token. The registration token is valid for one hour and can only register runners — it has no other capabilities.

On shutdown, the runner deregisters itself using a freshly obtained removal token. If the container is killed unexpectedly, the runner entry in GitHub is left stale but harmless — the next startup uses `--replace` to overwrite it.

---

## One Image, Three Roles

All three runners are built from the same Dockerfile:

```dockerfile
FROM ghcr.io/actions/actions-runner:latest

RUN apt-get install -y yamllint shellcheck ansible-lint \
    docker-ce-cli docker-compose-plugin

# sops v3.12.2 + age v1.3.1 installed from upstream releases

COPY start /start
ENTRYPOINT ["/start"]
```

Every runner gets `docker-ce-cli` and `docker-compose-plugin` installed, even `runner-ci`. Having the CLI installed does not grant Docker access — without a valid `DOCKER_HOST` or socket mount, the `docker` command fails. `runner-ci` has neither, so the CLI is inert.

Building one image simplifies maintenance. Updating a dependency means rebuilding once, not maintaining parallel Dockerfiles. The capabilities each runner actually has come from the Compose configuration, not from what is installed in the image.

---

## What This Achieves

The overall security posture is:

- **CI runner**: runs untrusted code (PRs), cannot reach Docker or production, cannot escalate
- **Deploy runner**: Docker access via restricted proxy, runs as non-root, workspace paths prevent filesystem escape
- **Rotate runner**: root access to exactly one directory, no Docker, no deploy capability
- **Socket proxy**: Docker API firewall between runners and the daemon, on an isolated internal network

A compromised CI job cannot reach production. A compromised deploy job can issue compose commands but not gain full Docker daemon access. The rotation job's blast radius is limited to the AGE key directory.

No individual runner has enough access to cause serious damage on its own. That combination of isolation and least privilege is the goal.

---

*Next in this series: [One Command to Provision a Server]({{< relref "2026-05-29 - mve-itguard-bootstrap/index.md" >}}) — how the bootstrap script provisions a fresh Debian server end-to-end with a single command.*
