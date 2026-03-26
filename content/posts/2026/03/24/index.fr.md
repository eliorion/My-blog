---
title: 'Containerise Python application'
date: 2025-12-11T09:38:10+01:00
draft: false
topics:
  - Homelab
  - DevOps
tags:
projects:
  - KubeCraft_learning
categories:
  - IT
  - Learning
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
## **Une application Python à containerise complète à la fin**

Dans le contexte du cours KubeCraft, j'avais besoin de créer une application complète containerise Python à partir de zéro. Le cours est centré sur l'implémentation DecSecOps, notez la partie Python.
## **Pré-requis**

La première étape pour avoir un bel environnement DevSecOps est le travail d'équipe. Je serai le seul qui utilise ce projet, mais en réalité une équipe de trou devra avoir accès et modifier une partie de l'application. Pensez d'abord à l'esprit lorsque vous avez un projet informatique et le travail d'équipe, vous pensez à Git. Même si vous n'avez pas une équipe avec laquelle travailler, utilisez Git est une belle façon d'avoir un journal de votre travail et expliquer pourquoi l'application ne fonctionne pas après une modification, et être en mesure de revenir à une version sécurisée.
### **Pourquoi un commit standard est requis**

Git est très utile de toute façon. Cependant, lorsque votre projet a de plus en plus de personnes sur lui, vous pouvez commencer à faire face à un problème avec l'enfer de commit. Cela consiste à avoir une bonne piste de vos commits, mais vous ne pouviez pas comprendre ce qui se passe sur ce commit parce qu'il est nommé comme ceci : - corriger les choses - mettre à jour le code - modifier - corriger les bugs login - version finale Donc, nous connaissons tous ce type de commits nom sur nos dépôts, et je suis le premier qui est coupable. La solution pour avoir une belle et compréhensible histoire de Git est de normaliser tout ce désordre. J'ai découvert « commit conventionnel » comment expliquer comment avoir une bonne base de commits de nommage sur ce que vous faites et quelle est la gamme de votre intervention.
### **Pourquoi est-il compliqué à mettre en œuvre**

C'est une bonne idée, mais si vous dites simplement à votre équipe de développeur et à votre équipe d'opération, certains le prendront avec grimace et l'implémenteront immédiatement, mais pour certains d'entre eux ou le nouveau gars qui vient d'arriver à l'équipe, il peut être complété pour forcer les gens à utiliser ce standard. C'est pourquoi il est nécessaire d'aider votre équipe à utiliser le bon format pour le début au moins. C'est pourquoi l'outil « Commitizen » est le match parfait. Avec une configuration simple et un crochet Git, vous pouvez forcer les gens à utiliser le commit standard directement sur le poste de travail de votre équipe. Et si vous avez encore oublié le standard, vous devez simplement utiliser le guide « Commitizen » pour vous aider à créer le bon nom et la bonne description de commit.
## **Setup the environment**

Le présent règlement entre en vigueur le jour suivant celui de sa publication au Journal officiel de l'Union européenne.
### **Configuration de Devcontainer**

Pour construire l'application, je choisis d'utiliser un devcontainer avec Docker install. Pour un ingénieur DevOps, la meilleure pratique est d'utiliser des devcontainers. Donc, si vous avez un nouveau gars qui est venu sur l'équipe, il peut être en haut et en cours d'exécution sur le code en quelques minutes. Avec cela, j'utilise DevPod pour gérer mon environnement de projet différent parce que c'est très convivial avec ma configuration de fichiers dot. Whit qui a dit, J'utilise "Mise" pour installer mon kit d'outils sur le decontainer. Pour cela, il y a une configuration à faire: ".devcontainer/devcontainer.json": ``bash { "build": { "context": ".., "dockerfile": "Dockerfile" }, "postCreateCommand": "scripts/setup" "features": { "ghcr.io/devtainers/docker-in-docker" }: {}, "command"
# Assurez-vous que mise est activé à la fois dans zsh et bash. Peut être dépassé par les fichiers dot d'un utilisateur.

RUN echo 'eval "$(mise activate bash)"" >> /home/vscode/.bashrc && \ echo 'eval "$(mise activate zsh)" >> /home/vscode/.zshrc `` Ce fichier spécifie l'image de base du devcontainer, et copie le binaire de "mise", avec le commentaire pour l'activer sur le devcontainer. "scripts/setup": ```bash
# !/Bin/Bash

/usr/local/bin/mise trust /workspaces/"$DEVPOD_WORKSPACE_ID"/mise.toml && /usr/local/bin/mise install `` Le script de configuration fait confiance aux espaces de travail et installe toutes les dépendances du projet.
### **Configuration de la mise en mémoire**

"mise.toml": ```bash [tools] pre-commit = "latest" python = "3.13" trivy = "0.69.2" uv = "latest" [settings] python.uv_venv_auto = true idiomatic_version_file_enable_tools = ["python"] experimental = true [env] APP_REPO = 'devops-study-app' GITOPS_REPO = 'devops-study-app-gitops' [hooks] enter = "bash ./scripts/setup_project" ``` Sur ce fichier, tous les outils nécessaires au projet sont configurés. De plus, le crochet exécute le fichier "scripts/setup_project" lorsque le devcontainer est créé.
# !/Bin/Bash

if ! command -v cz >/dev/null && [ "$DEVPOD" = "true" ]; alors git config --global push.autoSetupRemote true git config --global --add safe.directory /workspaces/devops-study-app/ pip install --user pipx install commitizen pre-commit install --hook-type commit-msg fi ``` Ce fichier set "Git" pour pouvoir utiliser "pre-commit" pour gérer le message de commit et vérifier si la norme est respectée.
## ** Structure du projet Python**

