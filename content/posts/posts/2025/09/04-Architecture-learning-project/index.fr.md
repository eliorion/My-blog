---
title: "Projet d'apprentissage homelab : l'architecture"
date: 2025-09-15T22:50:16+02:00
draft: false
topics: ["Homelab"]
tags: ["talos.linux", "K8S", "K9S", "K3S", "talosctl", "proxmox", "hardware", "homelab", "network"]
projects: ["HomeLab gitDevSecOps"]
categories: ["IT", "Homelab"]
cover:
  image: "cover.svg"
  alt: "Architecture Learning Project"
  caption: ""
  relative: true  
  hidden: true            # si true → pas de cover sur la page du post
  hiddenInList: true      # si true → pas de cover dans la liste des posts
  hiddenInSingle: false    # si true → pas de cover sur la page individuelle
---
## Bâtir un laboratoire domestique pour apprendre les Kubernetes

Je voulais apprendre Kubernetes – vraiment apprendre, pas seulement suivre quelques tutoriels. Pendant la recherche, j'ai remarqué que beaucoup de gens construisent leurs propres laboratoires à domicile pour exécuter des services cloud ou des applications personnalisées. Cela m'a inspiré de mettre en place un laboratoire à domicile complet moi-même: d'abord pour exécuter des services de base comme Nextcloud ou OpenProject, puis pour expérimenter avec un pipeline DevSecOps complet.
## Première étape

Pour bien comprendre Kubernetes, j'avais besoin de quelque chose près de l'infrastructure du monde réel. L'achat de trois serveurs physiques ou plus n'était pas possible, donc j'ai décidé de tout créer sur une seule machine à l'aide de plusieurs machines virtuelles (VM).
## Hyperviseur

Le matériel est modeste: un petit PC avec 16 Go de RAM et un lecteur de 500 Go. Pourtant, cela suffit pour démarrer. J'ai choisi Proxmox comme hyperviseur parce qu'il est facile à configurer et basé sur Debian, une distribution Linux que je connais déjà.
## Architecture

Pour que le labo se sente comme une véritable installation de production, j'ai fixé quelques objectifs : • Administration sécurisée afin que je puisse gérer le système en toute sécurité à partir de n'importe où. • Garder tous les outils de développement sur le serveur afin que je puisse travailler à partir de n'importe quel ordinateur. • Simuler un environnement Kubernetes réaliste, y compris un équilibreur de charge devant le cluster. Voici l'architecture matérielle : ![Homelab Diagram](Hardware-architecture.excalidraw.light.svg)
### Réseaux

Le serveur Proxmox utilise trois réseaux virtuels distincts : 1. Net0 – Connecté à l'interface réseau physique pour l'accès à Internet. Il s'agit de la première couche de pare-feu pour le cluster. Seuls les services orientés client sont exposés ici, et il héberge également le terminal VPN. 2. Net1 – Le réseau d'administration, accessible uniquement via le VPN. Il contient le cluster Kubernetes et un gestionnaire VM exécutant le jeu d'outils Talos. Il héberge également les tableaux de bord, l'enregistrement et la gestion du stockage. 3. Net2 – Dédié à l'équilibreur de charge et au cluster pour le trafic d'applications.
### Balanceur de charge

Dans la production, un fournisseur de cloud fournit généralement l'équilibreur de charge. Pour des fins d'apprentissage, je voulais construire mon propre. Parce que ce service est léger, je l'exécute dans un conteneur au lieu d'un VM.
### VPN

Le conteneur VPN est essentiel pour la sécurité. Pour déployer ou administrer n'importe quoi dans le cluster, je dois atteindre le réseau Net1 en toute sécurité de l'extérieur.
### Gestionnaire de serveur

Un VM agit comme gestionnaire de serveur. Il héberge le kit d'outils Talos pour gérer les nœuds du cluster et exécute également le système GitOps que j'utilise pour administrer le cluster.
## Configuration du serveur Proxmox

