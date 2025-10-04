import yaml
import os
from datetime import datetime
from netmiko import ConnectHandler
import subprocess

# Fallback system ping
def is_pingable(ip):
    try:
        result = subprocess.run(["ping", "-c", "1", "-W", "1", ip],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        return result.returncode == 0
    except Exception:
        return False

# Charger inventaire YAML
with open("devices.yaml") as f:
    inventory = yaml.safe_load(f)

# Créer dossier backup
os.makedirs("backups", exist_ok=True)

for dev in inventory["devices"]:
    ip = dev["ip"]
    print(f"🔎 Test ping {ip} ...", end=" ")
    if not is_pingable(ip):
        print("❌ Hors ligne")
        continue
    print("✅ en ligne")

    try:
        conn = ConnectHandler(
            device_type=dev["device_type"],
            host=ip,
            username=dev["username"],
            password=dev["password"]
        )
        print(f"SSH connecté à {ip}")

        output = conn.send_command(dev["command"])
        conn.disconnect()

        # Sauvegarde dans fichier
        filename = f"backups/{ip}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, "w") as out:
            out.write(output)

        print(f"✅ Config sauvegardée dans {filename}")

    except Exception as e:
        print(f"⚠️ Erreur SSH vers {ip}: {e}")
