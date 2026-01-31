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
        # Fallback robusto: retornar configuração padrão
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"⚠️ Arquivo de configuração SLO não encontrado: {config_file}. Usando configuração padrão.")
        return {
            "domain": domain,
            "slos": []
        }
    
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        
        if not config:
            # Arquivo vazio ou inválido
            return {
                "domain": domain,
                "slos": []
            }
        
        return config
    except Exception as e:
        # Fallback robusto em caso de erro de leitura
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"❌ Erro ao carregar configuração SLO: {e}. Usando configuração padrão.")
        return {
            "domain": domain,
            "slos": []
        }


def get_slo_config_path(domain: str) -> str:
    """Retorna caminho do arquivo de configuração SLO"""
    domain_lower = domain.lower()
    return str(CONFIG_DIR / f"slo_{domain_lower}.yaml")

