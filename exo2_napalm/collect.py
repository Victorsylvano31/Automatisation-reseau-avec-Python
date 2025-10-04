import yaml
import os
from datetime import datetime
from napalm import get_network_driver

# Charger l'inventaire
with open("devices.yaml") as f:
    inventory = yaml.safe_load(f)

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

        # Récupérer infos (facts)
        facts = device.get_facts()
        print(f"✅ {facts['hostname']} ({facts['vendor']}) - uptime {facts['uptime']}s")

        # Sauvegarde config
        config = device.get_config()
        filename = f"backups/{dev['ip']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.cfg"
        with open(filename, "w") as f:
            f.write(config["running"])
        print(f"💾 Config sauvegardée dans {filename}")

        device.close()

    except Exception as e:
        print(f"⚠️ Erreur sur {dev['ip']}: {e}")
