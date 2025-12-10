"""
Utilitário para cálculo do Hash SHA-256 do SLA-aware
Conforme Capítulo 6 - BC-NSSMF
"""
import hashlib
import json
from typing import Dict, Any


def calculate_sla_hash(sla_aware: Dict[str, Any]) -> str:
    """
    Calcula hash SHA-256 do SLA-aware conforme Capítulo 6
    
    O hash deve ser calculado sobre a estrutura completa do SLA-aware,
    excluindo apenas o campo slaHash (para evitar recursão).
    
    Args:
        sla_aware: Dicionário com estrutura SLA-aware completa
        
    Returns:
        Hash SHA-256 em formato hexadecimal (0x...)
    """
    # Criar cópia sem o campo slaHash para evitar recursão
    sla_for_hash = {k: v for k, v in sla_aware.items() if k != "slaHash"}
    
    # Ordenar chaves para garantir determinismo
    sorted_sla = dict(sorted(sla_for_hash.items()))
    
    # Serializar para JSON de forma determinística
    # Usar separadores sem espaços e ordenar chaves
    json_str = json.dumps(sorted_sla, sort_keys=True, separators=(',', ':'))
    
    # Calcular SHA-256
    hash_bytes = hashlib.sha256(json_str.encode('utf-8')).digest()
    
    # Converter para hexadecimal com prefixo 0x
    hash_hex = "0x" + hash_bytes.hex()
    
    return hash_hex


def convert_slos_to_numeric(sla_requirements: Dict[str, Any], decision: str) -> list:
    """
    Converte SLA requirements para SLOs numéricos válidos
    Remove strings inválidas como "REJECT", "REQUIRED", etc.
    
    Args:
        sla_requirements: Dicionário com requisitos do SLA
        decision: Decisão (ACCEPT/REJECT) - NÃO deve ser SLO
        
    Returns:
        Lista de SLOs no formato {name, value, threshold}
    """
    slos = []
    
    # Mapeamento de campos para SLOs numéricos
    slo_mappings = {
        "latency": {"unit": "ms", "default_threshold_multiplier": 2},
        "latency_maxima_ms": {"unit": "ms", "default_threshold_multiplier": 2},
        "reliability": {"unit": "percent", "default_threshold_multiplier": 1},
        "confiabilidade_percent": {"unit": "percent", "default_threshold_multiplier": 1},
        "availability": {"unit": "percent", "default_threshold_multiplier": 1},
        "disponibilidade_percent": {"unit": "percent", "default_threshold_multiplier": 1},
        "throughput_dl": {"unit": "mbps", "default_threshold_multiplier": 1},
        "throughput_min_dl_mbps": {"unit": "mbps", "default_threshold_multiplier": 1},
        "throughput_ul": {"unit": "mbps", "default_threshold_multiplier": 1},
        "throughput_min_ul_mbps": {"unit": "mbps", "default_threshold_multiplier": 1},
        "jitter": {"unit": "ms", "default_threshold_multiplier": 2},
        "packet_loss": {"unit": "percent", "default_threshold_multiplier": 1},
    }
    
    for key, value in sla_requirements.items():
        # Ignorar campos não numéricos ou inválidos
        if key in ["decision", "status", "type", "slice_type", "service_type", "template_id"]:
            continue
        
        if value is None:
            continue
        
        # Tentar converter para número
        numeric_value = None
        if isinstance(value, (int, float)):
            numeric_value = int(value)
        elif isinstance(value, str):
            # Remover unidades e converter
            value_clean = value.replace("ms", "").replace("Mbps", "").replace("mbps", "").replace("%", "").replace(",", ".").strip()
            try:
                # Converter para inteiro (multiplicar por 1000 para ms, 100 para percent)
                if "ms" in value.lower() or key in ["latency", "latency_maxima_ms", "jitter"]:
                    numeric_value = int(float(value_clean) * 1000)  # ms em microsegundos
                elif "%" in value or key in ["reliability", "availability", "confiabilidade_percent", "disponibilidade_percent", "packet_loss"]:
                    numeric_value = int(float(value_clean) * 100)  # percent em centésimos
                elif "mbps" in value.lower() or key in ["throughput_dl", "throughput_ul", "throughput_min_dl_mbps", "throughput_min_ul_mbps"]:
                    numeric_value = int(float(value_clean))  # Mbps como inteiro
                else:
                    numeric_value = int(float(value_clean))
            except (ValueError, TypeError):
                continue
        
        if numeric_value is None or numeric_value < 0:
            continue
        
        # Calcular threshold (usar multiplicador padrão se não especificado)
        mapping = slo_mappings.get(key, {})
        threshold_multiplier = mapping.get("default_threshold_multiplier", 1)
        threshold = numeric_value * threshold_multiplier
        
        # Adicionar SLO
        slos.append({
            "name": key,
            "value": numeric_value,
            "threshold": threshold
        })
    
    # Garantir pelo menos um SLO
    if not slos:
        # SLO padrão se nenhum for encontrado
        slos.append({
            "name": "latency",
            "value": 10000,  # 10ms em microsegundos
            "threshold": 20000  # 20ms em microsegundos
        })
    
    return slos
