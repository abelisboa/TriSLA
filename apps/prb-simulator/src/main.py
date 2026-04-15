import os
import random
import threading
import time
from typing import Dict, Tuple

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from prometheus_client import CONTENT_TYPE_LATEST, Gauge, generate_latest
from starlette.responses import Response


app = FastAPI(title="TriSLA PRB Simulator", version="1.0.0")

# Gauge principal consumido pelo pipeline atual.
PRB_UTILIZATION = Gauge(
    "trisla_ran_prb_utilization",
    "Simulated RAN PRB utilization based on scenario load (percent 0-100)",
)
PRB_SCENARIO = Gauge(
    "trisla_ran_prb_scenario",
    "Current PRB scenario encoded as 1, 10 or 50",
)
TRANSPORT_JITTER = Gauge(
    "trisla_transport_jitter_ms",
    "Simulated transport jitter in milliseconds (derived from RTT variation and load)",
)
RAN_LATENCY_MS = Gauge(
    "trisla_ran_latency_ms",
    "RAN air-interface latency (ms) derived from scenario load and PRB (simulator observability)",
)


SCENARIO_RANGES: Dict[str, Tuple[float, float]] = {
    "scenario_1": (10.0, 25.0),
    "scenario_10": (30.0, 60.0),
    "scenario_50": (70.0, 95.0),
}
SCENARIO_LEVEL = {"scenario_1": 1, "scenario_10": 10, "scenario_50": 50}

_current_scenario = os.getenv("PRB_SCENARIO", "scenario_1")
if _current_scenario not in SCENARIO_RANGES:
    _current_scenario = "scenario_1"
_latest_prb = 0.0
_latest_jitter = 0.1
_latest_ran_latency_ms = 1.0
_manual_prb_override: float | None = None
_load_inputs = {
    "active_slices": 0.0,
    "request_rate": 0.0,
    "concurrency": 0.0,
}
_lock = threading.Lock()


class PRBSetRequest(BaseModel):
    value: float = Field(..., ge=0.0, le=100.0)


class LoadInputRequest(BaseModel):
    active_slices: float = Field(0.0, ge=0.0)
    request_rate: float = Field(0.0, ge=0.0)
    concurrency: float = Field(0.0, ge=0.0)


def _next_prb_value(scenario: str) -> float:
    low, high = SCENARIO_RANGES[scenario]
    with _lock:
        manual_value = _manual_prb_override
        active_slices = _load_inputs["active_slices"]
        request_rate = _load_inputs["request_rate"]
        concurrency = _load_inputs["concurrency"]

    if manual_value is not None:
        global _latest_prb
        _latest_prb = round(max(0.0, min(100.0, manual_value)), 4)
        return _latest_prb

    # Base do cenário + acoplamento causal (carga real) + ruído.
    # PRB = base + f(active_slices, request_rate, concurrency) + jitter
    base = random.uniform(low, high)
    load_boost = (
        (active_slices * 0.7)
        + (request_rate * 0.10)
        + (concurrency * 0.90)
    )
    candidate = base + load_boost + random.uniform(-1.5, 1.5)

    # Smoothing leve para parecer comportamento de carga real.
    if _latest_prb > 0:
        candidate = (0.65 * _latest_prb) + (0.35 * candidate)
    candidate = max(0.0, min(100.0, candidate))
    _latest_prb = round(candidate, 4)
    return _latest_prb


def _next_jitter_value(scenario: str, prb_value: float) -> float:
    """
    Jitter (ms) coerente com carga e RTT de referência (4-6ms):
    - cenário baixo: jitter tende ao piso
    - cenário alto: jitter cresce e pode se aproximar de 2ms
    """
    bounds = {
        "scenario_1": (0.1, 0.6),
        "scenario_10": (0.4, 1.3),
        "scenario_50": (1.0, 2.0),
    }
    low, high = bounds[scenario]
    load_factor = max(0.0, min(1.0, prb_value / 100.0))
    base = low + (high - low) * load_factor
    noisy = base + random.uniform(-0.15, 0.15)

    global _latest_jitter
    if _latest_jitter > 0:
        noisy = (0.7 * _latest_jitter) + (0.3 * noisy)
    noisy = max(low, min(high, noisy))
    _latest_jitter = round(noisy, 4)
    return _latest_jitter


def _next_ran_latency_ms(scenario: str, prb_value: float) -> float:
    """Latência RAN (ms) coerente com carga: sobe com PRB no cenário (exportada ao Prometheus)."""
    global _latest_ran_latency_ms
    base_by_scenario = {"scenario_1": 2.0, "scenario_10": 5.0, "scenario_50": 8.0}
    base = base_by_scenario.get(scenario, 3.0)
    load = max(0.0, min(1.0, prb_value / 100.0))
    target = base + load * 6.0 + random.uniform(-0.2, 0.2)
    if _latest_ran_latency_ms > 0:
        target = 0.72 * _latest_ran_latency_ms + 0.28 * target
    _latest_ran_latency_ms = round(max(0.5, min(25.0, target)), 4)
    return _latest_ran_latency_ms


def _update_loop() -> None:
    while True:
        scenario = _current_scenario
        prb_value = _next_prb_value(scenario)
        jitter_value = _next_jitter_value(scenario, prb_value)
        lat_ms = _next_ran_latency_ms(scenario, prb_value)
        PRB_UTILIZATION.set(prb_value)
        PRB_SCENARIO.set(SCENARIO_LEVEL[scenario])
        TRANSPORT_JITTER.set(jitter_value)
        RAN_LATENCY_MS.set(lat_ms)
        time.sleep(1)


@app.on_event("startup")
async def startup_event() -> None:
    worker = threading.Thread(target=_update_loop, daemon=True, name="prb-simulator-loop")
    worker.start()


@app.get("/health")
async def health() -> Dict[str, object]:
    with _lock:
        load_inputs = dict(_load_inputs)
        manual_override = _manual_prb_override
    return {
        "status": "ok",
        "scenario": _current_scenario,
        "prb_utilization": _latest_prb,
        "ran_latency_ms": _latest_ran_latency_ms,
        "transport_jitter_ms": _latest_jitter,
        "manual_prb_override": manual_override,
        "load_inputs": load_inputs,
    }


@app.post("/scenario/{scenario_name}")
async def set_scenario(scenario_name: str) -> Dict[str, str]:
    if scenario_name not in SCENARIO_RANGES:
        raise HTTPException(status_code=400, detail="scenario must be one of: scenario_1, scenario_10, scenario_50")
    global _current_scenario
    _current_scenario = scenario_name
    return {"status": "ok", "scenario": _current_scenario}


@app.post("/set")
async def set_prb(payload: PRBSetRequest) -> Dict[str, object]:
    """Override manual para campanha controlada (sem alterar arquitetura)."""
    with _lock:
        global _manual_prb_override
        _manual_prb_override = float(payload.value)
    return {"status": "ok", "manual_prb_override": _manual_prb_override}


@app.post("/set/auto")
async def set_prb_auto() -> Dict[str, object]:
    with _lock:
        global _manual_prb_override
        _manual_prb_override = None
    return {"status": "ok", "manual_prb_override": None}


@app.post("/load")
async def set_load_inputs(payload: LoadInputRequest) -> Dict[str, object]:
    """Acoplamento causal: alimenta o simulador com sinais de carga."""
    with _lock:
        _load_inputs["active_slices"] = float(payload.active_slices)
        _load_inputs["request_rate"] = float(payload.request_rate)
        _load_inputs["concurrency"] = float(payload.concurrency)
    return {"status": "ok", "load_inputs": dict(_load_inputs)}


@app.get("/metrics")
async def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
