"""P4 — SLAStatusResponse schema alignment with GET /status router output."""
from __future__ import annotations

import json
from typing import Any

import pytest

from src.main import app
from src.schemas.sla import SLAStatusResponse

SCHEMA_FIELDS = [
    "sla_id",
    "status",
    "tenant_id",
    "intent_id",
    "nest_id",
    "created_at",
    "updated_at",
    "admission_decision",
    "runtime_lifecycle_enabled",
    "admission_telemetry_snapshot",
    "admission_decision_evidence",
    "admission_reasoning",
    "telemetry_snapshot",
    "runtime_assurance",
    "operational_summary",
    "traceability",
    "service_type",
    "sla_requirements",
]


def _status_payload(
    *,
    slice_type: str = "URLLC",
    decision: str = "ACCEPT",
    with_evidence: bool = True,
) -> dict[str, Any]:
    evidence = (
        [
            {
                "metric": "prb_utilization",
                "observed": 15.0,
                "threshold": 85.0,
                "delta": -70.0,
                "rule": "decision_score_mode",
                "unit": "%",
            }
        ]
        if with_evidence
        else None
    )
    return {
        "intent_id": f"intent-{slice_type.lower()}-p4",
        "status": "ACTIVE" if decision == "ACCEPT" else "TERMINATED",
        "tenant_id": "tenant-p4",
        "service_type": slice_type,
        "sla_requirements": {
            "slice_type": slice_type,
            "type": slice_type,
            "latency": "10ms",
            "throughput": "100Mbps",
            "reliability": 0.99999,
            "availability": 0.99999,
            "coverage": "Urban",
            "device_density": 1000,
        },
        "nest_id": f"nest-{slice_type.lower()}",
        "created_at": "2026-06-13T10:00:00Z",
        "updated_at": "2026-06-13T10:01:00Z",
        "metadata": {
            "final_decision": decision,
            "decision_evidence": evidence,
            "decision_explanation_plain": f"{slice_type} admission reasoning",
            "decision_snapshot": {"sla_id": f"intent-{slice_type.lower()}-p4", "decision": "AC"},
            "telemetry_snapshot": {
                "ran": {"prb_utilization": 0.15, "latency_ms": 5.0},
                "transport": {"latency_ms": 5.0},
                "core": {"cpu_utilization": 0.1},
            },
            "governance_event_id": "gov-p4",
        },
    }


def test_schema_declares_all_router_fields():
    model_fields = set(SLAStatusResponse.model_fields.keys())
    assert set(SCHEMA_FIELDS) == model_fields


def test_t1_openapi_generation_pass():
    schema = app.openapi()
    assert "paths" in schema
    status_path = schema["paths"].get("/api/v1/sla/status/{sla_id}")
    assert status_path is not None
    get_op = status_path.get("get")
    assert get_op is not None
    ref = get_op["responses"]["200"]["content"]["application/json"]["schema"]
    if "$ref" in ref:
        model_name = ref["$ref"].split("/")[-1]
        components = schema["components"]["schemas"][model_name]["properties"]
    else:
        components = ref.get("properties", {})
    for field in SCHEMA_FIELDS:
        assert field in components, f"missing OpenAPI field {field}"


def test_t2_router_payload_validates_100_percent():
    payload = {
        "sla_id": "intent-urllc-p4",
        "status": "ACTIVE",
        "tenant_id": "tenant-p4",
        "intent_id": "intent-urllc-p4",
        "nest_id": "nest-urllc",
        "created_at": "2026-06-13T10:00:00Z",
        "updated_at": "2026-06-13T10:01:00Z",
        "admission_decision": "ACCEPT",
        "runtime_lifecycle_enabled": True,
        "admission_telemetry_snapshot": {"ran": {"prb_utilization": 0.15}},
        "admission_decision_evidence": [
            {"metric": "prb_utilization", "observed": 15.0, "threshold": 85.0}
        ],
        "admission_reasoning": "Score contínuo 0.82 (ACCEPT)",
        "telemetry_snapshot": {"ran": {"latency_ms": 5.0}, "transport": {}, "core": {}},
        "runtime_assurance": {
            "state": "OK",
            "governance_clarity": {"blockchain_registration": {"executed": True}},
        },
        "operational_summary": {
            "lifecycle_status_label": "In Operation",
            "decision_score": 0.82,
            "semantic_validation": "Passed",
        },
        "traceability": {"trace_id": "trace-p4", "span_id": "span-p4"},
    }
    parsed = SLAStatusResponse.model_validate(payload)
    dumped = json.loads(parsed.model_dump_json())
    for key in SCHEMA_FIELDS:
        assert key in dumped


def test_t3_critical_nested_fields_present():
    payload = SLAStatusResponse(
        sla_id="x",
        status="ACTIVE",
        tenant_id="t",
        admission_decision_evidence=[{"metric": "prb_utilization", "observed": 1}],
        telemetry_snapshot={"ran": {}},
        runtime_assurance={"state": "OK"},
        operational_summary={"decision_score": 0.8},
    )
    data = payload.model_dump()
    assert data["admission_decision_evidence"][0]["metric"] == "prb_utilization"
    assert "telemetry_snapshot" in data
    assert "runtime_assurance" in data
    assert "operational_summary" in data


@pytest.mark.parametrize("slice_type", ["URLLC", "eMBB", "mMTC"])
def test_t4_slice_types_schema_acceptance(slice_type: str):
    """Schema accepts URLLC/eMBB/mMTC status-shaped payloads (no router change)."""
    sem = _status_payload(slice_type=slice_type)
    md = sem["metadata"]
    body = {
        "sla_id": sem["intent_id"],
        "status": sem["status"],
        "tenant_id": sem["tenant_id"],
        "intent_id": sem["intent_id"],
        "nest_id": sem["nest_id"],
        "created_at": sem["created_at"],
        "updated_at": sem["updated_at"],
        "admission_decision": md["final_decision"],
        "runtime_lifecycle_enabled": md["final_decision"] == "ACCEPT",
        "admission_telemetry_snapshot": md["telemetry_snapshot"],
        "admission_decision_evidence": md["decision_evidence"],
        "admission_reasoning": md["decision_explanation_plain"],
        "telemetry_snapshot": md["telemetry_snapshot"],
        "runtime_assurance": {"state": "OK", "governance_clarity": {}},
        "operational_summary": {
            "lifecycle_status_label": "In Operation",
            "decision_score": 0.82,
            "service_type": slice_type,
        },
        "traceability": {"trace_id": f"trace-{slice_type}"},
    }
    parsed = SLAStatusResponse.model_validate(body)
    assert parsed.operational_summary["service_type"] == slice_type
