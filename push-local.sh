#!/bin/bash

# Vérifie si un message de commit a été fourni
if [ -z "$1" ]; then
  echo "Usage: $0 \"commit message\""
  exit 1
fi

# Stocke le message de commit
COMMIT_MESSAGE="$1"

# Ajoute tous les fichiers modifiés
git add .

# Crée le commit avec le message
git commit -m "$COMMIT_MESSAGE"

# Pousse les changements vers le dépôt distant
git push --set-upstream git@github.com:eliorion/My-blog.git dev
