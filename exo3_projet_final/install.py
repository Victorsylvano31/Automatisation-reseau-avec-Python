#!/usr/bin/env python3
"""
Script d'installation corrigé pour Network Automation App
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Executer une commande avec gestion d'erreur"""
    print(f"Execution: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"Succes: {description}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de {description}: {e}")
        if e.stderr:
            print(f"Sortie d'erreur: {e.stderr}")
        return False

def install_requirements():
    """Installer les requirements avec gestion d'erreur"""
    if os.path.exists("requirements.txt"):
        # Lire et valider le fichier requirements
        with open("requirements.txt", "r") as f:
            lines = f.readlines()
        
        # Filtrer les lignes valides (qui ne commencent pas par # et ne sont pas vides)
        valid_requirements = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("```"):
                valid_requirements.append(line)
        
        if valid_requirements:
            print("Installation des dependances...")
            for req in valid_requirements:
                if not run_command(f"pip install {req}", f"Installation de {req}"):
                    return False
            return True
        else:
            print("Aucune dependance valide trouvee dans requirements.txt")
            return False
    else:
        print("Fichier requirements.txt non trouve")
        return False

def main():
    """Fonction principale d'installation"""
    print("Installation de Network Automation App")
    print("=" * 50)
    
    # Verifier Python
    if sys.version_info < (3, 7):
        print("Erreur: Python 3.7 ou superieur requis")
        sys.exit(1)
    
    # Creer les repertoires
    print("Creation des repertoires...")
    for directory in ["backups", "reports", "logs"]:
        os.makedirs(directory, exist_ok=True)
        print(f"Repertoire {directory} cree")
    
    # Installer les dependances
    if not install_requirements():
        print("Tentative d'installation manuelle des dependances principales...")
        core_packages = [
            "napalm", "netmiko", "python-nmap", "paramiko", 
            "requests", "pandas", "matplotlib", "pyyaml"
        ]
        for package in core_packages:
            if not run_command(f"pip install {package}", f"Installation de {package}"):
                print(f"Echec de l'installation de {package}")
    
    # Creer devices.yaml exemple si inexistant
    if not os.path.exists("devices.yaml"):
        print("Creation du fichier devices.yaml exemple...")
        with open("devices.yaml", "w") as f:
            f.write("""devices:
  router_exemple:
    hostname: "192.168.1.1"
    device_type: "cisco_ios"
    username: "admin"
    password: "cisco123"
    secret: "cisco123"

global_settings:
  backup_dir: "backups"
  report_dir: "reports"
  log_dir: "logs"
  default_timeout: 30
""")
    
    # Tester l'installation
    print("\nTest de l'installation...")
    test_commands = [
        ("python -c \"from modules.discovery import NetworkDiscovery; print('Discovery OK')\"", "Test module discovery"),
        ("python -c \"from modules.napalm_utils import NetworkAutomation; print('NAPALM OK')\"", "Test module NAPALM"),
    ]
    
    for command, description in test_commands:
        run_command(command, description)
    
    print("\n" + "=" * 50)
    print("Installation terminee!")
    print("\nProchaines etapes:")
    print("1. Modifiez devices.yaml avec vos parametres reseau")
    print("2. Testez avec: python main.py --dry-run --collect")
    print("3. Utilisez: python main.py --help pour voir toutes les options")

if __name__ == "__main__":
    main()