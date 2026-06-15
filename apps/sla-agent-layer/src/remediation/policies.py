"""Default remediation policies (simulation mode)."""
from __future__ import annotations

from typing import Any, Dict

from remediation.models import Action, Condition, RemediationPolicy, Rollback, Rule, Verification


def _sim_adjust_prb(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    ran = dict(snapshot.get("ran") or {})
    prb = float(ran.get("prb_utilization") or 0.0)
    if prb > 1.0:
        prb = prb / 100.0
    simulated = max(0.0, prb - 0.12)
    if simulated <= 1.0:
        simulated *= 100.0
    return {"ran": {**ran, "prb_utilization": simulated}, "simulated": True}


def _sim_recompute_path(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    tr = dict(snapshot.get("transport") or {})
    lat = float(tr.get("latency_ms") or tr.get("rtt") or 5.0)
    return {
        "transport": {**tr, "latency_ms": max(1.0, lat * 0.9)},
        "simulated": True,
    }


def _sim_reschedule_nf(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    core = dict(snapshot.get("core") or {})
    cpu = float(core.get("cpu_utilization") or core.get("cpu") or 0.01)
    return {
        "core": {**core, "cpu_utilization": max(0.001, cpu * 0.85)},
        "simulated": True,
    }


def default_remediation_policy() -> RemediationPolicy:
    return RemediationPolicy(
        policy_id="trisla-default-simulation-v1",
        mode="simulation",
        rules=[
            Rule(
                rule_id="ran-prb-saturation",
                condition=Condition(
                    metric="prb_utilization",
                    operator="gte",
                    threshold=25.0,
                    domain="ran",
                ),
                action=Action(
                    name="adjust_prb_policy",
                    domain="RAN",
                    description="Simulated PRB policy adjustment",
                    simulate=_sim_adjust_prb,
                ),
                verification=Verification(
                    metric="prb_utilization",
                    domain="ran",
                    expected_improvement_min=-5.0,
                ),
                rollback=Rollback(),
            ),
            Rule(
                rule_id="transport-path-degrade",
                condition=Condition(
                    metric="latency_ms",
                    operator="gte",
                    threshold=15.0,
                    domain="transport",
                ),
                action=Action(
                    name="recompute_path",
                    domain="Transport",
                    description="Simulated transport path recompute",
                    simulate=_sim_recompute_path,
                ),
                verification=Verification(
                    metric="latency_ms",
                    domain="transport",
                    expected_improvement_min=-1.0,
                ),
            ),
            Rule(
                rule_id="core-cpu-pressure",
                condition=Condition(
                    metric="cpu_utilization",
                    operator="gte",
                    threshold=0.5,
                    domain="core",
                ),
                action=Action(
                    name="reschedule_nf",
                    domain="Core",
                    description="Simulated NF reschedule",
                    simulate=_sim_reschedule_nf,
                ),
                verification=Verification(
                    metric="cpu_utilization",
                    domain="core",
                    expected_improvement_min=-0.01,
                ),
            ),
        ],
    )
