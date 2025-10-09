"""
Utilitaires communs pour l'application
"""

import yaml
import logging
import sys
from typing import Dict, Any
from config import Config


def setup_logging(level='INFO', log_file=None, console=True):
    """Configurer le logging structuré"""
    
    log_level = getattr(logging, level.upper())
    
    # Formatter commun
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handlers
    handlers = []
    
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        handlers.append(console_handler)
    
    if log_file:
        if log_file is True:  # Fichier par défaut
            log_file = f"{Config.LOG_DIR}/automation.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    
    # Configuration racine
    logging.basicConfig(
        level=log_level,
        handlers=handlers
    )
    
    # Réduire la verbosité des librairies externes
    logging.getLogger('paramiko').setLevel(logging.WARNING)
    logging.getLogger('napalm').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)


def load_devices(config_file=None) -> Dict[str, Any]:
    """Charger la configuration des équipements"""
    
    if config_file is None:
        config_file = Config.DEVICES_FILE
    
    try:
        with open(config_file, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        
        devices = config.get('devices', {})
        
        # Appliquer les paramètres globaux
        global_settings = config.get('global_settings', {})
        for device_name, device_config in devices.items():
            device_config.setdefault('timeout', global_settings.get('default_timeout', Config.DEFAULT_TIMEOUT))
        
        logging.info(f"Configuration chargée: {len(devices)} équipement(s)")
        return devices
        
    except FileNotFoundError:
        logging.error(f"Fichier de configuration non trouvé: {config_file}")
        return {}
    except yaml.YAMLError as e:
        logging.error(f"Erreur YAML dans {config_file}: {e}")
        return {}
    except Exception as e:
        logging.error(f"Erreur chargement configuration: {e}")
        return {}


def create_dry_run_devices() -> Dict[str, Any]:
    """Créer des équipements simulés pour le dry-run"""
    
    return {
        'router_sim_1': {
            'hostname': '192.168.1.1',
            'device_type': 'cisco_ios',
            'username': 'admin',
            'password': 'cisco123',
            'secret': 'cisco123'
        },
        'switch_sim_1': {
            'hostname': '192.168.1.2',
            'device_type': 'cisco_ios', 
            'username': 'admin',
            'password': 'cisco123',
            'secret': 'cisco123'
        },
        'firewall_sim_1': {
            'hostname': '192.168.1.3',
            'device_type': 'asa',
            'username': 'admin',
            'password': 'cisco123'
        }
    }


def validate_device_config(device_config: Dict[str, Any]) -> bool:
    """Valider la configuration d'un équipement"""
    
    required_fields = ['hostname', 'device_type', 'username', 'password']
    
    for field in required_fields:
        if field not in device_config or not device_config[field]:
            logging.error(f"Champ manquant dans configuration: {field}")
            return False
    
    # Validation du type d'équipement
    supported_types = ['cisco_ios', 'ios', 'junos', 'nxos', 'eos', 'asa']
    if device_config['device_type'] not in supported_types:
        logging.warning(f"Type d équipement non supporté: {device_config['device_type']}")
    
    return True