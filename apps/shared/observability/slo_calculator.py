"""
SLO Calculator - TriSLA
Cálculo de SLO por interface (I-01 a I-07)
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class SLOCalculator:
    """
    Calculador de SLO por interface
    
    Calcula compliance com SLOs para cada interface (I-01 a I-07)
    """
    
    # SLOs por interface (targets)
    SLO_TARGETS = {
        "I-01": {
            "latency_p99_ms": 100,  # 100ms p99
            "throughput_rps": 100,  # 100 req/s
            "error_rate": 0.01,  # 1% de erro
            "availability": 0.99  # 99% de disponibilidade
        },
        "I-02": {
            "latency_p99_ms": 200,  # 200ms p99
            "throughput_rps": 50,  # 50 msg/s
            "error_rate": 0.01,  # 1% de erro
            "availability": 0.99  # 99% de disponibilidade
        },
        "I-03": {
            "latency_p99_ms": 200,  # 200ms p99
            "throughput_rps": 50,  # 50 msg/s
            "error_rate": 0.01,  # 1% de erro
            "availability": 0.99  # 99% de disponibilidade
        },
        "I-04": {
            "latency_p99_ms": 500,  # 500ms p99 (blockchain)
            "throughput_rps": 10,  # 10 req/s
            "error_rate": 0.05,  # 5% de erro (blockchain pode ter mais erros)
            "availability": 0.95  # 95% de disponibilidade
        },
        "I-05": {
            "latency_p99_ms": 200,  # 200ms p99
            "throughput_rps": 50,  # 50 msg/s
            "error_rate": 0.01,  # 1% de erro
            "availability": 0.99  # 99% de disponibilidade
        },
        "I-06": {
            "latency_p99_ms": 200,  # 200ms p99
            "throughput_rps": 50,  # 50 msg/s
            "error_rate": 0.01,  # 1% de erro
            "availability": 0.99  # 99% de disponibilidade
        },
        "I-07": {
            "latency_p99_ms": 1000,  # 1000ms p99 (NASP pode ser mais lento)
            "throughput_rps": 20,  # 20 req/s
            "error_rate": 0.05,  # 5% de erro
            "availability": 0.95  # 95% de disponibilidade
        }
    }
    
    def __init__(self):
        """Inicializa calculador de SLO"""
        self.metrics_cache: Dict[str, Dict[str, Any]] = {}
    
    def calculate_slo_compliance(
        self,
        interface: str,
        latency_p99_ms: float,
        throughput_rps: float,
        error_rate: float,
        availability: float
    ) -> Dict[str, Any]:
        """
        Calcula compliance com SLO para uma interface
        
        Args:
            interface: Nome da interface (I-01 a I-07)
            latency_p99_ms: Latência p99 em milissegundos
            throughput_rps: Throughput em requisições por segundo
            error_rate: Taxa de erro (0.0 a 1.0)
            availability: Disponibilidade (0.0 a 1.0)
        
        Returns:
            Dicionário com compliance e status
        """
        if interface not in self.SLO_TARGETS:
            logger.warning(f"⚠️ Interface {interface} não tem SLO definido")
            return {
                "interface": interface,
                "compliance": 0.0,
                "status": "UNKNOWN",
                "violations": []
            }
        
        targets = self.SLO_TARGETS[interface]
        violations = []
        compliance_scores = []
        
        # Verificar latência
        if latency_p99_ms > targets["latency_p99_ms"]:
            violations.append("latency")
            compliance_scores.append(0.0)
        else:
            # Score baseado em quão próximo está do target
            score = 1.0 - (latency_p99_ms / targets["latency_p99_ms"] - 1.0) if latency_p99_ms > 0 else 1.0
            compliance_scores.append(max(0.0, min(1.0, score)))
        
        # Verificar throughput
        if throughput_rps < targets["throughput_rps"]:
            violations.append("throughput")
            compliance_scores.append(0.0)
        else:
            # Score baseado em quão acima está do target
            score = min(1.0, targets["throughput_rps"] / throughput_rps) if throughput_rps > 0 else 0.0
            compliance_scores.append(score)
        
        # Verificar error rate
        if error_rate > targets["error_rate"]:
            violations.append("error_rate")
            compliance_scores.append(0.0)
        else:
            # Score baseado em quão abaixo está do target
            score = 1.0 - (error_rate / targets["error_rate"]) if targets["error_rate"] > 0 else 1.0
            compliance_scores.append(max(0.0, min(1.0, score)))
        
        # Verificar disponibilidade
        if availability < targets["availability"]:
            violations.append("availability")
            compliance_scores.append(0.0)
        else:
            # Score baseado em quão acima está do target
            score = min(1.0, availability / targets["availability"])
            compliance_scores.append(score)
        
        # Calcular compliance geral (média ponderada)
        overall_compliance = sum(compliance_scores) / len(compliance_scores) if compliance_scores else 0.0
        
        # Determinar status
        if violations:
            status = "VIOLATED"
        elif overall_compliance < 0.8:
            status = "AT_RISK"
        else:
            status = "OK"
        
        result = {
            "interface": interface,
            "compliance": overall_compliance,
            "status": status,
            "violations": violations,
            "metrics": {
                "latency_p99_ms": latency_p99_ms,
                "throughput_rps": throughput_rps,
                "error_rate": error_rate,
                "availability": availability
            },
            "targets": targets,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Cache resultado
        self.metrics_cache[interface] = result
        
        return result
    
    def calculate_all_slos(self, metrics_by_interface: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """
        Calcula SLO para todas as interfaces
        
        Args:
            metrics_by_interface: Dicionário com métricas por interface
                {
                    "I-01": {
                        "latency_p99_ms": 95.0,
                        "throughput_rps": 105.0,
                        "error_rate": 0.005,
                        "availability": 0.995
                    },
                    ...
                }
        
        Returns:
            Dicionário com compliance de todas as interfaces
        """
        all_compliance = {}
        overall_compliance = 0.0
        total_interfaces = 0
        
        for interface in ["I-01", "I-02", "I-03", "I-04", "I-05", "I-06", "I-07"]:
            if interface in metrics_by_interface:
                metrics = metrics_by_interface[interface]
                compliance = self.calculate_slo_compliance(
                    interface=interface,
                    latency_p99_ms=metrics.get("latency_p99_ms", 0.0),
                    throughput_rps=metrics.get("throughput_rps", 0.0),
                    error_rate=metrics.get("error_rate", 0.0),
                    availability=metrics.get("availability", 0.0)
                )
                all_compliance[interface] = compliance
                overall_compliance += compliance["compliance"]
                total_interfaces += 1
        
        overall_compliance = overall_compliance / total_interfaces if total_interfaces > 0 else 0.0
        
        return {
            "overall_compliance": overall_compliance,
            "interfaces": all_compliance,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def get_slo_targets(self) -> Dict[str, Dict[str, Any]]:
        """Retorna SLOs targets para todas as interfaces"""
        return self.SLO_TARGETS.copy()






