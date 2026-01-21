---
title: 'Premier pas dans le monde de Homelab'
date: 2025-08-31T14:51:29+02:00
draft: false
topics: ["Homelab"]
tags: ["talos.linux", "K8S", "K9S", "K3S", "talosctl", "proxmox", "hardware", "homelab", "network"]
projects: ["HomeLab gitDevSecOps"]
categories: ["IT", "Homelab"]
weight: 0 # Lower number = toper in the list
cover:
  image: "cover.svg"
  alt: "First Step in Homelab"
  caption: ""
  relative: true
  hidden: true            # si true → pas de cover sur la page du post
  hiddenInList: true      # si true → pas de cover dans la liste des posts
  hiddenInSingle: false    # si true → pas de cover sur la page individuelle
---
Le présent règlement entre en vigueur le jour suivant celui de sa publication au Journal officiel de l'Union européenne.
## Créer un laboratoire d'accueil pour apprendre les Kubernetes

Le présent règlement entre en vigueur le jour suivant celui de sa publication au Journal officiel de l'Union européenne.
### Pourquoi apprendre Kubernetes?

swit En tant qu'ingénieur logiciel axé sur les implémentations de bas niveau, j'ai réalisé que je ne comprenais pas pleinement comment les systèmes cloud modernes fonctionnent, ou comment des millions d'utilisateurs peuvent accéder à des quantités massives de services sans interruption. Ce qui me fascine le plus est l'élasticité de l'allocation des ressources. Pensez à Netflix: chaque soir, des millions de personnes se connectent en même temps pour regarder leurs séries préférées. Cela crée un énorme pic de trafic. Pourtant, tout fonctionne bien sans temps d'arrêt. Comment est-ce possible? Réponse: Kubernetes.
### Pourquoi un labo ?

J'ai toujours voulu avoir mon propre serveur, avec mon propre nom de domaine, pour héberger un site personnel. Mais je n'ai jamais vraiment pris le temps de le faire. Quand il s'agit d'apprendre une technologie complètement nouvelle, la meilleure façon est de pratiquer, de pratiquer et de pratiquer. Vous pouvez regarder chaque tutoriel dans le monde, mais si vous ne vous salirez jamais les mains en écrivant du code et en expérimentant, vous ne comprendrez jamais vraiment comment fonctionnent les outils, comment les configurer, les déboguer et trouver des solutions quand quelque chose casse.
### Matériel

J'avais besoin d'une machine avec suffisamment de RAM pour faire fonctionner plusieurs services, un GPU décent pour finir par construire mon propre Netflix Mini, et quelque chose de petit et silencieux. Après quelques recherches, j'ai choisi le Nipogi E3B avec 16 Go de RAM. À moins de 300 €, il me semblait être un point de départ parfait.
### Logiciels

Pour construire un cluster Kubernetes, vous avez besoin de plusieurs machines. Un seul serveur nu-métal n'est pas suffisant si vous voulez simuler une configuration de production du monde réel. La solution est d'exécuter un hyperviseur sur le serveur, permettant la création de plusieurs machines virtuelles (VMs). Avec cela, je peux construire un environnement réaliste avec plusieurs nœuds. J'ai choisi Proxmox pour exécuter et gérer tous mes VMs, ainsi que gérer le réseau interne. C'est l'une des façons les plus communes de configurer un labo domestique. En plus de cela, Proxmox fonctionne sur Linux, ce qui est une grande pratique si vous voulez plonger plus profondément dans Kubernetes.
### Architecture

