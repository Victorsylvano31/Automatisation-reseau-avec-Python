"""
Module de découverte réseau
"""

import socket
import nmap
import ipaddress
import subprocess
import platform
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class NetworkDiscovery:
    """Classe pour la découverte des équipements réseau"""
    
    def __init__(self, timeout: int = 2, max_threads: int = 50):
        self.nm = nmap.PortScanner()
        self.timeout = timeout
        self.max_threads = max_threads
        logger.info(f"NetworkDiscovery initialisé: timeout={timeout}s, threads={max_threads}")
    
    def check_port(self, ip: str, port: int = 22, timeout: int = None) -> bool:
        """Vérifier si un port est ouvert"""
        
        if timeout is None:
            timeout = self.timeout
            
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        try:
            result = sock.connect_ex((ip, port))
            is_open = result == 0
            logger.debug(f"Port check {ip}:{port} -> {'OPEN' if is_open else 'CLOSED'}")
            return is_open
            
        except socket.gaierror as e:
            logger.error(f"Erreur DNS pour {ip}: {e}")
            return False
        except socket.error as e:
            logger.warning(f"Erreur socket pour {ip}:{port}: {e}")
            return False
        finally:
            sock.close()
    
    def check_ports(self, ip: str, ports: List[int] = None) -> Dict[int, bool]:
        """Vérifier plusieurs ports sur une IP"""
        
        if ports is None:
            ports = [22, 23, 80, 443, 161]  # Ports réseau courants
            
        results = {}
        for port in ports:
            results[port] = self.check_port(ip, port)
        
        open_ports = [p for p, is_open in results.items() if is_open]
        logger.info(f"Scan ports {ip}: {len(open_ports)} port(s) ouvert(s) - {open_ports}")
        return results
    
    def ping_host(self, host: str, count: int = 2) -> bool:
        """Ping un hôte de manière portable"""
        
        try:
            # Déterminer le paramètre selon l'OS
            param = "-n" if platform.system().lower() == "windows" else "-c"
            
            # Commande avec timeout
            command = ["ping", param, str(count), "-W", "2000", host]
            
            # Exécution silencieuse
            result = subprocess.run(
                command, 
                capture_output=True, 
                text=True,
                timeout=10
            )
            
            is_alive = result.returncode == 0
            logger.debug(f"Ping {host} -> {'ALIVE' if is_alive else 'DEAD'}")
            return is_alive
            
        except subprocess.TimeoutExpired:
            logger.warning(f"Ping timeout pour {host}")
            return False
        except Exception as e:
            logger.error(f"Erreur ping pour {host}: {e}")
            return False
    
    def scan_subnet(self, subnet: str, ports: List[int] = None) -> List[Dict[str, Any]]:
        """Scanner un sous-réseau avec Nmap"""
        
        logger.info(f"Début scan subnet: {subnet}")
        
        try:
            # Préparer les arguments nmap
            ports_str = ','.join(map(str, ports)) if ports else "22,23,80,443,161"
            arguments = f'-n -sS -T4 --host-timeout 30s -p {ports_str}'
            
            logger.debug(f"Exécution nmap: {arguments}")
            self.nm.scan(hosts=subnet, arguments=arguments)
            
            discovered_devices = []
            for host in self.nm.all_hosts():
                if self.nm[host].state() == 'up':
                    # Récupérer les ports ouverts
                    open_ports = []
                    if 'tcp' in self.nm[host]:
                        open_ports = [
                            port for port, info in self.nm[host]['tcp'].items() 
                            if info['state'] == 'open'
                        ]
                    
                    device_info = {
                        'ip': host,
                        'hostname': self.nm[host].hostname() or 'N/A',
                        'state': self.nm[host].state(),
                        'open_ports': open_ports,
                        'scan_method': 'nmap'
                    }
                    discovered_devices.append(device_info)
            
            logger.info(f"Scan terminé: {len(discovered_devices)} équipement(s) découvert(s)")
            return discovered_devices
            
        except nmap.PortScannerError as e:
            logger.error(f"Erreur nmap lors du scan {subnet}: {e}")
            return []
        except Exception as e:
            logger.error(f"Erreur inattendue lors du scan {subnet}: {e}")
            return []
    
    def ping_sweep(self, subnet: str, check_ports: List[int] = None) -> List[Dict[str, Any]]:
        """Découverte par ping sweep"""
        
        try:
            network = ipaddress.ip_network(subnet, strict=False)
            hosts_list = list(network.hosts())  # Convertir en liste une seule fois
            
            logger.info(f"Ping sweep sur {subnet} ({len(hosts_list)} hôte(s))")
            
            def check_host(ip):
                """Vérifier un hôte individuel"""
                ip_str = str(ip)
                if self.ping_host(ip_str):
                    port_status = self.check_ports(ip_str, check_ports) if check_ports else {}
                    return {
                        'ip': ip_str,
                        'alive': True,
                        'open_ports': [port for port, is_open in port_status.items() if is_open]
                    }
                return {'ip': ip_str, 'alive': False, 'open_ports': []}
            
            # Exécution parallèle
            active_hosts = []
            with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
                results = list(executor.map(check_host, hosts_list))
                active_hosts = [result for result in results if result['alive']]
            
            logger.info(f"Ping sweep terminé: {len(active_hosts)} hôte(s) actif(s)")
            return active_hosts
            
        except ValueError as e:
            logger.error(f"Sous-réseau invalide {subnet}: {e}")
            return []
        except Exception as e:
            logger.error(f"Erreur lors du ping sweep {subnet}: {e}")
            return []
    
    def comprehensive_discovery(self, subnet: str, ports: List[int] = None) -> Dict[str, Any]:
        """Découverte complète combinant plusieurs méthodes"""
        
        logger.info(f"Début découverte complète: {subnet}")
        
        results = {
            'subnet': subnet,
            'timestamp': ipaddress.datetime.now().isoformat(),
            'nmap_scan': [],
            'ping_sweep': [],
            'summary': {}
        }
        
        # Scan Nmap
        nmap_results = self.scan_subnet(subnet, ports)
        results['nmap_scan'] = nmap_results
        
        # Ping sweep
        ping_results = self.ping_sweep(subnet, ports)
        results['ping_sweep'] = ping_results
        
        # Résumé
        results['summary'] = {
            'nmap_devices': len(nmap_results),
            'ping_hosts': len(ping_results),
            'total_unique_ips': len(set(
                [dev['ip'] for dev in nmap_results] + 
                [host['ip'] for host in ping_results]
            ))
        }
        
        logger.info(f"Découverte complète terminée: {results['summary']}")
        return results