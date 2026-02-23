---
title: 'Pourquoi apprendre le linux avant la containerisation'
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
# **Quand 2 Go de RAM ont brisé mon environnement de Dev**

Une de mes premières percées réelles dans l'apprentissage de Linux s'est produite lorsque j'ai commencé à travailler sérieusement avec des conteneurs. Au début, j'ai lutté avec le Docker CLI. Il me semblait abstrait et parfois inintuitif. Mais plus j'ai appris sur Linux — processus, espaces de noms, cgroups, systèmes de fichiers — plus les conteneurs ont commencé à avoir du sens. La conteneurisation n'est pas magique. C'est Linux. Compréhension qui a tout changé.
## **De Docker Desktop à Rancher Desktop**

Pour mes projets, en particulier mon homelab, j'utilise DevPod et devcontainers sur mon Mac. Jusqu'à récemment, j'ai tout exécuté sur Docker Desktop. Lorsque j'ai rejoint la communauté KubeCraft pour approfondir mes connaissances Linux et Kubernetes, j'ai décidé de passer à Rancher Desktop. Une raison était que je voulais lancer un cluster local K3s et expérimenter plus profondément avec Kubernetes d'une manière qui se sentait plus proche des environnements de production.
## **Quand tout s'est effondré**

J'ai essayé de recréer mon devcontainer homelab. J'ai échoué. J'ai essayé un autre devcontainer utilisé pour bootstrap mes fichiers dot avec Chezmoi. Il a échoué aussi. Pendant plusieurs jours, j'ai débogé ce que je pensais être un problème de script. J'ai examiné mon processus d'initialisation Chezmoi, inspecté les journaux, et interrogé ma configuration. Finalement, j'ai découvert la cause réelle: un problème de mémoire. L'une des commandes de mon script d'initialisation était tuée par le noyau Linux avant qu'il ne puisse être terminé. Pas parce que le script était incorrect, mais parce qu'il n'avait pas assez de mémoire disponible. C'était déroutant.
## **La vraie différence : l'isolement des ressources**

La réponse n'était pas dans mon code. C'était dans la plate-forme. Sur macOS, les conteneurs ne fonctionnent pas nativement sur le noyau hôte. Docker Desktop et Rancher Desktop dépendent tous deux d'une machine virtuelle Linux sous le capot. Cependant, Rancher Desktop rend l'allocation des ressources plus explicite. Dans mon cas, Rancher Desktop a été configuré avec seulement 2 Go de RAM alloué à son VM Linux. À l'intérieur de ce VM, j'exécutais : - Mon cluster K3s - Plusieurs conteneurs créés lors d'expériences Kubernetes - Mon environnement de devcontainer Tout cela partageait la même limite mémoire de 2 Go. Donc, quand j'ai essayé de faire tourner mon devcontainer homelab, il n'y avait tout simplement pas assez de mémoire disponible.
## **La vraie leçon**

Cette expérience a renforcé quelque chose de fondamental pour moi en tant qu'aspirant DevOps / Platform Engineer: Quand quelque chose casse, ne blâmez pas immédiatement le code. Surtout après avoir changé d'outils, d'exécutions ou d'infrastructure. Différents outils peuvent introduire: - Différents modèles d'isolement - Différentes limites de ressources - Différentes contraintes architecturales Si l'implémentation sous-jacente change, le domaine de défaillance change aussi.
## **Améliorer mon état d'esprit de débogage**

À partir de maintenant, lorsque je change d'outils, d'exécutions de conteneurs ou de composants d'infrastructure, je veux : 1. comprendre l'architecture d'abord. 2. identifier les limites des ressources (CPU, mémoire, stockage, réseautage). 3. vérifier les contraintes d'environnement avant de plonger dans le débogage de l'application. Déboguer n'est pas seulement de lire les journaux. Il s'agit d'identifier la bonne couche où se produit l'échec.
## **Construire une habitude de suivi des enjeux**

