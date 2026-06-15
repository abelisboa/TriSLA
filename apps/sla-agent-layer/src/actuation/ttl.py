"""TTL configuration and expiration helpers for actuation scaffold."""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import NamedTuple


class TTLConfig(NamedTuple):
    request_expiration: int
    authorization_timeout: int
    execution_timeout: int


def get_ttl_config() -> TTLConfig:
    return TTLConfig(
        request_expiration=int(os.getenv("ACTUATION_REQUEST_TTL_SECONDS", "300")),
        authorization_timeout=int(os.getenv("ACTUATION_AUTHORIZATION_TIMEOUT_SECONDS", "300")),
        execution_timeout=int(os.getenv("ACTUATION_EXECUTION_TIMEOUT_SECONDS", "120")),
    )


def _age_seconds(since: datetime, now: datetime | None = None) -> float:
    ref = now or datetime.now(timezone.utc)
    if since.tzinfo is None:
        since = since.replace(tzinfo=timezone.utc)
    return (ref - since).total_seconds()


def is_authorization_expired(created_at: datetime, cfg: TTLConfig | None = None) -> bool:
    cfg = cfg or get_ttl_config()
    return _age_seconds(created_at) > cfg.authorization_timeout


def is_request_expired(created_at: datetime, cfg: TTLConfig | None = None) -> bool:
    cfg = cfg or get_ttl_config()
    return _age_seconds(created_at) > cfg.request_expiration


def is_execution_expired(executing_at: datetime, cfg: TTLConfig | None = None) -> bool:
    cfg = cfg or get_ttl_config()
    return _age_seconds(executing_at) > cfg.execution_timeout
