Write-Host " Installation des dépendances pour le projet d'automatisation réseau"

if (-Not (Test-Path ".venv")) {
    Write-Host " Création de l'environnement virtuel (.venv)..."
    python -m venv .venv
} else {
    Write-Host "Environnement virtuel déjà présent."
}

Write-Host "⬆ Mise à jour de pip..."
.venv\Scripts\python.exe -m pip install --upgrade pip

Write-Host " Installation des packages depuis requirements.txt..."
.venv\Scripts\python.exe -m pip install -r requirements.txt

Write-Host "--------------------------------------------------"
Write-Host " Installation terminée avec succès !"
Write-Host " Active l'environnement avec : .venv\Scripts\Activate.ps1"
