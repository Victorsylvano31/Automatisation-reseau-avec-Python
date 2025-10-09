#!/usr/bin/env python3
"""
Application principale d'automatisation réseau
Tafita Raijjoana - TCO M1 2025
"""

import argparse
import logging
import sys
from datetime import datetime

# Configuration du path pour les imports
sys.path.append('.')

from config import Config
from modules.discovery import NetworkDiscovery
from modules.napalm_utils import NetworkAutomation
from modules.monitoring import NetworkMonitoring
from modules.reports import ReportGenerator
from modules.utils import load_devices, setup_logging, create_dry_run_devices


def main():
    """Point d'entrée principal de l'application"""
    
    # Configuration des arguments
    parser = create_parser()
    args = parser.parse_args()
    
    # Configuration du logging
    setup_logging(
        level=args.log_level,
        log_file=args.log_file,
        console=not args.no_console
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Démarrage de Network Automation App")
    logger.info(f"Arguments: {vars(args)}")
    
    # Chargement des équipements
    if args.dry_run:
        logger.info("MODE DRY-RUN - Simulation sans équipements réels")
        devices = create_dry_run_devices()
    else:
        devices = load_devices()
    
    if not devices:
        logger.error("Aucun équipement configuré - Vérifiez devices.yaml")
        return 1
    
    logger.info(f"{len(devices)} équipement(s) chargé(s)")
    
    # Exécution des commandes
    try:
        return execute_commands(args, devices, logger)
    except KeyboardInterrupt:
        logger.info("Application interrompue par l'utilisateur")
        return 0
    except Exception as e:
        logger.error(f"Erreur critique: {e}", exc_info=True)
        return 1


def create_parser():
    """Créer le parser d'arguments"""
    parser = argparse.ArgumentParser(
        description="Application d'automatisation réseau complète",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python main.py --discover --scan-subnet "192.168.1.0/24"
  python main.py --collect --backup --auto-commit
  python main.py --monitor --duration 300 --interval 30
  python main.py --report --export-format excel
  python main.py --deploy-config new_config.txt --dry-run
        """
    )
    
    # Groupes de commandes
    discovery_group = parser.add_argument_group('Découverte')
    collection_group = parser.add_argument_group('Collecte')
    monitoring_group = parser.add_argument_group('Monitoring')
    config_group = parser.add_argument_group('Configuration')
    report_group = parser.add_argument_group('Rapports')
    system_group = parser.add_argument_group('Système')
    
    # Découverte
    discovery_group.add_argument('--discover', action='store_true', 
                                help='Découverte réseau')
    discovery_group.add_argument('--scan-subnet', type=str, 
                                help='Sous-réseau à scanner (ex: 192.168.1.0/24)')
    discovery_group.add_argument('--scan-ports', type=str, default="22,80,443,161",
                                help='Ports à scanner (ex: "22,80,443" ou "1-100")')
    discovery_group.add_argument('--ping-sweep', action='store_true',
                                help='Découverte par ping sweep')
    
    # Collecte
    collection_group.add_argument('--collect', action='store_true',
                                 help='Collecte des données des équipements')
    collection_group.add_argument('--backup', action='store_true',
                                 help='Sauvegarde des configurations')
    collection_group.add_argument('--backup-dir', type=str, default=Config.BACKUP_DIR,
                                 help='Répertoire de sauvegarde')
    
    # Monitoring
    monitoring_group.add_argument('--monitor', action='store_true',
                                 help='Monitoring des équipements')
    monitoring_group.add_argument('--duration', type=int, default=3600,
                                 help='Durée du monitoring (secondes)')
    monitoring_group.add_argument('--interval', type=int, default=60,
                                 help='Intervalle entre les checks (secondes)')
    
    # Configuration
    config_group.add_argument('--deploy-config', type=str,
                             help='Fichier de configuration à déployer')
    config_group.add_argument('--auto-commit', action='store_true',
                             help='Appliquer les configs sans confirmation')
    config_group.add_argument('--validate-only', action='store_true',
                             help='Valider la config sans appliquer')
    
    # Rapports
    report_group.add_argument('--report', action='store_true',
                             help='Génération de rapports')
    report_group.add_argument('--export-format', choices=['json', 'csv', 'excel', 'all'],
                             default='all', help='Format d export des rapports')
    
    # Système
    system_group.add_argument('--dry-run', action='store_true',
                             help='Mode simulation sans modifications')
    system_group.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                             default='INFO', help='Niveau de logging')
    system_group.add_argument('--log-file', type=str,
                             help='Fichier de log (défaut: logs/automation.log)')
    system_group.add_argument('--no-console', action='store_true',
                             help='Désactiver la sortie console')
    
    return parser


def execute_commands(args, devices, logger):
    """Exécuter les commandes en fonction des arguments"""
    
    # Initialisation des modules
    discovery = NetworkDiscovery(timeout=Config.DEFAULT_TIMEOUT, max_threads=Config.MAX_THREADS)
    automation = NetworkAutomation(
        backup_dir=args.backup_dir,
        auto_commit=args.auto_commit
    )
    monitoring = NetworkMonitoring(
        ping_count=Config.PING_COUNT,
        ping_timeout=Config.PING_TIMEOUT
    )
    reporter = ReportGenerator(report_dir=Config.REPORT_DIR)
    
    results = {}
    
    # Découverte réseau
    if args.discover:
        results['discovery'] = run_discovery(args, discovery, logger)
    
    # Collecte des données
    if args.collect:
        results['collection'] = run_collection(args, devices, automation, logger)
    
    # Sauvegarde
    if args.backup:
        results['backup'] = run_backup(args, devices, automation, logger)
    
    # Monitoring
    if args.monitor:
        results['monitoring'] = run_monitoring(args, devices, monitoring, logger)
    
    # Déploiement de configuration
    if args.deploy_config:
        results['deployment'] = run_deployment(args, devices, automation, logger)
    
    # Génération de rapports
    if args.report:
        results['reporting'] = run_reporting(args, devices, reporter, monitoring, logger)
    
    # Résumé final
    logger.info("Toutes les opérations sont terminées")
    logger.info(f"Résumé: {len(results)} commande(s) exécutée(s)")
    
    return 0


def run_discovery(args, discovery, logger):
    """Exécuter la découverte réseau"""
    if not args.scan_subnet and not args.ping_sweep:
        logger.error("Spécifiez --scan-subnet ou --ping-sweep")
        return None
    
    results = {}
    
    if args.scan_subnet:
        logger.info(f"Scan du sous-réseau: {args.scan_subnet}")
        ports = [int(p.strip()) for p in args.scan_ports.split(',')] if args.scan_ports else None
        scan_results = discovery.scan_subnet(args.scan_subnet, ports)
        results['scan'] = scan_results
        logger.info(f"{len(scan_results)} équipement(s) découvert(s) par scan")
    
    if args.ping_sweep and args.scan_subnet:
        logger.info(f"Ping sweep du sous-réseau: {args.scan_subnet}")
        ping_results = discovery.ping_sweep(args.scan_subnet)
        results['ping'] = ping_results
        logger.info(f"{len(ping_results)} hôte(s) actif(s) par ping")
    
    return results


def run_collection(args, devices, automation, logger):
    """Exécuter la collecte des données"""
    logger.info("Début de la collecte des données...")
    
    collected_data = {}
    for device_name, device_config in devices.items():
        if args.dry_run:
            logger.info(f"[DRY-RUN] Collecte simulée pour {device_name}")
            collected_data[device_name] = {'simulated': True}
            continue
        
        logger.info(f"Collecte pour {device_name}...")
        device_info = automation.collect_device_info(device_config)
        
        if device_info:
            collected_data[device_name] = device_info
            logger.info(f"Données collectées: {list(device_info.keys())}")
        else:
            logger.error(f"Echec collecte pour {device_name}")
    
    return collected_data


def run_backup(args, devices, automation, logger):
    """Exécuter la sauvegarde des configurations"""
    logger.info("Début de la sauvegarde...")
    
    backup_files = {}
    for device_name, device_config in devices.items():
        if args.dry_run:
            logger.info(f"[DRY-RUN] Sauvegarde simulée pour {device_name}")
            backup_files[device_name] = f"backup_{device_name}_simulated.cfg"
            continue
        
        backup_file = automation.backup_config(device_config)
        if backup_file:
            backup_files[device_name] = backup_file
            logger.info(f"Configuration sauvegardée: {backup_file}")
        else:
            logger.error(f"Echec sauvegarde pour {device_name}")
    
    return backup_files


def run_monitoring(args, devices, monitoring, logger):
    """Exécuter le monitoring"""
    logger.info("Démarrage du monitoring...")
    
    if args.dry_run:
        logger.info("[DRY-RUN] Monitoring simulé")
        return run_dry_run_monitoring(devices, args.duration, logger)
    
    try:
        monitoring.continuous_monitoring(
            devices, 
            interval=args.interval, 
            duration=args.duration
        )
        return {
            'monitoring_data': monitoring.monitoring_data,
            'stats': monitoring.get_uptime_stats()
        }
    except Exception as e:
        logger.error(f"Erreur monitoring: {e}")
        return None


def run_dry_run_monitoring(devices, duration, logger):
    """Simuler le monitoring en mode dry-run"""
    import time
    
    cycles = min(duration // 10, 5)  # Max 5 cycles en simulation
    logger.info(f"Simulation de {cycles} cycles de monitoring")
    
    for i in range(cycles):
        for device_name in devices.keys():
            logger.info(f"{device_name}: UP (simulation)")
        if i < cycles - 1:
            time.sleep(2)
    
    return {'simulated': True, 'cycles': cycles}


def run_deployment(args, devices, automation, logger):
    """Exécuter le déploiement de configuration"""
    logger.info(f"Déploiement de configuration: {args.deploy_config}")
    
    try:
        with open(args.deploy_config, 'r') as f:
            config_commands = [line.strip() for line in f if line.strip()]
        
        deployment_results = {}
        for device_name, device_config in devices.items():
            logger.info(f"Déploiement sur {device_name}...")
            
            result = automation.deploy_config(
                device_config, 
                config_commands,
                auto_commit=args.auto_commit,
                dry_run=args.dry_run or args.validate_only
            )
            
            deployment_results[device_name] = result
            
            if result['success']:
                if result.get('dry_run'):
                    logger.info("[DRY-RUN] Configuration validée")
                elif result['applied']:
                    logger.info("Configuration appliquée")
                else:
                    logger.info("Aucun changement nécessaire")
            else:
                logger.error(f"Echec déploiement: {result.get('error')}")
        
        return deployment_results
        
    except FileNotFoundError:
        logger.error(f"Fichier non trouvé: {args.deploy_config}")
        return None
    except Exception as e:
        logger.error(f"Erreur déploiement: {e}")
        return None


def run_reporting(args, devices, reporter, monitoring, logger):
    """Exécuter la génération de rapports"""
    logger.info("Génération des rapports...")
    
    monitoring_data = monitoring.monitoring_data if hasattr(monitoring, 'monitoring_data') else None
    
    try:
        report_files = reporter.generate_comprehensive_report(
            devices, 
            monitoring_data,
            export_format=args.export_format
        )
        
        for report_type, file_path in report_files.items():
            if file_path:
                logger.info(f"Rapport {report_type}: {file_path}")
        
        return report_files
        
    except Exception as e:
        logger.error(f"Erreur génération rapports: {e}")
        return None


if __name__ == "__main__":
    sys.exit(main())