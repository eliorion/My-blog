---
title: 'Persistence volume in Kubernetes'
date: 2025-12-11T09:38:10+01:00
draft: false
topics: ["Homelab"]
tags: ["talos.linux", "K8S", "TrueNAS", "pulumi", "talosctl", "proxmox", "hardware", "homelab", "IaC", "nfs", "pvc"]
projects: ["HomeLab gitDevSecOps"]
categories: ["IT", "Homelab"]
weight: 2 # Lower number = toper in the list
cover:
  image: "cover.svg"
  alt: 'Persistence data with TrueNAS'
  caption: ""
  relative: true
  hidden: true            # si true → pas de cover sur la page du post
  hiddenInList: true      # si true → pas de cover dans la liste des posts
  hiddenInSingle: false    # si true → pas de cover sur la page individuelle
---


## Learn persistent volume on kubernetes

My status in my learning session on kubernetes :

| Name | Learning stat | Commentary |
|------|---------------|------------|
| Pods |  | Create, delete, logs |
| Deployment | 🟢 | Consepts understood|
| nfs-driver | 🟢 | In place to use TrueNAS NFS shared storage |
| Calico | 🟠 | Basic functionality; not fully mastered but operational |
| Service | 🟠 | ClusterIP and NodePort understood; LoadBalancer and ExternalName not yet used |
| Traefix | 🟠 | Learning, used with Service LoadBalancer |
| API gateway | 🟠 | Learning, used with Service LoadBalancer |
| PV | 🔴 | Persistent volumes not yet required |
| PVC | 🔴 | Persistent volume claims not yet required |

I hadn't needed to create a PV and a PVC. So, I had to learn how to access this ressource in my Talos Kubernetes cluster.

The fastest way is to use the nodes storage to create PV. But, this is not the best way to store data. If you create a PV on one node and a pod in another node needed this PV, if the first node is down, the service can't access to the data.

The other problem is the complexity to create backup and to have relible data.
