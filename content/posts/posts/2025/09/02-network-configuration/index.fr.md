---
title: 'Configuration du réseau'
date: 2025-08-31T22:19:31+02:00
draft: true
topics: ["Homelab"]
tags: ["talos.linux", "K8S", "K9S", "K3S", "talosctl", "proxmox", "hardware", "homelab", "network"]
projects: ["HomeLab gitDevSecOps"]
categories: ["IT", "Homelab"]
weight: 0 # Lower number = toper in the list
cover:
  image: "cover.png"
  alt: 'Network Configuration'
  caption: ""
  relative: true  
  hidden: true            # si true → pas de cover sur la page du post
  hiddenInList: true      # si true → pas de cover dans la liste des posts
  hiddenInSingle: false    # si true → pas de cover sur la page individuelle
---
Le présent règlement entre en vigueur le jour suivant celui de sa publication au Journal officiel de l'Union européenne.
## Premier numéro

### Environnements multiples

Tout d'abord, je dois me connecter à mon serveur dans SSH et dans http pour gérer Proxmox. ![Homelab Diagram](diagram.png) Avec ce diagramme vous pouvez voir une utilisation simple de la machine VM. Mais, j'ai des conditions personnelles. J'ai besoin d'un réseau virtuel pour avoir une IP stable de mon noeud dans mon cluster. Mais, comme vous pouvez le voir, par défaut avec proxmox, vous avez un pont créé se connecter au port Ethernet physique dans le serveur. Et, je change d'environnement pour travailler dans mon bureau, et ma maison parce que je n'ai pas de boîte Internet là-dedans, donc pour connecter mon serveur à mon PC, je dois connecter les ports Ethernet du serveur et mon PC en direct. Mais, sans serveur DHCP je ne peux pas avoir d'IP dans mon serveur. J'ai perdu 2 heures pour trouver une solution. J'oblige le PC à partager la connexion wifi au port Ethernet. Avec cette solution, le réseau DHCP fonctionne bien avec le réseau `192.168.
### Brick virtuel pour le cluster

Pour éviter un changement de VM pendant le changement d'environnement, la solution est de construire un brick virtuel spécifique au cluster. C'est prety facile à créer. Je crée un brick vmb1, et j'ajoute ce brick à tous mes nœuds cluster et mon nœud manager. J'ajoute juste une nouvelle interface réseau. Et, ça ne fonctionne pas. Je veux créer un réseau virtuel, c'est vide. Quand vous connectez toute votre machine là-dedans, c'est comme avoir 4 machines dans le même réseau, mais personne ne peut interagir parce qu'aucune n'a d'adresse IP. Après avoir compris cela (il m'a pris 2 heures), j'ai eu besoin d'installer le serveur DHCP sur mon serveur Proxmox, et d'administrer le brick vmb1 pour attribuer automatiquement l'adresse IP.
#### Installer le serveur DHCP

Cette partie était prety facile, vous avez juste besoin de choisir un serveur DHCP, et l'installer. Je choisis `dnsmasq`pour ce lighweht.
#### Configurer DHCP

Très facile à utiliser avec un seul fichier de configuration `/etc/dnsmasq.d/<YOUR-INTERFACE-CONFIGURATION>.conf`. Voulez-vous créer ce fichier, vous pouvez configurer le DHCP avec une plage d'adresses IP, et une adresse statique avec adresse MAC spécifique. I mon cas : `/etc/dnsmasq.d/vmbr1.conf` : ``bash interface=<INTERFACE> # Interface dhcp-range=<START_IP_ADRESSE,END_IP_ADRESS,12h. # Attribut automaticaly IPs between START and END dhcp-host=<MAC_ADRESS>,<IP_ADRESS> # Attribut static IP to specific adresse device ```Dans mon cas, j'ai voulu avoir une IP statique pour mes nœuds et mon gestionnaire de cluster.
# Adresse IP des nœuds

dhcp-host=AA:BB:CC:DD:EE:01,10.0.0.10 # Attribut IP statique au noeud de commande dhcp-host=AA:BB:CC:DD:EE:02,10.0.0.11 # Attribut IP statique au travailleur 00 dhcp-host=AA:BB:CC:DD:EE:03,10.0.0.12 # Attribut IP statique au travailleur 01
# Gestionnaire de grappes

dhcp-host=AA:BB:CC:DD:EE:04,10.0.0.100 # Attribuer IP statique au gestionnaire de cluster ``
#### Résultat

