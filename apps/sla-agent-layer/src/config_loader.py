"""
Config Loader - SLA-Agent Layer
Carrega configurações de SLOs de arquivos YAML
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path

BASE_DIR = Path(__file__).parent
CONFIG_DIR = BASE_DIR / "config"


def load_slo_config(domain: str) -> Dict[str, Any]:
    """
    Carrega configuração de SLOs para um domínio
    
    Args:
        domain: Domínio ("RAN", "Transport", "Core")
    
    Returns:
        Dicionário com configuração de SLOs
    """
    domain_lower = domain.lower()
    config_file = CONFIG_DIR / f"slo_{domain_lower}.yaml"
    
    if not config_file.exists():
        raise FileNotFoundError(
            f"❌ Arquivo de configuração SLO não encontrado: {config_file}"
        )
    
    with open(config_file, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    return config


def get_slo_config_path(domain: str) -> str:
    """Retorna caminho do arquivo de configuração SLO"""
    domain_lower = domain.lower()
    return str(CONFIG_DIR / f"slo_{domain_lower}.yaml")

