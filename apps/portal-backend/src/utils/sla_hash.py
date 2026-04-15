import hashlib
import json


def convert_slos_to_numeric(slos):
    """
    Converte SLOs para formato numérico consistente.
    """
    result = []

    if not slos:
        return result

    for slo in slos:
        result.append({
            "name": slo.get("name"),
            "target": float(slo.get("target", 0)),
            "unit": slo.get("unit", "")
        })

    return result


def calculate_sla_hash(sla_data):
    """
    Calcula SHA-256 determinístico do SLA-aware.
    """
    normalized = json.dumps(
        sla_data,
        sort_keys=True,
        separators=(",", ":")
    )

    return hashlib.sha256(normalized.encode()).hexdigest()
