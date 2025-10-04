import subprocess
import pandas as pd
from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt
import yaml

REPORTS = Path("reports")
REPORTS.mkdir(exist_ok=True)

def check_ping(ip):
    try:
        res = subprocess.run(["ping", "-c", "1", "-W", "1", ip],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
        return res.returncode == 0
    except Exception:
        return False

with open("devices.yaml") as f:
    inventory = yaml.safe_load(f)

data = []
for dev in inventory["devices"]:
    ip = dev["ip"]
    status = check_ping(ip)
    data.append({"ip": ip, "status": "UP" if status else "DOWN", "time": datetime.now()})

df = pd.DataFrame(data)

# Générer un rapport CSV
csv_file = REPORTS / "availability.csv"
df.to_csv(csv_file, index=False)
print(f"💾 Rapport CSV : {csv_file}")

# Générer graphique
plt.figure(figsize=(6, 4))
df["status"].value_counts().plot(kind="bar", color=["green", "red"])
plt.title("Disponibilité réseau")
plt.xlabel("Status")
plt.ylabel("Nombre d'équipements")
plt.savefig(REPORTS / "availability.png")
print(f"📊 Graphique généré : {REPORTS}/availability.png")
