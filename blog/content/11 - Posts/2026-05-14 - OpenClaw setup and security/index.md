---
title: 'OpenClaw setup and security'
date: '2026-05-14'
draft: false
topics:
  - Homelab
  - Security
  - AI
tags:
  - openclaw
  - tailscale
  - homelab
  - security
  - self-hosted
projects:
  - HomeLab gitDevSecOps
categories:
  - IT
  - Homelab
weight: 10
cover:
  image: "cover.svg"
  alt: 'OpenClaw setup and security'
  caption: ""
  relative: true
  hidden: true
  hiddenInList: true
  hiddenInSingle: false
---

## **Why I run OpenClaw at home**

I want an AI agent who can read my files, run commands, and help me on my homelab project, but I don’t want to send my workspace to a SaaS or open a public port on my router. OpenClaw is a self-hosted agent platform: it run on my Linux box, hold the agent sessions, and expose a small control UI to interact with it from any of my devices.

The catch is that this agent has real power on the host. It can read files, execute shell commands, modify code, and even spawn subagents. So the security of the access path matter as much as the agent it self.

## **What is in the setup**

On the host, three pieces work together:

* The **OpenClaw agent** running on my Linux server, with its workspace under `~/.openclaw/workspace`
* The **gateway** who expose a small HTTP API and the control UI
* **Tailscale**, who give me a private mesh network between all my devices

I don’t use a public domain, no reverse proxy, no port forwarding on the router. The gateway is never reachable from the public internet.

## **The security issue I want to prevent**

The risk is simple: if the OpenClaw control plane is reachable from the public internet, then anyone who find the endpoint can try to talk to the agent. And the agent is not a static web app, it is a process with shell access on my machine. A weak auth, a bug in the gateway, or a leaked token become directly a remote code execution on the host.

The classic mistakes I want to avoid:

* expose the gateway port with a port forward on the router
* put it behind a public reverse proxy with only a password
* rely only on the application auth to protect a shell-executing service
* trust a public TLS cert as if it was an access control

A public AI agent endpoint is not the same as a public blog. The blog only serve static files, the worst case is defacement. The agent can `rm -rf`, read SSH keys, push to my repos. So the network layer it self must reject anyone who is not on my private network.

## **How Tailscale solve this**

Tailscale build a private WireGuard mesh between my devices. Each device get a stable IP on the `100.x.y.z` range, and only the devices I authorise can reach the others. There is no public IP, no port to scan, nothing visible from the internet.

The interesting part is that this is enforce at the network layer, before the gateway code even run. Even if my gateway have a zero-day, the attacker can’t reach the socket because the socket is not exposed on a public interface.

## **Gateway bound directly on the tailnet**

The simplest way to do this is to bind the gateway directly on the Tailscale interface. In my `~/.openclaw/openclaw.json`, the gateway is configure like this:

```json
{
  "gateway": {
    "bind": "tailnet",
    "tailscale": {
      "mode": "off"
    }
  }
}
```

With `bind: "tailnet"`, the gateway listen only on the Tailscale IP of the host (in my case `100.95.35.87:18789`). It don’t listen on `0.0.0.0`, so even if my firewall is misconfigure, the public interface have nothing to expose.

I previously try `tailscale.mode: "serve"` to get a nice HTTPS URL with the `.ts.net` domain, but it require `sudo` to manage the Tailscale operator, and I prefer to keep the setup simple. Direct bind work the same from my point of view, with one less moving piece.

## **Why not just put a password and call it a day**

A password on a public endpoint is one bug away from being useless. With Tailscale, the access control is move on a different layer:

* the network layer reject the connection before anything else
* the application auth is the second line, not the first
* if my Tailscale account is compromise, the attacker still need my device to be authorise on the tailnet

It’s the classic principle of "don’t expose what you don’t need to expose". My AI agent is for me, on my devices, so there is no reason to make it reachable from the internet.

## **What I keep in mind**

This setup is not magical. There is still things to watch:

* keep the Tailscale daemon up to date
* don’t share the tailnet with random people
* be careful with the `controlUi.allowedOrigins` list, who decide who can talk to the UI
* don’t leak my OpenClaw config file, it contain the bind address and other metadata

But with this layout, the attack surface is reduce to almost nothing from the public internet point of view. The agent stay private, my homelab stay calm, and I can focus on the actual work I want the agent to do.
