"""
Module de monitoring réseau
"""

import subprocess
import platform
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
import pandas as pd

logger = logging.getLogger(__name__)


class NetworkMonitoring:
    """Classe pour le monitoring des équipements réseau"""
    
    def __init__(self, ping_count: int = 2, ping_timeout: int = 5):
        self.monitoring_data = []
        self.ping_count = ping_count
        self.ping_timeout = ping_timeout
        logger.info(f"Monitoring initialisé: count={ping_count}, timeout={ping_timeout}s")
    
    def ping_host(self, host: str) -> Dict[str, Any]:
        """Vérifier le statut d'un équipement avec mesures de performance"""
        start_time = datetime.now()
        
        try:
            param = "-n" if platform.system().lower() == "windows" else "-c"
            command = ["ping", param, str(self.ping_count), "-W", "2000", host]
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=self.ping_timeout
            )
            
            response_time = (datetime.now() - start_time).total_seconds()
            is_alive = result.returncode == 0
            
            status_info = {
                'timestamp': start_time,
                'host': host,
                'status': 'UP' if is_alive else 'DOWN',
                'response_time': response_time if is_alive else None,
                'error': None
            }
            
            logger.debug(f"Ping {host}: {status_info['status']} ({response_time:.2f}s)")
            return status_info
            
        except subprocess.TimeoutExpired:
            status_info = {
                'timestamp': start_time,
                'host': host,
                'status': 'TIMEOUT',
                'response_time': None,
                'error': 'Timeout'
            }
            logger.warning(f"Ping timeout pour {host}")
            return status_info
            
        except Exception as e:
            status_info = {
                'timestamp': start_time,
                'host': host,
                'status': 'ERROR',
                'response_time': None,
                'error': str(e)
            }
            logger.error(f"Erreur ping pour {host}: {e}")
            return status_info
    
    def continuous_monitoring(self, devices: Dict[str, Any], interval: int = 60, 
                            duration: int = None) -> None:
        """Monitoring continu avec gestion d'arrêt gracieux"""
        logger.info(f"Démarrage monitoring: {len(devices)} équipements, interval={interval}s")
        
        start_time = datetime.now()
        iteration = 0
        
        try:
            while True:
                iteration += 1
                current_time = datetime.now()
                
                # Vérifier la durée maximale
                if duration and (current_time - start_time).total_seconds() > duration:
                    logger.info("Durée de monitoring atteinte - arrêt")
                    break
                
                logger.info(f"Cycle de monitoring #{iteration}")
                
                for device_name, device_config in devices.items():
                    try:
                        host = device_config['hostname']
                        status_info = self.ping_host(host)
                        
                        # Ajouter des métadonnées
                        status_info['device_name'] = device_name
                        status_info['iteration'] = iteration
                        
                        self.monitoring_data.append(status_info)
                        
                        # Log avec statut
                        status_text = "UP" if status_info['status'] == 'UP' else "DOWN"
                        logger.info(f"{device_name} ({host}): {status_text}")
                        
                    except Exception as e:
                        logger.error(f"Erreur monitoring {device_name}: {e}")
                        # Ajouter une entrée d'erreur
                        self.monitoring_data.append({
                            'timestamp': current_time,
                            'device_name': device_name,
                            'host': device_config.get('hostname', 'N/A'),
                            'status': 'ERROR',
                            'response_time': None,
                            'error': str(e),
                            'iteration': iteration
                        })
                
                logger.info(f"Cycle #{iteration} terminé - attente {interval}s")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("Monitoring arrêté par l'utilisateur")
        except Exception as e:
            logger.error(f"Erreur générale monitoring: {e}")
    
    def calculate_uptime_stats(self, device_name: str = None, hours: int = 24) -> Dict[str, Any]:
        """Calculer les statistiques de disponibilité avec analyse temporelle"""
        if not self.monitoring_data:
            logger.warning("Aucune donnée de monitoring disponible")
            return {}
        
        df = pd.DataFrame(self.monitoring_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Filtrer par période
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_data = df[df['timestamp'] > cutoff_time]
        
        if device_name:
            recent_data = recent_data[recent_data['device_name'] == device_name]
        
        if recent_data.empty:
            return {'error': 'Aucune donnée récente'}
        
        # Calculs statistiques
        stats = {
            'total_checks': len(recent_data),
            'up_checks': len(recent_data[recent_data['status'] == 'UP']),
            'availability_percent': 0,
            'avg_response_time': 0,
            'last_status': recent_data.iloc[-1]['status'] if not recent_data.empty else 'UNKNOWN',
            'analysis_period_hours': hours
        }
        
        if stats['total_checks'] > 0:
            stats['availability_percent'] = (stats['up_checks'] / stats['total_checks']) * 100
        
        # Temps de réponse moyen (uniquement pour les succès)
        successful_pings = recent_data[recent_data['status'] == 'UP']
        if not successful_pings.empty:
            stats['avg_response_time'] = successful_pings['response_time'].mean()
        
        logger.info(f"Stats {device_name or 'global'}: {stats['availability_percent']:.1f}% disponibilité")
        return stats
    
    def export_monitoring_data(self, filename: str = None) -> str:
        """Exporter les données de monitoring en CSV"""
        if not self.monitoring_data:
            logger.warning("Aucune donnée à exporter")
            return ""
        
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"monitoring_export_{timestamp}.csv"
        
        df = pd.DataFrame(self.monitoring_data)
        df.to_csv(filename, index=False)
        
        logger.info(f"Données exportées: {filename} ({len(df)} enregistrements)")
        return filename 