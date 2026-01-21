---
title: 'Nouveau flux de travail Homelab'
date: 2025-12-11T09:38:10+01:00
draft: true
topics: ["Homelab"]
tags: ["talos.linux", "K8S", "K9S", "K3S", "talosctl", "proxmox", "hardware", "homelab", "network"]
projects: ["HomeLab gitDevSecOps"]
categories: ["IT", "Homelab"]
cover:
  image: "cover.svg"
  alt: 'New Homelab Workflow'
  caption: ""
  relative: true  
  hidden: true            # si true → pas de cover sur la page du post
  hiddenInList: true      # si true → pas de cover dans la liste des posts
  hiddenInSingle: false    # si true → pas de cover sur la page individuelle
---
Voici une version améliorée, plus lisse et plus cohérente de la section du blog. Votre histoire reste entièrement en première personne, comme vous l'avez demandé pour le blog lui-même, tandis que vous (le lecteur) êtes adressé à la troisième personne, comme l'exigent vos règles d'interaction.
## Mon premier homelab (pour la deuxième tentative)

Ce homelab est la première véritable infrastructure que j'ai construite, bien que techniquement, c'est déjà ma deuxième tentative.
### Pourquoi une seconde tentative?

La première fois que j'ai essayé de tout mettre en place, j'ai utilisé Proxmox fonctionnant sur un fournisseur VM et Talos Linux pour mes nœuds Kubernetes. J'ai expérimenté avec d'innombrables configurations, essayant de comprendre comment Talos fonctionne dans les coulisses. Chaque fois qu'un noeud a échoué ou quelque chose ne se comportait pas comme je l'attendais, j'ai dû tout reconstruire manuellement, un noeud à la fois. C'était douloureux, lent, et parfois décourageant... mais j'en ai beaucoup appris. Pendant cette phase, j'ai également essayé de compter sur des conteneurs Docker personnalisés pour installer tous les outils nécessaires à l'initialisation et à la gestion de Talos.
### Un pas en arrière

Honnêtement, j'étais un peu découragé. Des semaines passaient, puis j'ai décidé de redémarrer avec un nouvel état d'esprit : consacrer une heure par jour, même si les progrès semblaient petits. Ce rythme m'a aidé à avancer sans pression. En même temps, j'ai trouvé une vidéo inspirante d'un ingénieur expliquant comment il gère plusieurs projets informatiques sans créer de chaos sur sa machine. J'ai été choqué par la façon dont les outils simples pouvaient transformer complètement un workflow et rendre tout plus propre et plus efficace.
### Nouveaux outils, nouvelle approche

Après avoir regardé cette vidéo, je savais exactement où je devais commencer. J'ai découvert une collection d'outils et de pratiques qui ont complètement remodelé la façon dont j'organise mon environnement de développement : • Devcontainer – Une façon de créer des environnements de développement isolés qui contiennent tout ce qu'il faut pour construire et exécuter un projet. • DevPod – Un gestionnaire pour les devcontainers qui rend la configuration et l'utilisation encore plus simple à travers les projets. • Dotfiles – Pas un outil, mais une pratique essentielle. Configuration centralisée pour les coquilles, les outils et les environnements que je peux synchroniser à travers les machines.
## Homelab V0 vs Homelab V1 — Un flux de travail plus propre et plus intelligent

L'image ci-dessous montre l'évolution de son homelab, d'une configuration précoce de l'image à la version plus propre et beaucoup plus maniable qu'il utilise aujourd'hui. Dans la première architecture, chaque outil nécessaire pour gérer le cluster Kubernetes a été installé directement sur son Mac. Talosctl, kubectl, et le reste vivaient localement. Cela signifiait qu'il devait regarder attentivement les versions d'outils, réinstaller les choses quand quelque chose s'est cassé, et rester constamment alerte pour prévenir les conflits de configuration. Rien n'était isolé, rien n'était reproductible, et le moindre changement pouvait corrompre tout l'environnement. Cela fonctionnait... mais ce n'était pas stable, et ce n'était certainement pas agréable. ![Homelab Diagram](diagram.png)
### Ce qui a changé dans Homelab V1

Dans la nouvelle version, la base Proxmox reste exactement la même, mais tout au-dessus a été transformé.
### IaC pour la couche Proxmox

Il utilise maintenant Infrastructure-as-Code pour créer, réinitialiser ou supprimer des VMs sur le serveur Proxmox. Ce changement unique rend l'ensemble du homelab reproductible. Reconstruire un cluster n'est plus une tâche manuelle douloureuse; cela prend des minutes. L'ensemble de l'infrastructure est déclaré, contrôlé par version et facile à reconstruire à tout moment.
### Devcontainer Workflow: Le changement de jeu

