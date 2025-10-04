import yaml
import os
from datetime import datetime
from napalm import get_network_driver
import argparse

# Analyse des arguments
parser = argparse.ArgumentParser(description="Moniteur réseau avec NAPALM")
parser.add_argument("--inventory", default="devices.yaml", help="Chemin vers devices.yaml")
args = parser.parse_args()
inventory_file = args.inventory

# Vérification et chargement de l'inventaire
if not os.path.exists(inventory_file):
    print("Fichier devices.yaml manquant ! Créez-le avec cette structure :")
    print("""
    devices:
      - ip: "192.168.1.1"
        username: "admin"
        password: "cisco123"
        driver: "ios"
    """)
    raise FileNotFoundError("Fichier devices.yaml manquant !")

with open(inventory_file) as f:
    try:
        inventory = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ValueError(f"Erreur dans {inventory_file} : {e}")

# Créer dossier backup
os.makedirs("backups", exist_ok=True)

for dev in inventory["devices"]:
    print(f"🔎 Connexion à {dev['ip']} ...")
    try:
        driver = get_network_driver(dev["driver"])
        device = driver(
            hostname=dev["ip"],
            username=dev["username"],
            password=dev["password"]
        )
        device.open()

        facts = device.get_facts()
        print(f"✅ {facts['hostname']} ({facts['vendor']}) - uptime {facts['uptime']}s")

        config = device.get_config()
        filename = f"backups/{dev['ip']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.cfg"
        with open(filename, "w") as f:
            f.write(config["running"])
        print(f"💾 Config sauvegardée dans {filename}")

        device.close()

    except Exception as e:
        print(f"⚠️ Erreur sur {dev['ip']}: {e}")