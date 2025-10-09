"""
Configuration centrale de l'application
"""

import os
import logging
from typing import Dict, Any

class Config:
    """Configuration de l'application"""
    
    # Répertoires
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    BACKUP_DIR = os.path.join(BASE_DIR, "backups")
    REPORT_DIR = os.path.join(BASE_DIR, "reports")
    LOG_DIR = os.path.join(BASE_DIR, "logs")
    
    # Fichiers
    DEVICES_FILE = os.path.join(BASE_DIR, "devices.yaml")
    
    # Paramètres par défaut
    DEFAULT_TIMEOUT = 30
    MAX_THREADS = 50
    PING_COUNT = 2
    PING_TIMEOUT = 5
    MONITORING_INTERVAL = 60
    
    # NAPALM settings
    NAPALM_OPTIONAL_ARGS = {
        'secret': '',
        'timeout': DEFAULT_TIMEOUT
    }
    
    @classmethod
    def setup_directories(cls):
        """Créer les répertoires nécessaires"""
        directories = [cls.BACKUP_DIR, cls.REPORT_DIR, cls.LOG_DIR]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            logging.debug(f"Directory ensured: {directory}")

# Initialisation
Config.setup_directories()