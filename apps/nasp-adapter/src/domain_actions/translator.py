from typing import Any, Dict

def translate_sla_to_domain_actions(
    sla: Dict[str, Any],
    decision: Dict[str, Any],
    telemetry_snapshot: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Formaliza a tradução SLA -> ações por domínio sem substituir o fluxo existente.
    Esta função apenas explicita e serializa as ações derivadas para evidência,
    auditoria e consumo pelo NASP Adapter.
    """
    form_values = sla.get("form_values", sla)
    slice_type = str(form_values.get("slice_type", form_values.get("service_type", ""))).lower()

    ran = telemetry_snapshot.get("ran", telemetry_snapshot.get("RAN", {})) if telemetry_snapshot else {}
    tn = telemetry_snapshot.get("transport", telemetry_snapshot.get("tn", telemetry_snapshot.get("TN", {}))) if telemetry_snapshot else {}
    cn = telemetry_snapshot.get("core", telemetry_snapshot.get("cn", telemetry_snapshot.get("CN", {}))) if telemetry_snapshot else {}

    if slice_type == "urllc":
        ran_policy = "latency_priority"
        tn_policy = "low_latency_path"
        cn_policy = "priority_control_plane"
    elif slice_type == "embb":
        ran_policy = "throughput_balanced"
        tn_policy = "high_throughput_path"
        cn_policy = "balanced_core_allocation"
    elif slice_type == "mmtc":
        ran_policy = "massive_access_efficient"
        tn_policy = "efficient_aggregate_path"
        cn_policy = "lightweight_session_handling"
    else:
        ran_policy = "default"
        tn_policy = "default"
        cn_policy = "default"

    return {
        "domain_actions_version": "v1",
        "slice_type": slice_type or "unknown",
        "decision": decision.get("decision", decision.get("status", "unknown")) if isinstance(decision, dict) else str(decision),
        "ran_actions": {
            "interface": "RAN-I1",
            "policy": ran_policy,
            "evidence": ran,
        },
        "tn_actions": {
            "interface": "TN-I1",
            "policy": tn_policy,
            "evidence": tn,
        },
        "cn_actions": {
            "interface": "CN-I1",
            "policy": cn_policy,
            "evidence": cn,
        },
    }
