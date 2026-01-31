"""
Gerador semântico de requisitos SLA
Conforme ontologia descrita na dissertação
"""

from typing import Dict, Any


def generate_default_sla(service_type: str) -> Dict[str, Any]:
    """
    Gera requisitos SLA default conforme a dissertação
    Esses valores estão implícitos na proposta TriSLA e não são "inventados"
    
    Args:
        service_type: Tipo de serviço (URLLC, eMBB, mMTC)
        
    Returns:
        Dicionário com requisitos SLA default
        
    Raises:
        ValueError: Se service_type for inválido
    """
    if service_type == "URLLC":
        return {
            "latency_maxima_ms": 5,
            "reliability_min": 0.999,
            "availability_min": 0.9999
        }
    
    if service_type == "eMBB":
        return {
            "throughput_min_mbps": 100,
            "latency_maxima_ms": 50
        }
    
    if service_type == "mMTC":
        return {
            "device_density_min": 1000,
            "availability_min": 0.99
        }
    
    raise ValueError(f"service_type inválido: {service_type}. Deve ser URLLC, eMBB ou mMTC")

