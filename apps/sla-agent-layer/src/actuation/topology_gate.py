"""ONOS topology readiness gate for ACT-TN-002 LIVE."""
from __future__ import annotations

from typing import Tuple

from actuation.onos_get import onos_get

TOPOLOGY_NOT_READY = "TOPOLOGY_NOT_READY"


def topology_counts() -> dict:
    """Read devices, links, hosts counts (GET-only)."""
    result: dict = {"devices": 0, "links": 0, "hosts": 0, "errors": {}}
    for ep, key, list_key in (
        ("/onos/v1/devices", "devices", "devices"),
        ("/onos/v1/links", "links", "links"),
        ("/onos/v1/hosts", "hosts", "hosts"),
    ):
        data, err = onos_get(ep)
        if err:
            result["errors"][key] = err
            continue
        if isinstance(data, dict):
            items = data.get(list_key) or data.get(key)
            result[key] = len(items) if isinstance(items, list) else 0
        elif isinstance(data, list):
            result[key] = len(data)
    return result


def is_topology_ready(counts: dict | None = None) -> Tuple[bool, dict]:
    """
    Require devices > 0, links > 0, hosts > 0.
    Returns (ready, snapshot).
    """
    snap = counts if counts is not None else topology_counts()
    ready = snap.get("devices", 0) > 0 and snap.get("links", 0) > 0 and snap.get("hosts", 0) > 0
    snap["ready"] = ready
    snap["gate"] = TOPOLOGY_NOT_READY if not ready else "TOPOLOGY_READY"
    return ready, snap
