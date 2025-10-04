import yaml
import os
from datetime import datetime
from napalm import get_network_driver
from concurrent.futures import ThreadPoolExecutor

# Vérification et chargement de l'inventaire
inventory_file = "devices.yaml"
if not os.path.exists(inventory_file):
    raise FileNotFoundError(f"Fichier {inventory_file} manquant !")

with open(inventory_file) as f:
    try:
        inventory = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ValueError(f"Erreur dans {inventory_file} : {e}")

# Créer dossier backup
os.makedirs("backups", exist_ok=True)

def backup_device(dev):
    print(f"🔎 Connexion à {dev['ip']} ...")
    driver = get_network_driver(dev["driver"])
    device = driver(
        hostname=dev["ip"],
        username=dev["username"],
        password=dev["password"]
    )
    try:
        device.open()
        facts = device.get_facts()
        print(f"✅ {facts['hostname']} ({facts['vendor']}) - uptime {facts['uptime']}s, modèle {facts.get('model', 'N/A')}")
        
        config = device.get_config()
        filename = f"backups/{dev['ip']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.cfg"
        with open(filename, "w") as f:
            f.write(config["running"])
        print(f"💾 Config sauvegardée dans {filename}")
    
    except Exception as e:
        print(f"⚠️ Erreur sur {dev['ip']}: {e}")
    finally:
        device.close()

# Exécution en parallèle
with ThreadPoolExecutor() as executor:
    executor.map(backup_device, inventory["devices"])

print("✅ Sauvegarde terminée pour tous les appareils.")