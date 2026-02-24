import os
from nornir import InitNornir
from nornir.core import Nornir
from typing import Optional

def get_nornir_engine(config_file: str = "core/inventory/config.yaml") -> Nornir:
    """Initialize and return a Nornir engine instance."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_config_path = os.path.join(base_dir, "inventory", "config.yaml")
    
    # Try absolute path first, then fallback to relative if provided path exists
    path_to_use = full_config_path if os.path.exists(full_config_path) else config_file
    
    nr = InitNornir(config_file=path_to_use)
    return nr

def filter_inventory(nr: Nornir, filters: Optional[dict] = None) -> Nornir:
    """Filter the Nornir inventory based on metadata."""
    if not filters:
        return nr
    return nr.filter(**filters)
