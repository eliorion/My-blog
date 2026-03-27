---
title: '{{ index (split .File.ContentBaseName " - ") 1 | title }}'
date: '{{ time.Now.Format "2006-01-02" }}'
draft: false
topics:
  - Kubernetes
tags:
  - talos.linux
  - K8S
  - K9S
  - K3S
  - talosctl
  - proxmox
  - hardware
  - homelab
  - network
projects:

categories:
  - IT
  - Homelab
weight: 10 # Lower number = toper in the list
cover:
  image: "cover.png"
  alt: '{{ index (split .File.ContentBaseName " - ") 1 | title }}'
  caption: ""
  relative: true  
  hidden: true            # si true → pas de cover sur la page du post
  hiddenInList: true      # si true → pas de cover dans la liste des posts
  hiddenInSingle: false    # si true → pas de cover sur la page individuelle
---
---
