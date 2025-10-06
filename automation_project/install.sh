#!/bin/bash

echo " Installation des dépendances pour le projet d'automatisation réseau"
echo "--------------------------------------------------"

# Vérifie si Python est installé
if ! command -v python3 &> /dev/null
then
    echo " Python3 n'est pas installé. Installe-le avant de continuer."
    exit 1
fi

# Crée un environnement virtuel s’il n’existe pas
if [ ! -d ".venv" ]; then
    echo " Création de l'environnement virtuel (.venv)..."
    python3 -m venv .venv
else
    echo " Environnement virtuel déjà présent."
fi

# Active le venv
source .venv/bin/activate

# Met à jour pip
echo "⬆ Mise à jour de pip..."
pip install --upgrade pip

# Installe les dépendances
echo " Installation des packages depuis requirements.txt..."
pip install -r requirements.txt

echo "--------------------------------------------------"
echo " Installation terminée avec succès !"
echo " Active l'environnement avec : source .venv/bin/activate"
