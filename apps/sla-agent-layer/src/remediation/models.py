"""Remediation policy data model."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class Condition:
    metric: str
    operator: str  # gte, lte, eq
    threshold: float
    domain: str = "ran"

    def evaluate(self, snapshot: Dict[str, Any]) -> bool:
        block = snapshot.get(self.domain) if isinstance(snapshot.get(self.domain), dict) else {}
        val = block.get(self.metric.split(".")[-1])
        if val is None and "." in self.metric:
            val = block.get(self.metric.split(".", 1)[-1])
        try:
            obs = float(val)
        except (TypeError, ValueError):
            return False
        thr = self.threshold
        if self.metric == "prb_utilization" and obs <= 1.0 and thr > 1.0:
            obs = obs * 100.0
        if self.operator == "gte":
            return obs >= thr
        if self.operator == "lte":
            return obs <= self.threshold
        return obs == self.threshold


@dataclass
class Action:
    name: str
    domain: str
    description: str
    simulate: Callable[[Dict[str, Any]], Dict[str, Any]]

    def run_simulation(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        return self.simulate(snapshot)


@dataclass
class Verification:
    metric: str
    domain: str
    expected_improvement_min: float = 0.0

    def check(self, before: float, after: float) -> bool:
        return (after - before) >= self.expected_improvement_min


@dataclass
class Rollback:
    enabled: bool = True
    note: str = "Simulation only — no runtime mutation"

    def describe(self) -> Dict[str, Any]:
        return {"enabled": self.enabled, "note": self.note}


@dataclass
class Rule:
    rule_id: str
    condition: Condition
    action: Action
    verification: Verification
    rollback: Rollback = field(default_factory=Rollback)


@dataclass
class RemediationPolicy:
    policy_id: str
    rules: List[Rule]
    mode: str = "simulation"


@dataclass
class RemediationAttempt:
    detected: str
    action: str
    domain: str
    result: str
    simulation: bool
    revalidation_delta_compliance: Optional[float] = None
    evidence: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "detected": self.detected,
            "action": self.action,
            "domain": self.domain,
            "result": self.result,
            "simulation": self.simulation,
            "revalidation_delta_compliance": self.revalidation_delta_compliance,
            "evidence": self.evidence,
        }