La structure du projet est basée sur la structure standard Python. Ainsi, il s'agit de la structure de dossier actuelle du projet: ```bash ─= backend │ │ │ │ │ │ │ │ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ uv.lock ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ ¦ . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
## **Containerisation de la demande**

Le présent règlement entre en vigueur le jour suivant celui de sa publication au Journal officiel de l'Union européenne.
### **Création du fichier Docker**

La première étape consiste à créer le fichier `Dockerfile` pour le frontend et l'application backend. Pour l'apprentissage de la purpuse, je spleet la version finale du fichier en quatre parties: Backend `Dockerfile` V0: ``bash
# Image de base du conteneur

FROM python:latest
# Installer uv sur le conteneur

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
# Le répertoire actuel est '/app'

RÉSULTATS /app
# Copier le répertoire courant dans le répertoire conteneur '/app'

COPY . /app
# Utilisez uv pour compiler le projet

Synchronisation RUN uv --locked --no-editable
# Exécuter le binaire de backend avec uv

CMD ["uv", "run", "study-tracker-api"] ``` Le conteneur est la base sur la dernière image de Python dans le registre de docker. C'est une base d'images lourde sur Debian avec beaucoup d'outils incorporés. Il y a de nombreuses façons d'économiser de l'espace et des performances mais pour l'instant il est bon pour le début.
### **Construisez l'image du conteneur**

Utilisez la commande `docker build` avec un drapeau pour la vérification. ``bash docker build -t backend:00 . ``` Maintenant, avec la commande `docker images or docker image ls` voir l`image dans votre registre Docker local. Si vous voulez aller plus loin dans la façon dont l`image est construite de vous pouvez utiliser `docker history backend:00` pour voir la mise en page de votre image.
### **Démarrer l'image**

Exécuter : ```bash docker run backend:00 `` Vous pouvez ajouter le drapeau `-d` pour exécuter le conteneur en mode détachement.
### **Sécurisation avec "Trivy"**

Être capable de pousser votre image avec un audit de sécurité est une bonne pratique de sécurité pour l'ingénieur DevOps. `Trivy` est l'un des contrôles de sécurité les plus populaires utilisés de nos jours. Pour ce projet, j'utilise simplement pour analyser les images de conteneur. `Trivy` est déjà installé avec `mise`, donc il est simple d'utiliser directement dans le devcontainer: ``bash trivy image --format table --severity CRITICAL,HIGH backend:00 ``` Cette commande vous montre sur une table forma les problèmes de sécurité les plus danjereux dans votre image de conteneur. Donc, avec cette version, trivy a trouvé quelques problèmes. Ce processus est nécessaire avant de lancer une image.
### ** Optimisation de la taille de l'image**

L'utilisation de l'image de base est la valeur par défaut `Python:latest`, mais si vous entrez dans le registre Python Docker Hub, vous trouverez de nombreuses versions de l'image de base Python. Par défaut, après avoir construit notre taille d'image 440MB. Donc, pour une petite application comme celle-ci, c'est surkill. De plus, `Trivy` a trouvé la plupart des problèmes de sécurité sur l'image de base Debian. Donc, si l'image a moins d'outils disponibles, cela signifie aussi moins de surface d'attaques possible pour les pirates.
#### **Python mince**

Utilisez une verion définie de Python avec le subtatle `slim`: `FROM python:3.13-slim`. Vous devez: 1. Reconstruisez votre image avec une nouvelle balise comme: 01 2. Scannez avec `Trivy` 3. Exécutez pour vérifier si elle fonctionne
#### **Python alpin**

Utilisez une verion définie de Python avec le sous-tache `alpine`: `FROM python:3.13-alpine`. L'image alpine est creat très léger et sécurisé. C'est donc les pieds parfaits pour notre application. D'ailleurs l'image alpine est dur à utiliser sur l'environnement de conteneurisation. Vous devez: 1. Reconstruire votre image avec une nouvelle étiquette comme: 02 2. Scanner avec `Trivy` 3. Exécuter pour vérifier si elle fonctionne
### ** Optimisation de la construction**

Pour pouvoir gagner de la taille sur notre image, il est possible de ne pas ajouter les fichiers Python sur l'image, mais seulement le binaire et juste ce que l'application devait absolument fonctionner. La méthode est d'utiliser une image de base pour construire le projet avec cach, de sorte que notre construction prendra moins de temps, et après la construction utiliser une autre image de base avec seulement le binaire de l'application. De cette façon, l'image finale n'a pas à contenir uv du tout. Backend `Dockerfile` V4: ``bash
# Étape de construction

FROM python:3.13-alpine AS builder COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
# Changer le répertoire de travail pour le répertoire `app`

RÉSULTATS /app
# Installez les dépendances dans un calque cache. Cela accélère le temps de construction

RUN --mount=type=cache,target=/root/.cache/uv \ --mount=type=bind,source=uv.lock,target=uv.lock \ --mount=type=bind,source=pyproject.toml,target=pyproject.toml \ uv sync --locked --no-install-project --no-editable
# Copier le projet dans l'image intermédiaire

COPY . /app
# Synchronisez le projet et installez-le, maintenant que nous avons accès au code source

RUN --mount=type=cache,target=/root/.cache/uv \ uv sync --locked --no-editable
# Création d'images

FROM Python:3.13-alpine
# Créer un utilisateur et un groupe non root avec des identifiants spécifiques

RUN addgroup -S -g 1000 app && adduser -S -u 1000 -G app app
# Copier l'environnement, mais pas le code source

COPY --from=builder --chown=app:app /app/.venv /app/.venv
# Basculer vers l'utilisateur non root

APPLICATION DE L' UTILISATEUR
# Exposer le bon port

EXPOSÉ 22112
# Exécuter l'application

