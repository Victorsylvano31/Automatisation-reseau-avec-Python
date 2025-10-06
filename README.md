# Projet d'automatisation réseau avec Python

Ce projet contient deux exercices pratiques pour apprendre à automatiser la gestion et la surveillance des équipements réseau avec Python.

---

## 1. Installation

### Étape 1 : Créer l’environnement virtuel et installer les dépendances

#### Sous Linux / macOS
```bash
./install.sh
````

#### Sous Windows

```powershell
.\install.ps1
```

### Étape 2 : Activer l’environnement

* Linux / macOS :

  ```bash
  source .venv/bin/activate
  ```
* Windows :

  ```powershell
  .venv\Scripts\Activate.ps1
  ```

### Étape 3 : Vérifier les dépendances

```bash
pip list
```

Vous devez voir : netmiko, napalm, pandas, matplotlib, pyyaml, pythonping, etc.

---

## 2. Structure du projet

```
automation_project/
│
├── install.sh / install.ps1     # script d'installation
├── requirements.txt             # dépendances Python
│
├── exo1_SSH/                    # Exercice 1 : SSH et sauvegarde de configuration
│   ├── ssh_backup.py
│   ├── devices.yaml
│   └── backups/
│
└── exo2_NAPALM/                 # Exercice 2 : NAPALM et monitoring
    ├── collect.py
    ├── monitor.py
    ├── devices.yaml
    ├── backups/
    └── reports/
```

---

## 3. Exercice 1 – Automatisation SSH

### Objectif

* Se connecter à plusieurs équipements via SSH
* Exécuter une commande
* Sauvegarder les configurations automatiquement

### Fichier principal

```
exo1_SSH/ssh_backup.py
```

### Exécution

```bash
python exo1_SSH/ssh_backup.py
```

Les configurations sont enregistrées dans le dossier :

```
exo1_SSH/backups/
```

---

## 4. Exercice 2 – Automatisation avancée avec NAPALM

### Objectif

* Se connecter à plusieurs routeurs/switchs avec NAPALM
* Récupérer les informations de base (hostname, uptime, vendor)
* Sauvegarder les configurations
* Vérifier la disponibilité réseau (ping)
* Générer un rapport graphique

### a) Collecte d’informations

```bash
python exo2_NAPALM/collect.py
```

Les fichiers de configuration sont enregistrés dans :

```
exo2_NAPALM/backups/
```

### b) Monitoring réseau

```bash
python exo2_NAPALM/monitor.py
```

Résultats :

* Rapport CSV : `exo2_NAPALM/reports/availability.csv`
* Graphique PNG : `exo2_NAPALM/reports/availability.png`

---

## 5. Fichier devices.yaml

Chaque exercice utilise un fichier `devices.yaml` qui contient la liste des équipements :

```yaml
devices:
  - ip: "192.168.56.101"
    device_type: "cisco_ios"   # pour SSH
    driver: "ios"              # pour NAPALM
    username: "admin"
    password: "cisco"
```

---

## 6. Conseils

* Vérifiez que vos routeurs ou VMs répondent au ping et que le service SSH est activé.
* Si vous utilisez GNS3, assurez-vous que les routeurs sont sur le même réseau que votre machine hôte.
* Si le ping échoue, le script indiquera "hors ligne".
* Pour les tests sans lab, vous pouvez utiliser l’adresse `127.0.0.1` avec un service SSH local.

---

## 7. Résumé

| Exercice | Fonction principale                          | Script                       | Résultat                               |
| -------- | -------------------------------------------- | ---------------------------- | -------------------------------------- |
| 1        | Connexion SSH et sauvegarde de configuration | `ssh_backup.py`              | Fichiers `.txt` dans `/backups`        |
| 2        | Collecte et supervision avec NAPALM          | `collect.py` et `monitor.py` | Configurations `.cfg` + rapport `.png` |

---