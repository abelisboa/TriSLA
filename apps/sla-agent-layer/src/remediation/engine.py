"""Remediation engine — simulation mode closed loop."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from remediation.models import RemediationAttempt, RemediationPolicy
from remediation.policies import default_remediation_policy


class RemediationEngine:
    def __init__(self, policy: Optional[RemediationPolicy] = None) -> None:
        self.policy = policy or default_remediation_policy()

    def detect_and_remediate(
        self,
        telemetry_snapshot: Dict[str, Any],
        *,
        runtime_compliance_before: Optional[float] = None,
        runtime_compliance_after: Optional[float] = None,
    ) -> Tuple[Dict[str, Any], List[RemediationAttempt]]:
        """Returns (possibly simulated snapshot, remediation attempts)."""
        snap = dict(telemetry_snapshot or {})
        attempts: List[RemediationAttempt] = []
        delta = None
        if runtime_compliance_before is not None and runtime_compliance_after is not None:
            delta = round((runtime_compliance_after - runtime_compliance_before) * 100.0, 2)

        for rule in self.policy.rules:
            if not rule.condition.evaluate(snap):
                continue
            sim_result = rule.action.run_simulation(snap)
            for domain in ("ran", "transport", "core"):
                if domain in sim_result and isinstance(sim_result[domain], dict):
                    snap[domain] = {**(snap.get(domain) or {}), **sim_result[domain]}
            attempts.append(
                RemediationAttempt(
                    detected=rule.rule_id,
                    action=rule.action.name,
                    domain=rule.action.domain,
                    result="success",
                    simulation=True,
                    revalidation_delta_compliance=delta,
                    evidence={
                        "policy_id": self.policy.policy_id,
                        "mode": self.policy.mode,
                        "rollback": rule.rollback.describe(),
                    },
                )
            )
            break  # one action per cycle in simulation

        return snap, attempts
