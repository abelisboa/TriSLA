"""
Metrics Collector - NASP Adapter
Coleta métricas reais do NASP.
PROMPT_SMDCE_V1: endpoint /api/v1/metrics/multidomain retorna schema SSOT (docs/MDCE_SCHEMA.json).
"""

from typing import Dict, Any, List
from opentelemetry import trace

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nasp_client import NASPClient

tracer = trace.get_tracer(__name__)

# Chaves canônicas do schema MDCE (SSOT)
MDCE_KEYS = [
    "core.upf.cpu_pct", "core.upf.mem_pct", "core.upf.tx_mbps", "core.upf.rx_mbps",
    "core.errors.pdu_fail_rate", "ran.ue.active_count", "transport.rtt_p95_ms",
]


def _extract_number(data: Dict[str, Any], *path: str, default: Any = None) -> Any:
    """Extrai número de data[path[0]][path[1]]... ou default."""
    cur = data
    for key in path:
        cur = cur.get(key) if isinstance(cur, dict) else None
        if cur is None:
            return default
    try:
        return float(cur) if isinstance(cur, (int, float)) else default
    except (TypeError, ValueError):
        return default


def build_multidomain_schema(raw: Dict[str, Any], timestamp: str) -> Dict[str, Any]:
    """
    Constrói o schema SSOT MDCE a partir da coleta bruta.
    Campos inexistentes retornam null e reasons incluem metric_unavailable.
    """
    reasons: List[str] = []
    core_upf = raw.get("core") or {}
    if isinstance(core_upf, dict) and "upf" in core_upf:
        core_upf = core_upf.get("upf") or {}
    else:
        core_upf = raw.get("core", {}).get("upf", {}) if isinstance(raw.get("core"), dict) else {}
    ran = raw.get("ran") or {}
    transport = raw.get("transport") or {}

    # Core UPF — tentar extrair de estruturas conhecidas; senão null
    cpu_pct = _extract_number(core_upf, "cpu_pct") or _extract_number(core_upf, "cpu_usage_pct")
    if cpu_pct is None:
        reasons.append("metric_unavailable:core.upf.cpu_pct")
    mem_pct = _extract_number(core_upf, "mem_pct") or _extract_number(core_upf, "memory_usage_pct")
    if mem_pct is None:
        reasons.append("metric_unavailable:core.upf.mem_pct")
    tx_mbps = _extract_number(core_upf, "tx_mbps") or _extract_number(core_upf, "throughput_tx_mbps")
    if tx_mbps is None:
        reasons.append("metric_unavailable:core.upf.tx_mbps")
    rx_mbps = _extract_number(core_upf, "rx_mbps") or _extract_number(core_upf, "throughput_rx_mbps")
    if rx_mbps is None:
        reasons.append("metric_unavailable:core.upf.rx_mbps")

    pdu_fail_rate = None
    if isinstance(raw.get("core"), dict) and isinstance(raw["core"].get("errors"), dict):
        pdu_fail_rate = raw["core"]["errors"].get("pdu_fail_rate")
    if pdu_fail_rate is None:
        reasons.append("metric_unavailable:core.errors.pdu_fail_rate")

    ue_count = None
    if isinstance(ran, dict):
        ue_count = ran.get("ue", {}).get("active_count") if isinstance(ran.get("ue"), dict) else ran.get("active_ue_count")
    if ue_count is not None:
        try:
            ue_count = int(ue_count)
        except (TypeError, ValueError):
            ue_count = None
    if ue_count is None:
        reasons.append("metric_unavailable:ran.ue.active_count")

    rtt_p95 = _extract_number(transport, "rtt_p95_ms") or _extract_number(transport, "rtt_p95")
    if rtt_p95 is None:
        reasons.append("metric_unavailable:transport.rtt_p95_ms")

    return {
        "core": {
            "upf": {
                "cpu_pct": cpu_pct,
                "mem_pct": mem_pct,
                "tx_mbps": tx_mbps,
                "rx_mbps": rx_mbps,
            },
            "errors": {"pdu_fail_rate": pdu_fail_rate},
        },
        "ran": {"ue": {"active_count": ue_count}},
        "transport": {"rtt_p95_ms": rtt_p95},
        "reasons": reasons,
        "timestamp": timestamp,
    }


class MetricsCollector:
    """Coleta métricas reais do NASP"""
    
    def __init__(self, nasp_client: NASPClient):
        self.nasp_client = nasp_client
    
    async def collect_all(self) -> Dict[str, Any]:
        """Coleta todas as métricas do NASP"""
        with tracer.start_as_current_span("collect_all_nasp_metrics") as span:
            # ⚠️ PRODUÇÃO REAL: Coleta real de métricas dos serviços descobertos
            all_metrics = {
                "ran": {},
                "transport": {},
                "core": {},
                "timestamp": self._get_timestamp(),
                "source": "nasp_real"
            }
            
            # Coletar métricas RAN (srsenb)
            try:
                all_metrics["ran"] = await self.nasp_client.get_ran_metrics()
            except Exception as e:
                all_metrics["ran"] = {"error": str(e)}
            
            # Coletar métricas Transport (UPF)
            try:
                all_metrics["transport"] = await self.nasp_client.get_transport_metrics()
            except Exception as e:
                all_metrics["transport"] = {"error": str(e)}
            
            # Coletar métricas Core (UPF, AMF, SMF)
            try:
                core_metrics = await self.nasp_client.get_core_metrics()
                all_metrics["core"] = {
                    "upf": core_metrics,
                    "amf_endpoint": self.nasp_client.core_amf_endpoint,
                    "smf_endpoint": self.nasp_client.core_smf_endpoint
                }
            except Exception as e:
                all_metrics["core"] = {"error": str(e)}
            
            span.set_attribute("metrics.domains", "ran,transport,core")
            span.set_attribute("metrics.source", "nasp_real")
            span.set_attribute("metrics.ran_endpoint", self.nasp_client.ran_endpoint)
            span.set_attribute("metrics.core_endpoint", self.nasp_client.core_endpoint)
            
            return all_metrics
    
    async def get_multidomain(self) -> Dict[str, Any]:
        """
        Retorna métricas no schema SSOT MDCE (docs/MDCE_SCHEMA.json).
        Usado por GET /api/v1/metrics/multidomain e pelo Decision Engine (MDCE v1).
        """
        raw = await self.collect_all()
        ts = self._get_timestamp()
        return build_multidomain_schema(raw, ts)
    
    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"

