"""
Metrics Collector - NASP Adapter
Coleta métricas reais do NASP e Prometheus (telemetria real).
PROMPT_SMDCE_V1: endpoint /api/v1/metrics/multidomain retorna schema SSOT.
PROMPT_STELEMETRY_REAL_ACTIVATION: Prometheus como fonte para CPU%, Mem%, UE count.
"""

from typing import Dict, Any, List, Optional, Iterable
from opentelemetry import trace
from prometheus_client import Gauge

import sys
import os
import requests
import re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nasp_client import NASPClient

tracer = trace.get_tracer(__name__)

# PRB real (RAN): exportado para consumo do portal-backend via Prometheus.
# Unidade adotada: percentual [0, 100].
TRISLA_RAN_PRB_UTILIZATION = Gauge(
    "trisla_ran_prb_utilization",
    "RAN PRB utilization collected from NASP RAN metrics endpoint (percent 0-100)",
)

# Prometheus (telemetria real) — PROMPT_STELEMETRY_REAL_ACTIVATION
PROM_URL = os.getenv(
    "PROMETHEUS_URL",
    "http://monitoring-kube-prometheus-prometheus.monitoring.svc.cluster.local:9090",
)


def _prom_query(query: str) -> Optional[Dict[str, Any]]:
    """Executa query no Prometheus. Em erro retorna None (nunca crasha)."""
    try:
        r = requests.get(
            f"{PROM_URL}/api/v1/query",
            params={"query": query},
            timeout=5,
        )
        return r.json()
    except Exception:
        return None


def _prom_scalar(resp: Optional[Dict[str, Any]]) -> Optional[float]:
    """Extrai valor escalar da resposta Prometheus (data.result[0].value[1])."""
    if not resp or resp.get("status") != "success":
        return None
    data = resp.get("data") or {}
    results = data.get("result") or []
    if not results:
        return None
    val = results[0].get("value")
    if not val or len(val) < 2:
        return None
    try:
        return float(val[1])
    except (TypeError, ValueError):
        return None


def _collect_prometheus_trisla() -> Dict[str, Any]:
    """
    Coleta métricas do namespace trisla via Prometheus (telemetria real).
    Retorna dict com cpu_pct, mem_pct, ue_count (proxy), rtt_p95_ms (null se indisponível).
    Em falha retorna valores None; nunca levanta exceção.
    """
    out: Dict[str, Any] = {
        "cpu_pct": None,
        "mem_pct": None,
        "ue_count": None,
        "rtt_p95_ms": None,
    }
    try:
        # CPU %: uso trisla / total cluster
        q_cpu = 'sum(rate(container_cpu_usage_seconds_total{namespace="trisla"}[1m]))/sum(rate(node_cpu_seconds_total[1m]))*100'
        v = _prom_scalar(_prom_query(q_cpu))
        if v is not None:
            out["cpu_pct"] = round(float(v), 2)

        # Mem %: uso trisla / total memória dos nós
        q_mem_usage = 'sum(container_memory_usage_bytes{namespace="trisla"})'
        q_mem_total = "sum(node_memory_MemTotal_bytes)"
        usage = _prom_scalar(_prom_query(q_mem_usage))
        total = _prom_scalar(_prom_query(q_mem_total))
        if usage is not None and total is not None and total > 0:
            out["mem_pct"] = round(float(usage) / float(total) * 100, 2)

        # UE count: proxy = pods Running no trisla (ou ueransim se existir)
        q_ue = 'count(kube_pod_status_phase{namespace="trisla",phase="Running"})'
        v = _prom_scalar(_prom_query(q_ue))
        if v is not None:
            out["ue_count"] = int(v)

        # RTT (Transporte): blackbox probe (tcp_connect) — política determinística (worst-case)
        rtt = _collect_transport_rtt_prometheus()
        if rtt is not None:
            out["rtt_p95_ms"] = round(float(rtt), 3)
    except Exception:
        pass
    return out


def _to_float(value: Any) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _normalize_prb_percent(value: Optional[float]) -> Optional[float]:
    """
    Normaliza PRB para percentual [0, 100].
    - Se vier como fração [0,1], converte para percentual.
    - Se vier fora da faixa, descarta (None) para evitar dado inválido.
    """
    if value is None:
        return None
    if 0.0 <= value <= 1.0:
        value = value * 100.0
    if value < 0.0 or value > 100.0:
        return None
    return round(float(value), 4)


def _walk_numbers_for_prb(data: Any) -> Iterable[float]:
    """
    Percorre payload JSON e retorna candidatos numéricos para chaves contendo "prb".
    """
    if isinstance(data, dict):
        for k, v in data.items():
            key = str(k).lower()
            if "prb" in key and isinstance(v, (int, float, str)):
                num = _to_float(v)
                if num is not None:
                    yield num
            yield from _walk_numbers_for_prb(v)
    elif isinstance(data, list):
        for item in data:
            yield from _walk_numbers_for_prb(item)


_PRB_PROM_LINE = re.compile(
    r"^\s*([a-zA-Z_:][a-zA-Z0-9_:]*)\{[^}]*\}\s+(-?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?)\s*$"
)
_PRB_PROM_SIMPLE = re.compile(
    r"^\s*([a-zA-Z_:][a-zA-Z0-9_:]*)\s+(-?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?)\s*$"
)


