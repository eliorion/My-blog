---
title: Why learn linux before containerisation
date: 2026-02-23T09:38:10+01:00
draft: false
topics:
  - DevOps
tags:
  - Mindset
  - docker_desktop
  - rancher_desktop
  - container
projects:
  - HomeLab gitDevSecOps
categories:
  - IT
weight: 2
cover:
  image: cover.svg
  alt: homelab
  caption: ""
  relative: true
  hidden: true
  hiddenInList: true
  hiddenInSingle: false
---
# **When 2 GB of RAM Broke My Dev Environment**

One of my first real breakthroughs in learning Linux happened when I started working seriously with containers.

At first, I struggled with the Docker CLI. It felt abstract and sometimes unintuitive. But the more I learned about Linux — processes, namespaces, cgroups, filesystems — the more containers started to make sense. Containerization is not magic. It is Linux.

Understanding that changed everything.

## **From Docker Desktop to Rancher Desktop**

For my projects, especially my homelab, I use DevPod and devcontainers on my Mac. Until recently, I was running everything on Docker Desktop.

When I joined the KubeCraft community to deepen my Linux and Kubernetes knowledge, I decided to switch to Rancher Desktop. One reason was that I wanted to run a local K3s cluster and experiment more deeply with Kubernetes in a way that felt closer to production environments.

The course was excellent. Everything worked smoothly. I was progressing well.

Until I went back to my original devcontainer setup.

## **When Everything Broke**

I tried to recreate my homelab devcontainer.
It failed.
I tried another devcontainer used to bootstrap my dotfiles with Chezmoi.
It failed too.

For several days, I debugged what I thought was a script issue. I reviewed my Chezmoi initialization process, inspected logs, and questioned my configuration.

Eventually, I discovered the real cause: a memory issue.

One of the commands in my initialization script was being killed by the Linux kernel before it could complete. Not because the script was incorrect, but because it didn’t have enough memory available.

That was confusing.

My Mac had plenty of free memory. So why was the process being killed?

## **The Real Difference: Resource Isolation**

The answer was not in my code. It was in the platform.

On macOS, containers do not run natively on the host kernel. Both Docker Desktop and Rancher Desktop rely on a Linux virtual machine under the hood. However, Rancher Desktop makes resource allocation more explicit.

In my case, Rancher Desktop was configured with only 2 GB of RAM allocated to its Linux VM.
Inside that VM, I was running:

- My K3s cluster
- Several containers created during Kubernetes experiments
- My devcontainer environments

All of that shared the same 2 GB memory limit.
So when I tried to spin up my homelab devcontainer, there simply wasn’t enough memory available. The kernel’s OOM killer terminated my process.

The issue wasn’t in my script.
It was in my infrastructure constraints.
Once I deleted the K3s cluster and freed memory inside the VM, everything worked again.

## **The Real Lesson**

This experience reinforced something fundamental for me as an aspiring DevOps / Platform Engineer:

When something breaks, don’t immediately blame the code.
Especially after changing tools, runtimes, or infrastructure.
Different tools may introduce:

- Different isolation models
- Different resource limits
- Different architectural constraints

If the underlying implementation changes, the failure domain changes too.

In my case, I was debugging at the application layer when the problem was at the virtualization layer.

That mismatch cost me several days.

## **Improving My Debugging Mindset**

From now on, when I switch tools, container runtimes, or infrastructure components, I want to:
1. Understand the architecture first.
2. Identify resource boundaries (CPU, memory, storage, networking).
3. Verify environment constraints before diving into application debugging.

Debugging is not just about reading logs.

It is about identifying the correct layer where the failure occurs.

Application layer?
Container layer?
Runtime layer?
Virtualization layer?
Host layer?

That distinction matters.

## **Building an Issue Tracking Habit**

To avoid repeating the same mistakes, I am also standardizing an issue template for myself.

When I encounter a significant technical issue, I want to document:

- Context
- Environment
- Symptoms
- Root cause
- Resolution
- Lessons learned

This will help me build a personal knowledge base over time. Not just to fix problems faster, but to think more systematically.

Because in platform engineering, understanding the system is often more important than writing the code.
