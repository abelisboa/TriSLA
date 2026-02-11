"""
3GPP Reality Gate - NASP Adapter
PROMPT_S3GPP_GATE_v1.0: Valida pré-condições 3GPP reais antes de ACCEPT/instantiate.
Sem criar sessão PDU; usa evidências e proxies reais (pods, readiness, métricas existentes).
"""

import os
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Namespaces configuráveis (defaults alinhados ao ambiente NASP auditado)
GATE_CORE_NAMESPACE = os.getenv("GATE_3GPP_CORE_NAMESPACE", "ns-1274485")
GATE_UERANSIM_NAMESPACE = os.getenv("GATE_3GPP_UERANSIM_NAMESPACE", "ueransim")
# Limiar para teste de falha controlada: UPF_MAX_SESSIONS=0 força upf_capacity_ok=False
UPF_MAX_SESSIONS = int(os.getenv("UPF_MAX_SESSIONS", "999999"))
UPF_CPU_LIMIT_PCT = float(os.getenv("UPF_CPU_LIMIT_PCT", "85.0"))
UPF_MEM_LIMIT_PCT = float(os.getenv("UPF_MEM_LIMIT_PCT", "85.0"))

# Slice types suportados (G4 - política aplicável)
SUPPORTED_SLICE_TYPES = {"URLLC", "eMBB", "mMTC"}


def _normalize_slice_type(s: str) -> str:
    u = (s or "").strip().upper()
    if u == "EMBB":
        return "eMBB"
    if u == "URLLC":
        return "URLLC"
    if u == "MMTC":
        return "mMTC"
    return (s or "").strip()


def _get_k8s_core_v1():
    """Obtém CoreV1Api usando in-cluster config (reutiliza auth do NSIController)."""
    from controllers.k8s_auth import load_incluster_config_with_validation
    from kubernetes import client
    api_client, _, _, _ = load_incluster_config_with_validation()
    return client.CoreV1Api(api_client=api_client)


def _pods_ready_in_namespace(core_v1, namespace: str, name_substrings: List[str]) -> tuple[bool, List[str]]:
    """
    Verifica se existe pelo menos um pod Running/Ready para cada substring em name_substrings.
    Retorna (all_ok, reasons).
    """
    if not namespace or namespace.strip() == "":
        return True, ["namespace not configured, skip"]
    reasons = []
    try:
        ret = core_v1.list_namespaced_pod(namespace=namespace, watch=False)
    except Exception as e:
        logger.warning(f"[GATE] list_namespaced_pod {namespace}: {e}")
        return False, [f"list_pods_error:{namespace}:{e}"]
    pods_by_sub = {s: [] for s in name_substrings}
    for p in ret.items:
        phase = getattr(p.status, "phase", None)
        ready = False
        if getattr(p.status, "conditions", None):
            for c in p.status.conditions:
                if getattr(c, "type", None) == "Ready" and getattr(c, "status", None) == "True":
                    ready = True
                    break
        if phase != "Running" or not ready:
            continue
        name = getattr(p.metadata, "name", "") or ""
        for sub in name_substrings:
            if sub.lower() in name.lower():
                pods_by_sub[sub].append(name)
                break
    all_ok = True
    for sub in name_substrings:
        if not pods_by_sub[sub]:
            all_ok = False
            reasons.append(f"missing_ready_pod:{sub}")
        else:
            reasons.append(f"ok:{sub}")
    return all_ok, reasons


def run_gate(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Executa o Gate 3GPP Real.
    payload: opcional para POST; pode conter slice_type, thresholds, etc.
    Retorna JSON no formato exigido: gate, reasons, checks, timestamp.
    """
    payload = payload or {}
    slice_type = _normalize_slice_type(
        payload.get("slice_type") or payload.get("serviceProfile") or "eMBB"
    )
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    reasons: List[str] = []
    checks = {
        "core_ready": False,
        "ueransim_ready": False,
        "upf_capacity_ok": False,
        "policy_applicable": False,
    }

    core_v1 = None
    # G1: Core (AMF, SMF, UPF, PCF, NRF) operacionais
    try:
        core_v1 = _get_k8s_core_v1()
        core_ok, core_reasons = _pods_ready_in_namespace(
            core_v1, GATE_CORE_NAMESPACE, ["amf", "smf", "upf", "pcf", "nrf"]
        )
        checks["core_ready"] = core_ok
        reasons.extend([f"core:{r}" for r in core_reasons])
    except Exception as e:
        logger.exception("[GATE] core check failed")
        reasons.append(f"core_error:{e}")
        checks["core_ready"] = False

    # G1: UERANSIM (gNB/UE) operacional
    try:
        if core_v1 is None:
            core_v1 = _get_k8s_core_v1()
        ue_ok, ue_reasons = _pods_ready_in_namespace(core_v1, GATE_UERANSIM_NAMESPACE, ["ueransim"])
        checks["ueransim_ready"] = ue_ok
        reasons.extend([f"ueransim:{r}" for r in ue_reasons])
    except Exception as e:
        logger.exception("[GATE] ueransim check failed")
        reasons.append(f"ueransim_error:{e}")
        checks["ueransim_ready"] = False

    # G3: Capacidade proxy UPF (Running/Ready; limiar UPF_MAX_SESSIONS=0 força FAIL para teste)
    if UPF_MAX_SESSIONS <= 0:
        checks["upf_capacity_ok"] = False
        reasons.append("upf_capacity:UPF_MAX_SESSIONS=0 (forced fail for test)")
    elif checks["core_ready"]:
        # UPF já considerado em core_ready; capacidade ok se core ok (sem métrica PFCP aqui)
        checks["upf_capacity_ok"] = True
        reasons.append("upf_capacity:ok")
    else:
        reasons.append("upf_capacity:skip_core_not_ready")
        checks["upf_capacity_ok"] = False

    # G4: QoS policy aplicável (slice_type suportado e PCF/SMF ativos)
    checks["policy_applicable"] = (
        slice_type in SUPPORTED_SLICE_TYPES and checks["core_ready"]
    )
    if not checks["policy_applicable"]:
        if slice_type not in SUPPORTED_SLICE_TYPES:
            reasons.append(f"policy:unsupported_slice_type:{slice_type}")
        else:
            reasons.append("policy:core_not_ready")

    gate = "PASS" if all(checks.values()) else "FAIL"
    if gate == "FAIL":
        logger.info(f"[GATE] 3GPP Gate FAIL: {reasons}")
    else:
        logger.info(f"[GATE] 3GPP Gate PASS")

    return {
        "gate": gate,
        "reasons": reasons,
        "checks": checks,
        "timestamp": timestamp,
    }
