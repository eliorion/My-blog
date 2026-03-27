---
title: First GitOps implementation
date: 2026-03-04T09:38:10+01:00
draft: false
topics:
  - DevOps
  - Homelab
  - GitOps
tags:
  - GitOps
  - blog
  - homelab
  - hardware
  - K3S
  - K8S
projects:
  - HomeLab gitDevSecOps
categories:
  - IT
  - Homelab
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

## **KubeCraft Course**

After completing the first Kubernetes course, where I deployed a basic K3s cluster on Rancher Desktop, I moved to the next level: a homelab course focused on building a fully GitOps-based K3s cluster on a Debian VM, hosting real self-hosted applications exposed to the internet.

### **What to Expect at the End?**

The final goal is to deploy a self-hosted **Linkding** application accessible from the internet using a custom domain name.

To achieve this setup, the following components are required:

- A domain name (I use OVH as the provider, with DNS managed by Cloudflare)

- A server (Raspberry Pi, old laptop, VM, etc.)

- A Cloudflare account (for tunnel access)

- A K3s cluster (running on my VM in this case)

- A complete monitoring stack (Prometheus, Grafana, etc.)

- A remote Git repository provider (I use GitHub)

---

## **Single-Node GitOps Project**

This project is designed for learning purposes. My real homelab architecture will not remain single-node in the long term. However, this simplified setup gives me confidence to later deploy a more solid and secure production-like homelab for daily use.

For this learning project, I use:

- A single Kubernetes node

- A single Git repository

- A simplified GitOps architecture

This approach allows me to build strong foundations in GitOps principles before scaling further.

---

## **Hardware**

For now, I use my Proxmox server to deploy a K3s instance.

I created a single VM with:

- 50 GB of storage

- 2 GB of RAM

Since I am only deploying lightweight self-hosted applications, powerful hardware is not required at this stage.

---

## **Operating System**

I chose Debian for the VM because I personally prefer it over Ubuntu.

I do not use a graphical interface. A Debian CLI installation is sufficient to:

- Install K3s

- Perform Kubernetes configuration

- Troubleshoot at the system level

One important objective of this setup is to retain full root access so I can deeply understand how K3s works internally, inspect processes, and observe how the system behaves in a production-like environment.

---

## **K3s**

K3s is a lightweight Kubernetes distribution designed for simplicity and efficiency.

It is also used internally by Rancher Desktop, which makes it a logical choice for consistency between local development and VM-based deployment.

For learning Kubernetes fundamentals without unnecessary complexity, K3s is an excellent option.

---

# **GitOps Architecture**

As mentioned earlier, this project uses a single Git repository following the official Flux recommendation for structuring repositories:

<https://fluxcd.io/flux/guides/repository-structure/>

This architecture keeps everything declarative and centralized in Git.

---

## **FluxCD**

### **What Is It?**

FluxCD is a GitOps operator that runs inside a Kubernetes cluster.

Its purpose is to continuously reconcile the cluster state with the desired state defined in a Git repository.

![[GitOps.svg]]

Instead of manually applying manifests using:

```
kubectl apply -f ...
```

Flux automatically:

- Monitors the Git repository

- Detects changes

- Applies them to the cluster

- Removes resources that were deleted from Git

Git becomes the single source of truth.

This model is very similar to Kubernetes’ own reconciliation logic. When using kubectl, you declare the desired state. Kubernetes then works to match the current state to that desired state.

Flux extends this idea by making Git the declarative interface.

---

## **Bootstrapping Flux**

The Flux documentation is well designed and contains many examples.

Since this project is built from scratch, bootstrapping was straightforward.

Using:

```
flux bootstrap
```

Flux installs itself into the cluster and connects to the Git repository.

This command saves a significant amount of time and avoids many potential configuration mistakes. After bootstrapping, only additional configuration is required to complete the setup.

---

## **How the Repository Works**

Here is the base directory structure of my learning GitOps cluster:

```
|-- apps
|-- clusters
|-- infrastructure
|-- monitoring
|-- documentations
```

The logic works as follows:

1. Flux is bootstrapped in clusters/staging/flux-system and watches this Git repository.

2. Git is the single source of truth; the cluster only reflects what is declared in Git.

3. In clusters/staging/, three Flux Kustomization objects are defined:

    - apps.yaml
    - infrastructure.yaml
    - monitoring.yaml

4. Each Flux Kustomization points to a specific path in the repository.

5. Flux reads that path and executes a Kustomize build.

6. The kustomization.yaml files inside those directories define which resources belong together.

7. The base folders contain generic manifests.

8. The staging folders override base configurations.

9. Flux applies the rendered manifests to the cluster.

10. With prune: true, resources removed from Git are also deleted from the cluster.

This reconciliation loop runs continuously, ensuring that the cluster always matches the Git repository.

