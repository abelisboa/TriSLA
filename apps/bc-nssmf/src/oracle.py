"""
Metrics Oracle - BC-NSSMF
Oracle que coleta métricas reais do NASP para validação de smart contracts

Conforme dissertação TriSLA:
- Oracle conecta ao NASP Adapter para obter métricas reais
- Métricas são usadas para validar cláusulas de SLA no contrato Solidity
"""

from typing import Dict, Any
from opentelemetry import trace
import sys
import os

# Adicionar path para NASP Adapter
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "nasp-adapter",
    "src"
))

try:
    from nasp_client import NASPClient
    NASP_AVAILABLE = True
except ImportError:
    NASP_AVAILABLE = False
    print("⚠️ NASP Adapter não disponível. Oracle usará fallback.")

tracer = trace.get_tracer(__name__)


class MetricsOracle:
    """
    Oracle que coleta métricas reais do NASP para validação de smart contracts
    
    IMPORTANTE: Métricas devem ser coletadas do NASP Adapter real, não hardcoded.
    """
    
    def __init__(self, nasp_client: NASPClient = None):
        """
        Inicializa Oracle
        
        Args:
            nasp_client: Cliente NASP (padrão: cria novo se disponível)
        """
        if nasp_client:
            self.nasp_client = nasp_client
        elif NASP_AVAILABLE:
            self.nasp_client = NASPClient()
        else:
            self.nasp_client = None
            print("⚠️ Oracle sem NASP Adapter - usando fallback limitado")
    
    async def get_metrics(self) -> Dict[str, Any]:
        """
        Obtém métricas reais do NASP via NASP Adapter
        
        IMPORTANTE: Métricas são coletadas do NASP real, não hardcoded.
        
        Returns:
            Dicionário com métricas agregadas (latency, throughput, packet_loss, etc.)
        """
        with tracer.start_as_current_span("get_metrics_oracle") as span:
            if self.nasp_client:
                try:
                    # Coletar métricas reais do NASP
                    ran_metrics = await self.nasp_client.get_ran_metrics()
                    transport_metrics = await self.nasp_client.get_transport_metrics()
                    core_metrics = await self.nasp_client.get_core_metrics()
                    
                    # Agregar métricas
                    metrics = {
                        "latency": self._extract_latency(ran_metrics, transport_metrics, core_metrics),
                        "throughput": self._extract_throughput(ran_metrics, transport_metrics, core_metrics),
                        "packet_loss": self._extract_packet_loss(ran_metrics, transport_metrics, core_metrics),
                        "jitter": self._extract_jitter(ran_metrics, transport_metrics, core_metrics),
                        "reliability": self._extract_reliability(ran_metrics, transport_metrics, core_metrics),
                        "source": "nasp_real",
                        "timestamp": self._get_timestamp(),
                        "ran_metrics": ran_metrics,
                        "transport_metrics": transport_metrics,
                        "core_metrics": core_metrics
                    }
                    
                    span.set_attribute("metrics.source", "nasp_real")
                    span.set_attribute("metrics.latency", metrics["latency"])
                    span.set_attribute("metrics.throughput", metrics["throughput"])
                    
                    return metrics
                    
                except Exception as e:
                    span.record_exception(e)
                    print(f"⚠️ Erro ao coletar métricas do NASP: {e}")
                    # Fallback para métricas básicas
                    return self._get_fallback_metrics()
            else:
                # Fallback se NASP não disponível
                return self._get_fallback_metrics()
    
    def _extract_latency(self, ran: Dict, transport: Dict, core: Dict) -> float:
        """Extrai latência agregada das métricas"""
        latencies = []
        for metrics in [ran, transport, core]:
            if isinstance(metrics, dict):
                if "latency" in metrics:
                    latencies.append(float(metrics["latency"]))
                elif "delay" in metrics:
                    latencies.append(float(metrics["delay"]))
        return sum(latencies) / len(latencies) if latencies else 0.0
    
    def _extract_throughput(self, ran: Dict, transport: Dict, core: Dict) -> float:
        """Extrai throughput agregado das métricas"""
        throughputs = []
        for metrics in [ran, transport, core]:
            if isinstance(metrics, dict):
                if "throughput" in metrics:
                    throughputs.append(float(metrics["throughput"]))
                elif "bitrate" in metrics:
                    throughputs.append(float(metrics["bitrate"]))
        return sum(throughputs) if throughputs else 0.0
    
    def _extract_packet_loss(self, ran: Dict, transport: Dict, core: Dict) -> float:
        """Extrai packet loss agregado das métricas"""
        losses = []
        for metrics in [ran, transport, core]:
            if isinstance(metrics, dict):
                if "packet_loss" in metrics:
                    losses.append(float(metrics["packet_loss"]))
                elif "loss" in metrics:
                    losses.append(float(metrics["loss"]))
        return sum(losses) / len(losses) if losses else 0.0
    
    def _extract_jitter(self, ran: Dict, transport: Dict, core: Dict) -> float:
        """Extrai jitter agregado das métricas"""
        jitters = []
        for metrics in [ran, transport, core]:
            if isinstance(metrics, dict):
                if "jitter" in metrics:
                    jitters.append(float(metrics["jitter"]))
        return sum(jitters) / len(jitters) if jitters else 0.0
    
    def _extract_reliability(self, ran: Dict, transport: Dict, core: Dict) -> float:
        """Extrai reliability agregada das métricas"""
        reliabilities = []
        for metrics in [ran, transport, core]:
            if isinstance(metrics, dict):
                if "reliability" in metrics:
                    reliabilities.append(float(metrics["reliability"]))
        return sum(reliabilities) / len(reliabilities) if reliabilities else 0.99
    
    def _get_fallback_metrics(self) -> Dict[str, Any]:
        """Métricas de fallback (apenas se NASP não disponível)"""
        print("⚠️ Usando métricas de fallback (NASP não disponível)")
        return {
            "latency": 0.0,
            "throughput": 0.0,
            "packet_loss": 0.0,
            "jitter": 0.0,
            "reliability": 0.99,
            "source": "fallback",
            "timestamp": self._get_timestamp(),
            "warning": "NASP Adapter não disponível - métricas não são reais"
        }
    
    def _get_timestamp(self) -> str:
        """Retorna timestamp atual"""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()
