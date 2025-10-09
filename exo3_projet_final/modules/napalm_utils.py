"""
Module d'automatisation avec NAPALM
"""

from napalm import get_network_driver
import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class NetworkAutomation:
    """Classe pour l'automatisation réseau avec NAPALM"""
    
    def __init__(self, backup_dir: str = "backups", auto_commit: bool = False):
        self.driver_map = {
            'cisco_ios': 'ios',
            'ios': 'ios',
            'junos': 'junos',
            'nxos': 'nxos',
            'eos': 'eos'
        }
        self.backup_dir = backup_dir
        self.auto_commit = auto_commit
        self._connections = {}  # Cache des connexions
        
        # Créer le répertoire de backup
        os.makedirs(self.backup_dir, exist_ok=True)
        logger.info(f"NetworkAutomation initialisé avec backup_dir={backup_dir}, auto_commit={auto_commit}")
    
    def connect_to_device(self, device_config: Dict[str, Any]) -> Optional[Any]:
        """Établir la connexion à l'équipement avec cache"""
        device_key = f"{device_config['hostname']}_{device_config['device_type']}"
        
        # Vérifier le cache
        if device_key in self._connections:
            logger.debug(f"Utilisation connexion cache pour {device_config['hostname']}")
            return self._connections[device_key]
        
        try:
            driver_name = self.driver_map.get(device_config['device_type'], 'ios')
            driver = get_network_driver(driver_name)
            
            # Préparer les arguments optionnels
            optional_args = {}
            if 'secret' in device_config and device_config['secret']:
                optional_args['secret'] = device_config['secret']
            if 'timeout' in device_config:
                optional_args['timeout'] = device_config['timeout']
            
            device = driver(
                hostname=device_config['hostname'],
                username=device_config['username'],
                password=device_config['password'],
                optional_args=optional_args
            )
            
            device.open()
            logger.info(f"Connexion établie avec {device_config['hostname']}")
            
            # Mettre en cache
            self._connections[device_key] = device
            return device
            
        except Exception as e:
            logger.error(f"Echec connexion à {device_config['hostname']}: {e}")
            return None
    
    def _get_device_config(self, device) -> Dict[str, Any]:
        """Méthode centralisée pour récupérer la configuration"""
        try:
            config = device.get_config()
            return {
                'running': config.get('running', ''),
                'startup': config.get('startup', ''),
                'candidate': config.get('candidate', '')
            }
        except Exception as e:
            logger.error(f"Erreur récupération configuration: {e}")
            return {'running': '', 'startup': '', 'candidate': ''}
    
    def collect_device_info(self, device_config: Dict[str, Any]) -> Dict[str, Any]:
        """Collecter les informations complètes"""
        device = self.connect_to_device(device_config)
        if not device:
            return {}
        
        try:
            # Collecte séquentielle avec gestion d'erreur
            info = {'timestamp': datetime.now().isoformat()}
            
            try:
                info['facts'] = device.get_facts()
                logger.debug(f"Facts collectés pour {device_config['hostname']}")
            except Exception as e:
                logger.warning(f"Impossible de récupérer facts pour {device_config['hostname']}: {e}")
                info['facts'] = {}
            
            try:
                info['interfaces'] = device.get_interfaces()
                logger.debug(f"Interfaces collectées pour {device_config['hostname']}")
            except Exception as e:
                logger.warning(f"Impossible de récupérer interfaces pour {device_config['hostname']}: {e}")
                info['interfaces'] = {}
            
            try:
                info['environment'] = device.get_environment()
            except Exception as e:
                logger.warning(f"Impossible de récupérer environment pour {device_config['hostname']}: {e}")
                info['environment'] = {}
            
            # Récupération config via méthode centralisée
            info.update(self._get_device_config(device))
            
            logger.info(f"Données collectées pour {device_config['hostname']}: {list(info.keys())}")
            return info
            
        except Exception as e:
            logger.error(f"Erreur générale collecte pour {device_config['hostname']}: {e}")
            return {}
        finally:
            if device:
                device.close()
                # Retirer du cache après utilisation
                device_key = f"{device_config['hostname']}_{device_config['device_type']}"
                self._connections.pop(device_key, None)
    
    def backup_config(self, device_config: Dict[str, Any]) -> Optional[str]:
        """Sauvegarder la configuration"""
        device = self.connect_to_device(device_config)
        if not device:
            return None
        
        try:
            configs = self._get_device_config(device)
            hostname = device_config['hostname']
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Sauvegarder running config
            filename = f"{self.backup_dir}/backup_{hostname}_{timestamp}.cfg"
            with open(filename, 'w') as f:
                f.write(configs['running'])
            
            logger.info(f"Configuration sauvegardée: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde pour {device_config['hostname']}: {e}")
            return None
        finally:
            if device:
                device.close()
                device_key = f"{device_config['hostname']}_{device_config['device_type']}"
                self._connections.pop(device_key, None)
    
    def deploy_config(self, device_config: Dict[str, Any], config_commands: List[str], 
                     auto_commit: bool = None, dry_run: bool = False) -> Dict[str, Any]:
        """Déployer une configuration"""
        if auto_commit is None:
            auto_commit = self.auto_commit
            
        device = self.connect_to_device(device_config)
        if not device:
            return {'success': False, 'error': 'Connexion échouée'}
        
        try:
            # Charger la configuration candidate
            device.load_merge_candidate(config='\n'.join(config_commands))
            diff = device.compare_config()
            
            result = {
                'success': True,
                'diff': diff,
                'has_changes': bool(diff.strip()),
                'applied': False
            }
            
            logger.info(f"Différences détectées: {len(diff.splitlines())} lignes")
            
            if dry_run:
                logger.info("Mode dry-run - aucune modification appliquée")
                device.discard_config()
                return {**result, 'dry_run': True}
            
            if diff.strip():  # Il y a des changements
                if auto_commit:
                    device.commit_config()
                    result['applied'] = True
                    logger.info("Configuration appliquée automatiquement")
                else:
                    # Log les changements au lieu de demander interactivement
                    logger.warning("Changements détectés mais auto_commit=False")
                    logger.info(f"Différences:\n{diff}")
                    device.discard_config()
                    result['applied'] = False
            else:
                logger.info("Aucun changement détecté")
                device.discard_config()
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur déploiement pour {device_config['hostname']}: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            if device:
                device.close()
                device_key = f"{device_config['hostname']}_{device_config['device_type']}"
                self._connections.pop(device_key, None)
    
    def close_all_connections(self):
        """Fermer toutes les connexions du cache"""
        for device_key, device in self._connections.items():
            try:
                device.close()
                logger.debug(f"Connexion fermée: {device_key}")
            except Exception as e:
                logger.warning(f"Erreur fermeture connexion {device_key}: {e}")
        
        self._connections.clear()