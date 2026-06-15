#!/usr/bin/env python3
"""
PROMPT_RESULTS_MULTIDOMAIN_STRESS_CAMPAIGN_V2
Live multidomain degradation campaign: RAN (PRB via traffic), transport (iperf), core (stress pod).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

REPO = Path(__file__).resolve().parents[2]
BACKEND = os.getenv("TRISLA_BACKEND_URL", "http://192.168.10.15:32002").rstrip("/")
PRB_URL = os.getenv("TRISLA_PRB_URL", "").rstrip("/")
IPERF_SERVER = os.getenv("TRISLA_IPERF_SERVER", "192.168.100.51")
IPERF_NS = os.getenv("TRISLA_IPERF_UE_NAMESPACE", "ueransim")
IPERF_DEPLOY = os.getenv("TRISLA_IPERF_UE_DEPLOY", "deploy/ueransim-singlepod")
IPERF_CONTAINER = os.getenv("TRISLA_IPERF_UE_CONTAINER", "ue")
STRESS_NS = os.getenv("TRISLA_V62_STRESS_NS", "ns-1274485")
PAUSE_S = float(os.getenv("TRISLA_SUBMIT_PAUSE_S", "3.5"))
IPERF_WARMUP_S = float(os.getenv("TRISLA_IPERF_WARMUP_S", "8"))

PROMQL_RAN_PRB = "avg(trisla_ran_prb_utilization{job=\"trisla-ran-ue-upf-proxy\"})"
PROMQL_RTT = 'max(probe_duration_seconds{job="probe/monitoring/trisla-transport-tcp-probe"}) * 1000'
PROMQL_JITTER = (
    '(max_over_time(probe_duration_seconds{job="probe/monitoring/trisla-transport-tcp-probe"}[1m]) - '
    'min_over_time(probe_duration_seconds{job="probe/monitoring/trisla-transport-tcp-probe"}[1m])) * 1000'
)
PROMQL_CORE_CPU = os.getenv("TELEMETRY_PROMQL_CORE_CPU", "sum(rate(process_cpu_seconds_total[1m]))")
PROMQL_CORE_MEM = os.getenv("TELEMETRY_PROMQL_CORE_MEMORY", "sum(process_resident_memory_bytes)")

SLICES = ("URLLC", "eMBB", "mMTC")


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    label: str
    prb_target: Optional[float]  # None = do not tune
    iperf_bitrate: Optional[str]
    core_stress_cpu: int
    core_stress_timeout_s: int


SCENARIOS: Tuple[Scenario, ...] = (
    Scenario("C0", "baseline_healthy", 18.0, None, 0, 0),
    Scenario("C1", "ran_degradation", 52.0, None, 0, 0),
    Scenario("C2", "transport_degradation", 18.0, "90M", 0, 0),
    Scenario("C3", "core_degradation", 18.0, None, 4, 120),
    Scenario("C4", "ran_transport", 52.0, "90M", 0, 0),
    Scenario("C5", "transport_core", 18.0, "90M", 4, 120),
    Scenario("C6", "ran_core", 52.0, None, 4, 120),
    Scenario("C7", "full_multidomain", 52.0, "130M", 4, 120),
)


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def _http_json(method: str, url: str, body: Optional[dict] = None, timeout: float = 180.0) -> Any:
    data = headers = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers = {"Content-Type": "application/json"}
    req = Request(url, data=data, headers=headers or {}, method=method)
    with urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw) if raw else {}


def _prom_scalar(query: str) -> Optional[float]:
    url = f"{BACKEND}/api/v1/prometheus/query?" + urlencode({"query": query})
    try:
        data = _http_json("GET", url, timeout=25.0)
        res = ((data or {}).get("data") or {}).get("result") or []
        if not res:
            return None
        return float(res[0]["value"][1])
    except (TypeError, ValueError, IndexError, KeyError, OSError):
        return None


def _prom_before() -> Dict[str, Optional[float]]:
    return {
        "ran_prb": _prom_scalar(PROMQL_RAN_PRB),
        "transport_rtt": _prom_scalar(PROMQL_RTT),
        "transport_jitter": _prom_scalar(PROMQL_JITTER),
        "core_cpu": _prom_scalar(PROMQL_CORE_CPU),
        "core_memory": _prom_scalar(PROMQL_CORE_MEM),
    }


def _set_prb_target(target_pct: float) -> bool:
    if not PRB_URL:
        return False
    try:
        jobs_url = f"{BACKEND}/api/v1/prometheus/query?" + urlencode({"query": "trisla_ran_prb_utilization"})
        data = _http_json("GET", jobs_url, timeout=20.0)
        proxy = 0.0
        for item in ((data or {}).get("data") or {}).get("result") or []:
            if (item.get("metric") or {}).get("job") == "trisla-ran-ue-upf-proxy":
                proxy = float(item["value"][1])
        raw_sim = max(0.0, min(100.0, (2.0 * target_pct) - proxy))
        _http_json("POST", f"{PRB_URL}/set", {"value": round(raw_sim, 4)}, timeout=30.0)
        time.sleep(2.5)
        return True
    except (OSError, ValueError, TypeError, HTTPError, URLError):
        return False


def _start_iperf(bitrate: str, duration_s: int) -> subprocess.Popen:
    return subprocess.Popen(
        [
            "kubectl", "-n", IPERF_NS, "exec", IPERF_DEPLOY, "-c", IPERF_CONTAINER, "--",
            "iperf3", "-c", IPERF_SERVER, "-u", "-b", bitrate, "-t", str(duration_s),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _start_core_stress(cpu: int, timeout_s: int) -> str:
    name = f"mdstress-{uuid.uuid4().hex[:8]}"
    subprocess.run(
        [
            "kubectl", "-n", STRESS_NS, "run", name, "--restart=Never",
            "--image=polinux/stress", "--", "stress", f"--cpu={cpu}", f"--timeout={timeout_s}s",
        ],
        check=False,
        capture_output=True,
    )
    for _ in range(20):
        time.sleep(2)
        r = subprocess.run(
            ["kubectl", "-n", STRESS_NS, "get", "pod", name, "-o", "jsonpath={.status.phase}"],
            capture_output=True, text=True,
        )
        if (r.stdout or "").strip() == "Running":
            break
    return name


def _del_stress(name: str) -> None:
    if name:
        subprocess.run(["kubectl", "-n", STRESS_NS, "delete", "pod", name, "--wait=false"], capture_output=True)


def _slice_body(slice_type: str, scenario_id: str, rep: int) -> dict:
    templates = {
        "URLLC": ("urllc-template-001", {"type": "URLLC", "latency": "1ms", "reliability": 0.99999, "throughput": "100Mbps"}),
        "eMBB": ("embb-template-001", {"type": "eMBB", "latency": "20ms", "reliability": 0.99, "throughput": "500Mbps"}),
        "mMTC": ("mmtc-template-001", {"type": "mMTC", "latency": "100ms", "reliability": 0.95, "throughput": "10Mbps"}),
    }
    tid, fv = templates[slice_type]
    return {
        "template_id": tid,
        "tenant_id": f"mdstress-v2-{scenario_id}-{slice_type.lower()}-{rep}",
        "form_values": {**fv, "scenario": f"multidomain_{scenario_id}", "notes": f"{scenario_id}_{slice_type}_r{rep}"},
    }


def _safe_float(v: Any) -> Optional[float]:
    try:
        return float(v) if v is not None else None
    except (TypeError, ValueError):
        return None


def _extract_row(
    scenario: Scenario,
    slice_type: str,
    rep: int,
    before: Dict[str, Optional[float]],
    payload: dict,
    http_elapsed: float,
    controls: dict,
) -> dict:
    md = payload.get("metadata") or {}
    snap = md.get("telemetry_snapshot") or {}
    ran, tr, co = snap.get("ran") or {}, snap.get("transport") or {}, snap.get("core") or {}
    sla = md.get("sla_metrics") or {}
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "scenario_id": scenario.scenario_id,
        "scenario_label": scenario.label,
        "slice_type": slice_type,
        "rep": rep,
        "decision": str(payload.get("decision") or ""),
        "decision_score": _safe_float(md.get("decision_score")),
        "confidence": _safe_float(payload.get("confidence")),
        "decision_source": md.get("decision_source"),
        "reason_codes": json.dumps(md.get("reason_codes") or []),
        "telemetry_snapshot_present": bool(snap),
        "prb_utilization": _safe_float(ran.get("prb_utilization")),
        "transport_rtt_ms": _safe_float(tr.get("rtt_ms", tr.get("rtt"))),
        "transport_jitter_ms": _safe_float(tr.get("jitter_ms", tr.get("jitter"))),
        "packet_loss": _safe_float(tr.get("packet_loss", tr.get("loss"))),
        "core_cpu": _safe_float(co.get("cpu_utilization", co.get("cpu"))),
        "core_memory": _safe_float(co.get("memory_utilization", co.get("memory"))),
        "ml_risk_score": _safe_float(md.get("ml_risk_score")),
        "feasibility_score": _safe_float(sla.get("feasibility_score")),
        "resource_pressure": _safe_float(sla.get("resource_pressure")),
        "bc_status": str(payload.get("bc_status") or ""),
        "tx_hash": str(md.get("tx_hash") or payload.get("tx_hash") or ""),
        "sla_agent_status": str(payload.get("sla_agent_status") or ""),
        "intent_id": payload.get("intent_id"),
        "execution_id": md.get("execution_id"),
        "http_elapsed_s": http_elapsed,
        "prb_before": before.get("ran_prb"),
        "rtt_before": before.get("transport_rtt"),
        "jitter_before": before.get("transport_jitter"),
        "core_cpu_before": before.get("core_cpu"),
        "iperf_bitrate": controls.get("iperf_bitrate"),
        "core_stress": controls.get("core_stress"),
        "prb_control_applied": controls.get("prb_control_applied"),
    }


def run_campaign(out: Path, reps: int, scenarios: List[Scenario], skip_revalidate: bool) -> pd.DataFrame:
    raw_dir = out / "dataset" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    jsonl = out / "dataset" / "raw" / "all_submits.jsonl"
    jsonl.write_text("", encoding="utf-8")
    commands_log = out / "analysis" / "commands_executed.txt"
    commands_log.parent.mkdir(parents=True, exist_ok=True)
    commands_log.write_text(f"# Multidomain stress V2 — {_utc()}\nBACKEND={BACKEND}\nPRB_URL={PRB_URL or 'unset'}\n", encoding="utf-8")

    rows: List[dict] = []
    total = len(scenarios) * len(SLICES) * reps
    n_done = 0
    active_iperf: Optional[subprocess.Popen] = None
    active_stress: str = ""

    try:
        for sc in scenarios:
            for sl in SLICES:
                for rep in range(reps):
                    n_done += 1
                    controls = {
                        "iperf_bitrate": sc.iperf_bitrate,
                        "core_stress": sc.core_stress_cpu > 0,
                        "prb_control_applied": False,
                    }
                    if active_stress:
                        _del_stress(active_stress)
                        active_stress = ""
                    if sc.core_stress_cpu > 0:
                        active_stress = _start_core_stress(sc.core_stress_cpu, sc.core_stress_timeout_s)
                        time.sleep(5)

                    iperf_proc = None
                    if sc.iperf_bitrate:
                        dur = int(PAUSE_S * 3 + 90)
                        iperf_proc = _start_iperf(sc.iperf_bitrate, dur)
                        active_iperf = iperf_proc
                        time.sleep(IPERF_WARMUP_S)

                    if sc.prb_target is not None:
                        controls["prb_control_applied"] = _set_prb_target(sc.prb_target)

                    before = _prom_before()
                    body = _slice_body(sl, sc.scenario_id, rep)
                    t0 = time.perf_counter()
                    try:
                        payload = _http_json("POST", f"{BACKEND}/api/v1/sla/submit", body, timeout=180.0)
                        err = None
                    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as e:
                        payload = {}
                        err = str(e)
                    elapsed = time.perf_counter() - t0

                    row = _extract_row(sc, sl, rep, before, payload, elapsed, controls)
                    row["submit_error"] = err
                    snap = (payload.get("metadata") or {}).get("telemetry_snapshot") if payload else None
                    if not skip_revalidate and payload.get("intent_id") and snap:
                        try:
                            rev = _http_json(
                                "POST",
                                f"{BACKEND}/api/v1/sla/revalidate-telemetry",
                                {"intent_id": payload["intent_id"], "reference_telemetry_snapshot": snap},
                                timeout=60.0,
                            )
                            row["revalidate_status"] = rev.get("status")
                            row["drift_compared"] = (rev.get("drift_summary") or {}).get("compared")
                        except (OSError, HTTPError, URLError):
                            row["revalidate_status"] = "error"
                            row["drift_compared"] = None
                    rows.append(row)
                    with jsonl.open("a", encoding="utf-8") as f:
                        f.write(json.dumps({"row": row, "payload": payload}, ensure_ascii=False) + "\n")
                    print(f"[{n_done}/{total}] {sc.scenario_id} {sl} r{rep} -> {row.get('decision')} score={row.get('decision_score')}")

                    if iperf_proc and rep == reps - 1 and sl == SLICES[-1]:
                        try:
                            iperf_proc.wait(timeout=30)
                        except subprocess.TimeoutExpired:
                            iperf_proc.kill()
                        active_iperf = None
                    time.sleep(PAUSE_S)
    finally:
        if active_stress:
            _del_stress(active_stress)
        if active_iperf:
            try:
                active_iperf.kill()
            except OSError:
                pass

    df = pd.DataFrame(rows)
    csv_path = out / "dataset" / "multidomain_stress_final.csv"
    df.to_csv(csv_path, index=False)
    return df


def _save_fig(fig: plt.Figure, base: Path) -> None:
    base.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(base.with_suffix(".png"), dpi=300, bbox_inches="tight", facecolor="white")
    fig.savefig(base.with_suffix(".svg"), bbox_inches="tight", facecolor="white")
    plt.close(fig)


def generate_figures(df: pd.DataFrame, fig_dir: Path) -> None:
    sm = df[df["decision_source"].astype(str) == "decision_score_mode"].copy()
    if sm.empty:
        sm = df.copy()

    # R1
    sub = sm.dropna(subset=["prb_utilization", "decision_score"])
    if len(sub) >= 3:
        fig, ax = plt.subplots(figsize=(6.5, 4))
        ax.scatter(sub["prb_utilization"], sub["decision_score"], alpha=0.6, s=30)
        r, _ = stats.pearsonr(sub["prb_utilization"], sub["decision_score"])
        z = np.polyfit(sub["prb_utilization"], sub["decision_score"], 1)
        xs = np.linspace(sub["prb_utilization"].min(), sub["prb_utilization"].max(), 50)
        ax.plot(xs, np.poly1d(z)(xs), "r--", label=f"r={r:.3f}")
        ax.set_xlabel("RAN PRB (%)")
        ax.set_ylabel("Decision score")
        ax.set_title("R1 — Score vs PRB")
        ax.legend()
        _save_fig(fig, fig_dir / "R1_score_vs_prb")

    # R2 transport panel
    fig, axes = plt.subplots(1, 3, figsize=(10, 3.5))
    for ax, col, title in zip(
        axes,
        ["transport_rtt_ms", "transport_jitter_ms", "packet_loss"],
        ["RTT (ms)", "Jitter (ms)", "Packet loss"],
    ):
        s = sm.dropna(subset=[col, "decision_score"])
        if len(s) >= 3 and col in s.columns:
            ax.scatter(s[col], s["decision_score"], alpha=0.5, s=20)
            ax.set_xlabel(title)
            ax.set_ylabel("Score")
    fig.suptitle("R2 — Score vs transport metrics")
    _save_fig(fig, fig_dir / "R2_score_vs_transport")

    # R3 core
    fig, ax = plt.subplots(figsize=(6.5, 4))
    s = sm.dropna(subset=["core_cpu", "decision_score"])
    if len(s) >= 3:
        ax.scatter(s["core_cpu"], s["decision_score"], alpha=0.6)
        ax.set_xlabel("Core CPU (Prometheus aggregate)")
        ax.set_ylabel("Decision score")
        ax.set_title("R3 — Score vs core pressure")
    _save_fig(fig, fig_dir / "R3_score_vs_core")

    # R4 scenario boxplot
    fig, ax = plt.subplots(figsize=(8, 4))
    order = [s.scenario_id for s in SCENARIOS]
    data = [sm.loc[sm["scenario_id"] == sid, "decision_score"].dropna().values for sid in order]
    ax.boxplot([d for d in data if len(d)], labels=[o for o, d in zip(order, data) if len(d)], patch_artist=True)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=35, ha="right")
    ax.set_ylabel("Decision score")
    ax.set_title("R4 — Score by scenario C0–C7")
    _save_fig(fig, fig_dir / "R4_scenario_comparison")

    # R5 slice sensitivity
    fig, ax = plt.subplots(figsize=(7, 4))
    slices = list(SLICES)
    data = [sm.loc[sm["slice_type"] == sl, "decision_score"].dropna().values for sl in slices]
    ax.boxplot(data, labels=slices, patch_artist=True)
    ax.set_title("R5 — Slice-aware score distribution")
    _save_fig(fig, fig_dir / "R5_slice_sensitivity")

    # R6 decision distribution
    fig, ax = plt.subplots(figsize=(8, 4))
    ct = pd.crosstab(df["scenario_id"], df["decision"])
    ct = ct.reindex([s.scenario_id for s in SCENARIOS], fill_value=0)
    bottom = np.zeros(len(ct))
    for dec in ["ACCEPT", "RENEGOTIATE", "REJECT"]:
        if dec in ct.columns:
            ax.bar(ct.index, ct[dec], bottom=bottom, label=dec)
            bottom += ct[dec].values
    ax.legend()
    ax.set_title("R6 — Decision mix by scenario")
    plt.xticks(rotation=35, ha="right")
    _save_fig(fig, fig_dir / "R6_decision_distribution")

    # R7 dominance heatmap by scenario
    feats = ["prb_utilization", "transport_rtt_ms", "transport_jitter_ms", "core_cpu", "core_memory"]
    mat = []
    for sid in [s.scenario_id for s in SCENARIOS]:
        block = sm[sm["scenario_id"] == sid]
        row = []
        for f in feats:
            if f not in block.columns:
                row.append(0.0)
                continue
            x = pd.to_numeric(block[f], errors="coerce")
            y = pd.to_numeric(block["decision_score"], errors="coerce")
            m = x.notna() & y.notna()
            row.append(abs(float(x[m].corr(y[m]))) if m.sum() >= 3 else 0.0)
        mat.append(row)
    fig, ax = plt.subplots(figsize=(7, 5))
    im = ax.imshow(mat, aspect="auto", cmap="YlOrRd")
    ax.set_xticks(range(len(feats)), [f.replace("_", "\n") for f in feats], rotation=30, ha="right")
    ax.set_yticks(range(len(SCENARIOS)), [s.scenario_id for s in SCENARIOS])
    fig.colorbar(im, ax=ax, label="|corr(feature, score)|")
    ax.set_title("R7 — Feature influence by scenario")
    _save_fig(fig, fig_dir / "R7_feature_dominance_heatmap")

    # R8 runtime consistency (score vs feasibility)
    if "feasibility_score" in sm.columns:
        fig, ax = plt.subplots(figsize=(6, 4))
        s = sm.dropna(subset=["decision_score", "feasibility_score"])
        ax.scatter(s["decision_score"], s["feasibility_score"], alpha=0.5)
        ax.set_xlabel("Decision score")
        ax.set_ylabel("Feasibility score")
        ax.set_title("R8 — Admission score vs feasibility")
        _save_fig(fig, fig_dir / "R8_runtime_consistency")

    # R9 governance
    fig, ax = plt.subplots(figsize=(6, 4))
    g = df.groupby("scenario_id").agg(
        tx_rate=("tx_hash", lambda s: (s.astype(str).str.len() > 4).mean()),
        committed=("bc_status", lambda s: (s == "COMMITTED").mean()),
    )
    x = np.arange(len(g))
    ax.bar(x - 0.2, g["tx_rate"], width=0.4, label="tx_hash present")
    ax.bar(x + 0.2, g["committed"], width=0.4, label="bc COMMITTED")
    ax.set_xticks(x, g.index, rotation=35, ha="right")
    ax.set_title("R9 — Governance continuity by scenario")
    ax.legend()
    _save_fig(fig, fig_dir / "R9_governance_continuity")


def validate_campaign(df: pd.DataFrame) -> dict:
    sm = df[df["decision_source"].astype(str) == "decision_score_mode"]
    checks: Dict[str, Any] = {}

    def corr(col: str) -> Optional[float]:
        s = sm.dropna(subset=[col, "decision_score"])
        if len(s) < 5:
            return None
        return float(s[col].corr(s["decision_score"]))

    checks["ran_influences_score"] = {
        "corr_prb_score": corr("prb_utilization"),
        "pass": corr("prb_utilization") is not None and abs(corr("prb_utilization") or 0) >= 0.15,
    }
    checks["transport_influences_score"] = {
        "corr_rtt": corr("transport_rtt_ms"),
        "corr_jitter": corr("transport_jitter_ms"),
        "pass": any(
            abs(c or 0) >= 0.1
            for c in (corr("transport_rtt_ms"), corr("transport_jitter_ms"))
        ),
    }
    checks["core_influences_score"] = {
        "corr_cpu": corr("core_cpu"),
        "pass": corr("core_cpu") is not None and abs(corr("core_cpu") or 0) >= 0.05,
    }

    means = sm.groupby("scenario_id")["decision_score"].mean()
    c0 = means.get("C0", np.nan)
    c7 = means.get("C7", np.nan)
    checks["combined_degradation_lower_score"] = {
        "mean_C0": float(c0) if not np.isnan(c0) else None,
        "mean_C7": float(c7) if not np.isnan(c7) else None,
        "pass": not np.isnan(c0) and not np.isnan(c7) and c7 < c0,
    }

    slice_means = sm.groupby("slice_type")["decision_score"].mean().to_dict()
    checks["slice_differentiable"] = {
        "means": slice_means,
        "pass": len(set(round(v, 3) for v in slice_means.values() if v == v)) >= 2,
    }

    checks["telemetry_present"] = {
        "rate": float(df["telemetry_snapshot_present"].mean()),
        "pass": float(df["telemetry_snapshot_present"].mean()) >= 0.95,
    }

    checks["decisions_coherent"] = {
        "distribution": df["decision"].value_counts().to_dict(),
        "pass": df["decision"].nunique() >= 2,
    }

    all_pass = all(v.get("pass") for v in checks.values() if isinstance(v, dict))
    return {"checks": checks, "campaign_approved": all_pass}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=int(os.getenv("TRISLA_MD_STRESS_REPS", "10")))
    ap.add_argument("--out", type=str, default="")
    ap.add_argument("--skip-revalidate", action="store_true")
    ap.add_argument("--figures-only", type=str, default="", help="path to existing csv")
    args = ap.parse_args()

    out = Path(args.out) if args.out else REPO / f"evidencias_multidomain_stress_campaign_v2_{_utc()}"
    out.mkdir(parents=True, exist_ok=True)
    fig_dir = out / "figures"

    if args.figures_only:
        df = pd.read_csv(args.figures_only)
    else:
        print(f"Campaign output: {out}")
        print(f"Planned executions: {len(SCENARIOS) * len(SLICES) * args.reps}")
        df = run_campaign(out, args.reps, list(SCENARIOS), args.skip_revalidate)

    generate_figures(df, fig_dir)
    validation = validate_campaign(df)

    def _json_safe(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {k: _json_safe(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [_json_safe(v) for v in obj]
        if isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        if isinstance(obj, (np.integer, np.floating)):
            return float(obj) if isinstance(obj, np.floating) else int(obj)
        if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
            return None
        return obj

    validation_safe = _json_safe(validation)
    (out / "analysis" / "hypothesis_report.json").write_text(
        json.dumps(
            {
                "central_hypothesis": (
                    "TriSLA determines SLA feasibility using correlated multidomain telemetry "
                    "from RAN, transport, and core domains before orchestration execution."
                ),
                "validation": validation_safe,
                "n_rows": len(df),
                "scenarios": [s.scenario_id for s in SCENARIOS],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    csv_path = out / "dataset" / "multidomain_stress_final.csv"
    report_lines = [
        f"# Multidomain Stress Campaign V2 — Validation Report",
        f"",
        f"**Pack:** `{out.name}`",
        f"**Rows:** {len(df)}",
        f"**Campaign approved:** {validation['campaign_approved']}",
        f"",
        "## Checks",
    ]
    for k, v in validation["checks"].items():
        report_lines.append(f"- **{k}**: pass={v.get('pass')} — {json.dumps({kk: vv for kk, vv in v.items() if kk != 'pass'})}")
    report_lines.append("\n## Scientific conclusion\n")
    if validation["campaign_approved"]:
        report_lines.append(
            "Evidence supports multidomain telemetry correlation influencing SLA feasibility scores "
            "under controlled RAN/transport/core degradation."
        )
    else:
        report_lines.append(
            "Campaign completed with partial validation; see per-check metrics. "
            "Do not claim balanced multidomain scoring or full tri-slice proof without addressing failed checks."
        )
    (out / "analysis" / "validation_report.md").write_text("\n".join(report_lines), encoding="utf-8")

    manifest = {
        "timestamp_utc": _utc(),
        "output_dir": str(out.relative_to(REPO)),
        "dataset_csv": str(csv_path.relative_to(REPO)) if csv_path.exists() else None,
        "dataset_sha256": _sha256_file(csv_path) if csv_path.exists() else None,
        "backend": BACKEND,
        "validation": validation_safe,
        "commands": ["python3 docs/scripts/multidomain_stress_campaign_v2.py", f"--reps {args.reps}"],
    }
    (out / "manifest.json").write_text(json.dumps(_json_safe(manifest), indent=2), encoding="utf-8")
    print(json.dumps(validation_safe, indent=2))
    return 0 if validation["campaign_approved"] else 2


if __name__ == "__main__":
    sys.exit(main())
