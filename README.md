#  NRE Platform V2 — Network Automation Platform

Bienvenue dans la version 2.0 de ta plateforme d'automatisation réseau. Ce projet a été transformé d'un ensemble de scripts séquentiels en une application moderne, asynchrone et pilotée par API.

---

## Architecture Globale

La plateforme repose sur une architecture découplée en trois couches :

1.  **Core Engine (Nornir + Scrapli)** : Le moteur qui gère les connexions SSH en parallèle massivement.
2.  **API Backend (FastAPI + Celery + SQLAlchemy)** : La couche intelligente qui gère les requêtes, l'historique en base de données et les tâches en arrière-plan (async).
3.  **Frontend Dashboard (React + Vite)** : Une interface web moderne pour visualiser l'état du réseau et piloter les automates.

---

##  Structure du Projet

```text
nre_platform/
├── api/                # Code de l'API FastAPI
│   ├── routes/         # Endpoints (jobs, devices)
│   └── main.py         # Point d'entrée de l'API
├── core/               # Moteur d'automatisation
│   ├── automation_engine/ # Initialisation de Nornir
│   ├── inventory/      # Fichiers YAML (hosts, groups, defaults)
│   ├── tasks/          # Fonctions d'automatisation (backup, etc.)
│   └── config.py       # Configuration centralisée (Pydantic)
├── db/                 # Modèles de base de données (SQLAlchemy)
├── frontend/           # Application React (Tableau de bord)
├── workers/            # Configuration Celery pour les tâches async
├── cli/                # Interface en ligne de commande (Typer)
├── backups/            # Dossier où sont stockées les configurations réseau
└── docker-compose.yml  # (Optionnel) Pour PostgreSQL/Redis en production
```

---

##  Stack Technique

*   **Backend** : Python 3.10+, FastAPI, Nornir 3.x, Scrapli, SQLAlchemy (SQLite), Celery (Eager mode).
*   **Frontend** : React 18, Vite 5, Axios, Framer Motion (animations), Lucide React (icônes).
*   **CLI** : Typer.

---

##  Comment l'utiliser

### 1. Prérequis
Assure-toi d'avoir installé les dépendances :
```bash
pip install fastapi uvicorn nornir nornir-scrapli nornir-napalm nornir-netbox sqlalchemy celery redis typer pydantic-settings
# Dans le dossier frontend
cd frontend
npm install
```

### 2. Lancer le Backend (L'API)
Depuis la racine `nre_platform` :
```powershell
$env:PYTHONPATH="."
uvicorn api.main:app --reload
```
Accède à la documentation interactive : [http://localhost:8000/docs](http://localhost:8000/docs)

### 3. Lancer le Dashboard (Le Web)
Dans un nouveau terminal, dossier `frontend` :
```bash
npm run dev
```
Ouvre [http://localhost:5173](http://localhost:5173)

### 4. Utiliser la CLI
Pour déclencher un job depuis la console :
```powershell
$env:PYTHONPATH="."
python cli/main.py backup
python cli/main.py status <JOB_ID>
```

---

##  Configuration de l'Inventaire

Pour ajouter tes vrais équipements :
1. Ouvre `core/inventory/hosts.yaml`.
2. Décommente les exemples et remplace `hostname` par l'IP de ton équipement.
3. Vérifie les identifiants dans `core/inventory/defaults.yaml`.

---

##  Roadmap & Améliorations Futures

*   **NetBox Integration** : Remplacer les fichiers YAML par NetBox comme Source of Truth.
*   **Monitoring Temps Réel** : Ajouter des sondes SNMP/Telemetry via Nornir.
*   **Logs Interactifs** : Afficher le flux SSH en direct dans le Dashboard via WebSockets.
*   **Multi-Constructeurs** : Ajouter des profils pour Arista, Palo Alto et F5.

