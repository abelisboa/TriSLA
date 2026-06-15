"""ACT-TN-002 ONOS intent dry-run — payload generation and validation (no ONOS mutation)."""
from __future__ import annotations

from typing import Any, Dict, Optional, Tuple
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator

ACT_TN_002 = "ACT-TN-002"
ACTION_DOMAIN_TRANSPORT = "TRANSPORT"
DRY_RUN_MODE = "synthetic_no_post"


class OnosIntentDryRunPayload(BaseModel):
    """Synthetic ONOS intent payload — persisted only, never POSTed."""

    intent_type: str = "PointToPointIntent"
    src: str
    dst: str
    constraints: Dict[str, Any] = Field(default_factory=lambda: {"durable": True, "lab_only": True})
    bandwidth: str = "1Gbps"
    priority: int = 100
    app_id: str = "trisla-w2b-dryrun"
    dry_run: bool = True

    @field_validator("intent_type")
    @classmethod
    def validate_intent_type(cls, v: str) -> str:
        allowed = {"PointToPointIntent", "PathIntent", "HostIntent"}
        if v not in allowed:
            raise ValueError(f"intent_type must be one of {allowed}")
        return v

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: int) -> int:
        if not 0 <= v <= 65535:
            raise ValueError("priority must be 0-65535")
        return v

    def to_onos_shape(self) -> Dict[str, Any]:
        """ONOS-compatible JSON shape for audit (not submitted)."""
        return {
            "type": self.intent_type,
            "appId": self.app_id,
            "priority": self.priority,
            "selector": {
                "criteria": [
                    {"type": "ETH_SRC", "match": self.src},
                    {"type": "ETH_DST", "match": self.dst},
                ]
            },
            "treatment": {
                "instructions": [{"type": "L2MODIFICATION", "subtype": "ETH_SRC", "mac": self.src}]
            },
            "constraints": [self.constraints],
            "resource": self.bandwidth,
            "dryRun": self.dry_run,
            "trisla": {
                "mode": DRY_RUN_MODE,
                "onos_post_forbidden": True,
            },
        }


def build_dryrun_payload(
    intent_id: str,
    nsi_id: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> OnosIntentDryRunPayload:
    meta = metadata or {}
    lab_src = meta.get("src") or f"lab-src-{nsi_id[:8]}"
    lab_dst = meta.get("dst") or f"lab-dst-{intent_id[:8]}"
    return OnosIntentDryRunPayload(
        intent_type=meta.get("intent_type", "PointToPointIntent"),
        src=str(lab_src),
        dst=str(lab_dst),
        constraints=meta.get("constraints") or {"durable": True, "lab_only": True, "nsi_id": nsi_id},
        bandwidth=str(meta.get("bandwidth", "1Gbps")),
        priority=int(meta.get("priority", 100)),
        app_id=str(meta.get("app_id", "trisla-w2b-dryrun")),
        dry_run=True,
    )


def validate_payload(payload: OnosIntentDryRunPayload) -> Tuple[bool, str]:
    """Schema validation only — no network call."""
    if not payload.src or not payload.dst:
        return False, "src and dst required"
    if payload.src == payload.dst:
        return False, "src and dst must differ"
    if not payload.dry_run:
        return False, "dry_run must be true for W2B"
    shape = payload.to_onos_shape()
    if shape.get("type") != payload.intent_type:
        return False, "type mismatch in onos shape"
    return True, "valid"


def build_rollback_metadata(payload: OnosIntentDryRunPayload) -> Dict[str, Any]:
    """Rollback metadata — no DELETE sent to ONOS."""
    return {
        "rollback_mode": "metadata_only",
        "onos_delete_forbidden": True,
        "would_withdraw_intent_id": f"dryrun-{uuid4()}",
        "payload_snapshot": payload.model_dump(),
        "onos_mutation": False,
    }
