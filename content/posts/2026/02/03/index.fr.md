---
title: 'Première mise en œuvre GitOps'
date: 2026-03-04T09:38:10+01:00
draft: false
topics:
  - DevOps
  - Homelab
  - GitOps
tags:
  - GitOps
  - blo
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
---
---
---
---
---
---
---
---
Le présent règlement entre en vigueur le jour suivant celui de sa publication au Journal officiel de l'Union européenne.
## **Cours de radeau de bureau**

Après avoir terminé le premier cours Kubernetes, où j'ai déployé un cluster K3s de base sur Rancher Desktop, j'ai passé au niveau suivant : un cours homelab axé sur la construction d'un cluster K3s entièrement basé sur GitOps sur une VM Debian, hébergeant de vraies applications autonomes exposées à Internet.
### **À quoi s'attendre à la fin?**

Le but final est de déployer une application auto-installée **Linkding** accessible depuis Internet en utilisant un nom de domaine personnalisé. Pour réaliser cette configuration, les composants suivants sont requis : - Un nom de domaine (j'utilise OVH comme fournisseur, avec DNS géré par Cloudflare) - Un serveur (Raspberry Pi, ancien ordinateur portable, VM, etc.) - Un compte Cloudflare (pour l'accès tunnel) - Un cluster K3s (qui fonctionne sur mon VM dans ce cas) - Une pile de surveillance complète (Prometheus, Grafana, etc.) - Un fournisseur de dépôt Git distant (j'utilise GitHub)
## **Projet GitOps mono-nœud**

Ce projet est conçu à des fins d'apprentissage. Ma véritable architecture de homelab ne restera pas un seul nœud à long terme. Cependant, cette configuration simplifiée me donne confiance pour déployer plus tard un homelab plus solide et plus sécurisé comme une production pour une utilisation quotidienne. Pour ce projet d'apprentissage, j'utilise : - Un seul nœud Kubernetes - Un dépôt Git unique - Une architecture GitOps simplifiée Cette approche me permet de construire des fondations solides dans les principes GitOps avant d'augmenter l'échelle.
## **Horloge**

Pour l'instant, j'utilise mon serveur Proxmox pour déployer une instance K3. J'ai créé un seul VM avec : - 50 Go de stockage - 2 Go de RAM Comme je ne déploie que des applications légères auto-portées, un matériel puissant n'est pas nécessaire à ce stade.
## **Système d'exploitation**

J'ai choisi Debian pour la VM parce que je la préfère personnellement à Ubuntu. Je n'utilise pas d'interface graphique. Une installation Debian CLI suffit pour : - installer K3s - effectuer la configuration de Kubernetes - résoudre les problèmes au niveau du système Un objectif important de cette configuration est de conserver un accès root complet afin que je puisse comprendre en profondeur comment K3s fonctionne en interne, inspecter les processus et observer comment le système se comporte dans un environnement similaire à celui de la production.
## **K3s**

K3s est une distribution Kubernetes légère conçue pour la simplicité et l'efficacité. Elle est également utilisée en interne par Rancher Desktop, ce qui en fait un choix logique pour la cohérence entre le développement local et le déploiement basé sur VM. Pour apprendre Kubernetes fondamentaux sans complexité inutile, K3s est une excellente option.
# **Architecture GitOps**

Comme mentionné précédemment, ce projet utilise un seul dépôt Git suivant la recommandation officielle Flux pour structurer les dépôts : https://fluxcd.io/flux/guides/repository-structure/ Cette architecture maintient tout ce qui est déclaratif et centralisé dans Git.
## * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *

Le présent règlement entre en vigueur le jour suivant celui de sa publication au Journal officiel de l'Union européenne.
### **Qu'est-ce que c'est?**

FluxCD est un opérateur GitOps qui fonctionne à l'intérieur d'un cluster Kubernetes. Son but est de concilier en permanence l'état du cluster avec l'état souhaité défini dans un dépôt Git. ![[[[GitOps.svg]]] Au lieu d'appliquer manuellement des manifestes en utilisant : `` kubectl appliquer -f ... `` Flux automatiquement : - Surveille le dépôt Git - Détecte les modifications - Les applique au cluster - Supprime les ressources qui ont été supprimées de Git Git devient la seule source de vérité. Ce modèle est très similaire à Kubernetes propre logique de réconciliation. Lorsque vous utilisez kubectl, vous déclarez l'état souhaité. Kubernetes fonctionne alors pour correspondre à l'état actuel à cet état souhaité. Flux étend cette idée en faisant de Git l'interface déclarative.
## **Flux d'embouteillage**

La documentation Flux est bien conçue et contient de nombreux exemples. Comme ce projet est construit à partir de zéro, bootstrapping était simple. Utilisation: `` flux bootstrap ``` Flux s'installe dans le cluster et se connecte au dépôt Git. Cette commande permet d'économiser beaucoup de temps et évite de nombreuses erreurs de configuration potentielles.
## **Comment fonctionne le dépôt**