def _extract_prb_from_prom_text(raw_text: str) -> Optional[float]:
    """
    Extrai PRB de payload Prometheus text exposition quando disponível.
    Usa média dos samples cujo nome de métrica contém "prb".
    """
    values: List[float] = []
    for line in raw_text.splitlines():
        if not line or line.startswith("#"):
            continue
        m = _PRB_PROM_LINE.match(line) or _PRB_PROM_SIMPLE.match(line)
        if not m:
            continue
        metric_name = m.group(1).lower()
        if "prb" not in metric_name:
            continue
        number = _to_float(m.group(2))
        if number is None:
            continue
        values.append(number)

    if not values:
        return None

    avg = sum(values) / len(values)
    return _normalize_prb_percent(avg)


def _extract_ran_prb_percent(ran_payload: Any) -> Optional[float]:
    """
    Extrai PRB real do payload RAN retornado pelo NASP Client.
    Fonte primária: campos "prb*" em JSON.
    Fonte secundária: métricas em texto bruto (/metrics) contendo "prb".
    """
    if not isinstance(ran_payload, dict):
        return None

    # 1) JSON com chaves "prb*"
    nums = list(_walk_numbers_for_prb(ran_payload))
    if nums:
        normalized = [_normalize_prb_percent(v) for v in nums]
        valid = [v for v in normalized if v is not None]
        if valid:
            return round(sum(valid) / len(valid), 4)

    # 2) Texto Prometheus bruto em "raw"
    raw = ran_payload.get("raw")
    if isinstance(raw, str):
        return _extract_prb_from_prom_text(raw)

    return None

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

            # PRB real: extrair do payload RAN e exportar em métrica Prometheus.
            try:
                prb_percent = _extract_ran_prb_percent(all_metrics.get("ran"))
                if prb_percent is not None:
                    all_metrics["ran"]["prb_utilization"] = prb_percent
                    all_metrics["ran"]["prb_unit"] = "percent_0_100"
                    TRISLA_RAN_PRB_UTILIZATION.set(prb_percent)
            except Exception:
                pass
            
            # Coletar métricas Transport (UPF)
            try:
                all_metrics["transport"] = await self.nasp_client.get_transport_metrics()
            except Exception as e:
                all_metrics["transport"] = {"error": str(e)}
            
            # Coletar métricas Core (UPF, AMF, SMF)
            try:
                core_metrics = await self.nasp_client.get_core_metrics()
                if not isinstance(core_metrics, dict):
                    core_metrics = {}
                all_metrics["core"] = {
                    "upf": dict(core_metrics),
                    "amf_endpoint": self.nasp_client.core_amf_endpoint,
                    "smf_endpoint": self.nasp_client.core_smf_endpoint
                }
            except Exception as e:
                all_metrics["core"] = {
                    "upf": {},
                    "amf_endpoint": getattr(self.nasp_client, "core_amf_endpoint", ""),
                    "smf_endpoint": getattr(self.nasp_client, "core_smf_endpoint", ""),
                    "error": str(e),
                }

            # Telemetria real: Prometheus (CPU%, Mem%, UE proxy) — sobrescreve quando disponível
            try:
                prom = _collect_prometheus_trisla()
                upf = all_metrics["core"].get("upf")
                if isinstance(upf, dict):
                    if prom.get("cpu_pct") is not None:
                        upf["cpu_pct"] = prom["cpu_pct"]
                    if prom.get("mem_pct") is not None:
                        upf["mem_pct"] = prom["mem_pct"]
                if prom.get("ue_count") is not None and isinstance(all_metrics.get("ran"), dict):
                    all_metrics["ran"]["ue"] = {"active_count": prom["ue_count"]}
                if prom.get("rtt_p95_ms") is not None and isinstance(all_metrics.get("transport"), dict):
                    all_metrics["transport"]["rtt_p95_ms"] = prom["rtt_p95_ms"]
            except Exception:
                pass

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


# ============================
# RTT REAL VIA BLACKBOX
# ============================

def _collect_transport_rtt_prometheus() -> float | None:
    """
    RTT de Transporte baseado em blackbox_exporter (tcp_connect).
    Política DevOps determinística: retornar o pior caso (max) do job do probe.
    Retorna RTT em ms (float) ou None.
    """
    try:
        prom_url = os.getenv(
            "PROMETHEUS_URL",
            "http://monitoring-kube-prometheus-prometheus.monitoring.svc.cluster.local:9090"
        )

        # Pior caso do job (max) em segundos -> ms
        query = 'max(probe_duration_seconds{job="probe/monitoring/trisla-transport-tcp-probe"}) * 1000'

        resp = requests.get(
            f"{prom_url}/api/v1/query",
            params={"query": query},
            timeout=5
        )
        if resp.status_code != 200:
            return None

        data = resp.json()
        if not isinstance(data, dict) or data.get("status") != "success":
            return None

        result = (data.get("data") or {}).get("result") or []
        if not result:
            return None

        value = result[0].get("value")
        if not value or len(value) < 2:
            return None

        return float(value[1])
    except Exception:
        return None
