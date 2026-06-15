"""
PROMPT_116 — RAN load proxy from observable dataplane (UE pod + UPF), not srsenb/EmPOWER.

Exports trisla_ran_prb_utilization for TriSLA pipeline compatibility. Semantics: utilization
of a configurable throughput cap on cAdvisor pod network(bytes/s → bps), not 3GPP PRB%.
"""

from __future__ import annotations

import os
import time
from typing import Any

import requests
from flask import Flask, Response

app = Flask(__name__)

PROMETHEUS_URL = (os.environ.get("PROMETHEUS_URL") or "").rstrip("/")
NAMESPACE = (os.environ.get("RAN_PROXY_NAMESPACE") or "ns-1274485").strip()
UPF_POD_RE = (os.environ.get("RAN_PROXY_UPF_POD_REGEX") or "upf.*").strip()
UE_POD_RE = (os.environ.get("RAN_PROXY_UE_POD_REGEX") or "rantester.*").strip()
N6_PEER_POD = (os.environ.get("RAN_PROXY_N6_PEER_POD") or "dnn-n6-iperf-peer").strip()
N6_INTERFACE = (os.environ.get("RAN_PROXY_N6_INTERFACE") or "net1").strip()
RATE_WINDOW = (os.environ.get("RAN_PROXY_RATE_WINDOW") or "2m").strip()
# Bits per second at which trisla_ran_prb_utilization reaches 100 (tune to your link UE→UPF).
MAX_THROUGHPUT_BPS = float(os.environ.get("RAN_PROXY_MAX_THROUGHPUT_BPS") or "100000000")
# Optional: add up to this many percentage points when UE pod(s) are Running (0 = disabled).
UE_RUNNING_BONUS_CAP = float(os.environ.get("RAN_PROXY_UE_RUNNING_BONUS_CAP") or "0")
BONUS_PER_UE = float(os.environ.get("RAN_PROXY_BONUS_PER_RUNNING_UE") or "5")
REQUEST_TIMEOUT = float(os.environ.get("RAN_PROXY_PROM_TIMEOUT") or "10")

_STATE: dict[str, Any] = {
    "throughput_bps": 0.0,
    "util": 0.0,
    "running_ues": 0.0,
    "ok": 0.0,
}


def _instant(query: str) -> float | None:
    if not PROMETHEUS_URL:
        return None
    try:
        r = requests.get(
            f"{PROMETHEUS_URL}/api/v1/query",
            params={"query": query},
            timeout=REQUEST_TIMEOUT,
        )
        r.raise_for_status()
        payload = r.json()
        if payload.get("status") != "success":
            return None
        res = (payload.get("data") or {}).get("result") or []
        if not res:
            return None
        val = res[0].get("value")
        if not isinstance(val, list) or len(val) < 2:
            return None
        return float(val[1])
    except (requests.RequestException, ValueError, TypeError, KeyError):
        return None


def _throughput_bps() -> float | None:
    # Observability anchor: N6 peer net1 RX (validated UE→UPF→N6 causal path).
    q = (
        f'rate(container_network_receive_bytes_total{{namespace="{NAMESPACE}",pod="{N6_PEER_POD}",'
        f'interface="{N6_INTERFACE}"}}[{RATE_WINDOW}]) * 8'
    )
    return _instant(q)


def _running_ue_pods() -> float | None:
    q = (
        "sum(kube_pod_status_phase{"
        f'namespace="{NAMESPACE}",pod=~"{UE_POD_RE}",phase="Running"'
        "})"
    )
    return _instant(q)


def _ran_latency_ms(util: float) -> float:
    """
    Canonical `trisla_ran_latency_ms` for TriSLA telemetry (PromQL SSOT: avg(trisla_ran_latency_ms)).
    Prefer the same transport TCP probe RTT (ms) already used cluster-wide when Prometheus answers;
    otherwise a conservative first-order proxy from the RAN load proxy utilization.
    """
    if PROMETHEUS_URL:
        q = (
            'max(probe_duration_seconds{job="probe/monitoring/trisla-transport-tcp-probe"}) * 1000'
        )
        v = _instant(q)
        if v is not None and v > 0:
            return max(1.0, min(10000.0, float(v)))
    u = max(0.0, min(100.0, float(util)))
    return max(1.0, min(500.0, 2.0 + u * 1.25))


def _compute() -> tuple[float, float, float, float]:
    ok = 1.0
    bps = _throughput_bps()
    if bps is None:
        ok = 0.0
        bps = float(_STATE.get("throughput_bps") or 0.0)
    cap = max(MAX_THROUGHPUT_BPS, 1.0)
    util_line = max(0.0, min(100.0, 100.0 * bps / cap))

    ues = _running_ue_pods()
    if ues is None:
        ok = 0.0
        ues = float(_STATE.get("running_ues") or 0.0)

    bonus = 0.0
    if UE_RUNNING_BONUS_CAP > 0 and ues > 0:
        bonus = min(UE_RUNNING_BONUS_CAP, ues * BONUS_PER_UE)
    util = max(0.0, min(100.0, util_line + bonus))

    _STATE["throughput_bps"] = bps
    _STATE["util"] = util
    _STATE["running_ues"] = ues
    _STATE["ok"] = ok
    return bps, util, ues, ok


@app.route("/metrics")
def metrics() -> Response:
    bps, util, ues, ok = _compute()
    lat_ms = _ran_latency_ms(util)
    body = "\n".join(
        [
            "# HELP trisla_ran_prb_utilization Dataplane load proxy (0–100): N6 peer throughput vs RAN_PROXY_MAX_THROUGHPUT_BPS; not 3GPP PRB.",
            "# TYPE trisla_ran_prb_utilization gauge",
            f"trisla_ran_prb_utilization {util:.6f}",
            "# HELP trisla_ran_latency_ms Canonical TriSLA RAN latency (ms); transport-probe RTT when available else utilization-derived proxy.",
            "# TYPE trisla_ran_latency_ms gauge",
            f"trisla_ran_latency_ms {lat_ms:.6f}",
            "# HELP trisla_ran_ue_proxy_throughput_bps N6 peer net1 RX rate * 8 from cAdvisor (observability anchor).",
            "# TYPE trisla_ran_ue_proxy_throughput_bps gauge",
            f"trisla_ran_ue_proxy_throughput_bps {bps:.6f}",
            "# HELP trisla_ran_ue_proxy_running_ue_pods kube_pod_status_phase Running count for RAN_PROXY_UE_POD_REGEX.",
            "# TYPE trisla_ran_ue_proxy_running_ue_pods gauge",
            f"trisla_ran_ue_proxy_running_ue_pods {ues:.6f}",
            "# HELP trisla_ran_ue_proxy_exporter_ok 1 if Prometheus queries succeeded this scrape.",
            "# TYPE trisla_ran_ue_proxy_exporter_ok gauge",
            f"trisla_ran_ue_proxy_exporter_ok {ok:.6f}",
            "# HELP trisla_ran_ue_proxy_last_eval_unixtime Time of last evaluation.",
            "# TYPE trisla_ran_ue_proxy_last_eval_unixtime gauge",
            f"trisla_ran_ue_proxy_last_eval_unixtime {int(time.time())}",
        ]
    ) + "\n"
    return Response(body, mimetype="text/plain; version=0.0.4; charset=utf-8")


@app.route("/healthz")
@app.route("/health")
def healthz() -> Response:
    return Response("ok\n", mimetype="text/plain")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "9102")))
