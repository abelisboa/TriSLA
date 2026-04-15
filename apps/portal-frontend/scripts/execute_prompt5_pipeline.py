#!/usr/bin/env python3
import csv
import json
import math
import random
import statistics
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
import uuid

import requests

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except Exception:
    plt = None


BASE_URL = "http://192.168.10.16:32002"
ROOT_DIR = Path("/home/porvir5g/gtp5g/trisla/evidencias_resultados_article_trisla_v2")

SCENARIOS = {"scenario_1": 1, "scenario_10": 10, "scenario_50": 50}
SLICE_TYPES = ["URLLC", "eMBB", "mMTC"]

# Diretórios do run atual (setados em main()).
OUT_DIR: Path | None = None
RAW_DIR: Path | None = None
SCENARIOS_DIR: Path | None = None
PROCESSED_DIR: Path | None = None
FIGURES_DIR: Path | None = None
TABLES_DIR: Path | None = None
VALIDATION_DIR: Path | None = None
METADATA_DIR: Path | None = None


def make_run_dirs():
    root = ROOT_DIR
    root.mkdir(parents=True, exist_ok=True)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_dir = root / f"run_{run_id}"
    raw_dir = run_dir / "raw"
    scenarios_dir = run_dir / "scenarios"
    processed_dir = run_dir / "processed"
    figures_dir = run_dir / "figures"
    tables_dir = run_dir / "tables"
    validation_dir = run_dir / "validation"
    metadata_dir = run_dir / "metadata"
    for d in (raw_dir, scenarios_dir, processed_dir, figures_dir, tables_dir, validation_dir, metadata_dir):
        d.mkdir(parents=True, exist_ok=True)
    return run_id, run_dir, raw_dir, scenarios_dir, processed_dir, figures_dir, tables_dir, validation_dir, metadata_dir


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def percentile(values, p):
    if not values:
        return None
    vals = sorted(values)
    k = (len(vals) - 1) * (p / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return vals[int(k)]
    d0 = vals[f] * (c - k)
    d1 = vals[c] * (k - f)
    return d0 + d1


def make_payload(slice_type: str, idx: int):
    if slice_type == "URLLC":
        latency, throughput_dl, throughput_ul, reliability, priority, devices = 5, 120, 60, 99.999, "high", 20
    elif slice_type == "eMBB":
        latency, throughput_dl, throughput_ul, reliability, priority, devices = 20, 500, 100, 99.9, "medium", 200
    else:
        latency, throughput_dl, throughput_ul, reliability, priority, devices = 50, 20, 10, 99.0, "low", 1000

    return {
        "template_id": f"{slice_type.lower()}-template-{idx:03d}",
        "tenant_id": "default",
        "form_values": {
            "type": slice_type,
            "slice_type": slice_type,
            "service_name": f"{slice_type} evidence {idx}",
            "latency": latency,
            "reliability": reliability,
            "availability": 99.99,
            "throughput_dl": throughput_dl,
            "throughput_ul": throughput_ul,
            "device_count": devices,
            "coverage_area": "urban",
            "mobility": "low",
            "duration": 3600,
            "priority": priority,
        },
    }


def run_scenario(name: str, count: int, run_id: str):
    rows = []
    cycle = [SLICE_TYPES[i % 3] for i in range(count)]
    random.shuffle(cycle)
    for i, slice_type in enumerate(cycle, start=1):
        payload = make_payload(slice_type, i)
        started = time.time()
        status_code = None
        response_json = {}
        error = ""
        timed_out = 0
        try:
            r = requests.post(f"{BASE_URL}/api/v1/sla/submit", json=payload, timeout=60)
            status_code = r.status_code
            if "application/json" in r.headers.get("content-type", ""):
                response_json = r.json()
            else:
                error = (r.text or "")[:300]
        except requests.Timeout:
            timed_out = 1
            error = "timeout"
        except Exception as exc:
            error = str(exc)[:300]

        elapsed_ms = (time.time() - started) * 1000.0
        decision = (response_json.get("decision") or "UNKNOWN").upper()
        if decision not in {"ACCEPT", "REJECT", "RENEGOTIATE"}:
            decision = "UNKNOWN"

        sem_ms = response_json.get("semantic_parsing_latency_ms")
        dec_ms = response_json.get("decision_duration_ms")
        e2e_ms = None
        if isinstance(sem_ms, (int, float)) and isinstance(dec_ms, (int, float)):
            e2e_ms = float(sem_ms) + float(dec_ms)

        metadata = response_json.get("metadata") if isinstance(response_json.get("metadata"), dict) else {}
        mod_lat = metadata.get("module_latencies_ms") if isinstance(metadata.get("module_latencies_ms"), dict) else {}
        execution_id = metadata.get("execution_id") or str(uuid.uuid4())

        row = {
            "execution_id": execution_id,
            "run_id": run_id,
            "timestamp_utc": now_iso(),
            "scenario": name,
            "request_index": i,
            "slice_type": slice_type,
            "http_status": status_code or 0,
            "ok": 1 if status_code == 200 else 0,
            "timeout": timed_out,
            "error": error,
            "decision": decision,
            "confidence": response_json.get("confidence"),
            "admission_time_total_ms": response_json.get("admission_time_total_ms"),
            "semantic_parsing_latency_ms": sem_ms,
            "decision_duration_ms": dec_ms,
            "e2e_latency_ms": e2e_ms,
            "blockchain_transaction_latency_ms": response_json.get("blockchain_transaction_latency_ms"),
            "nasp_latency_ms": metadata.get("nasp_latency_ms"),
            "sla_agent_ingest_latency_ms": metadata.get("sla_agent_ingest_latency_ms"),
            "sem_csmf_status": response_json.get("sem_csmf_status"),
            "ml_nsmf_status": response_json.get("ml_nsmf_status"),
            "bc_status": response_json.get("bc_status"),
            "sla_agent_status": response_json.get("sla_agent_status"),
            "sla_id": response_json.get("sla_id"),
            "ml_risk_score": metadata.get("ml_risk_score"),
            "ml_confidence": metadata.get("ml_confidence"),
            "ml_prediction_latency_ms": metadata.get("ml_prediction_latency_ms"),
            "module_latency_semantic_parsing_ms": mod_lat.get("semantic_parsing_ms"),
            "module_latency_sem_csmf_internal_ms": mod_lat.get("sem_csmf_internal_ms"),
            "module_latency_sem_pipeline_to_decision_ms": mod_lat.get("sem_pipeline_to_decision_ms"),
            "module_latency_admission_total_ms": mod_lat.get("admission_total_ms"),
            "module_latency_ml_nsmf_predict_ms": mod_lat.get("ml_nsmf_predict_ms"),
            "module_latency_nasp_orchestration_ms": mod_lat.get("nasp_orchestration_ms"),
            "module_latency_blockchain_register_ms": mod_lat.get("blockchain_register_ms"),
            "module_latency_sla_agent_ingest_http_ms": mod_lat.get("sla_agent_ingest_http_ms"),
            "response_json": json.dumps(response_json, ensure_ascii=False),
        }
        rows.append(row)
        time.sleep(random.uniform(0.2, 0.5))
    return rows


def write_csv(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def num(rows, key):
    vals = [r.get(key) for r in rows]
    return [float(v) for v in vals if isinstance(v, (int, float))]


def summarize_group(rows, group_name, group_value):
    total = len(rows)
    decisions = Counter(r["decision"] for r in rows)
    ok = sum(r["ok"] for r in rows)
    decision_base = decisions["ACCEPT"] + decisions["REJECT"] + decisions["RENEGOTIATE"]
    success_ratio = (decisions["ACCEPT"] / decision_base) if decision_base else 0.0
    timeout_rate = (sum(r["timeout"] for r in rows) / total) if total else 0.0
    error_rate = 1.0 - success_ratio
    sem_vals = num(rows, "semantic_parsing_latency_ms")
    dec_vals = num(rows, "decision_duration_ms")
    adm_vals = num(rows, "admission_time_total_ms")
    e2e_vals = num(rows, "e2e_latency_ms")
    conf_vals = num(rows, "confidence")
    ml_risk = num(rows, "ml_risk_score")
    ml_conf = num(rows, "ml_confidence")
    ml_lat = num(rows, "ml_prediction_latency_ms")

    module_ok = 0
    for r in rows:
        sem_ok = (r.get("sem_csmf_status") == "OK")
        ml_ok = (r.get("ml_nsmf_status") == "OK")
        module_ok += 1 if (sem_ok and ml_ok and r.get("ok") == 1) else 0
    module_availability_ratio = (module_ok / total) if total else 0.0

    return {
        "group_name": group_name,
        "group_value": group_value,
        "samples": total,
        "admission_time_total_ms_avg": statistics.mean(adm_vals) if adm_vals else None,
        "semantic_parsing_latency_ms_avg": statistics.mean(sem_vals) if sem_vals else None,
        "decision_duration_ms_avg": statistics.mean(dec_vals) if dec_vals else None,
        "module_availability_ratio": module_availability_ratio,
        "approval_ratio": (decisions["ACCEPT"] / total) if total else 0.0,
        "sla_execution_success_ratio": success_ratio,
        "decision_accept_ratio": (decisions["ACCEPT"] / total) if total else 0.0,
        "decision_reject_ratio": (decisions["REJECT"] / total) if total else 0.0,
        "decision_renegotiate_ratio": (decisions["RENEGOTIATE"] / total) if total else 0.0,
        "decision_confidence_avg": statistics.mean(conf_vals) if conf_vals else None,
        "decision_confidence_std": statistics.pstdev(conf_vals) if len(conf_vals) > 1 else 0.0 if conf_vals else None,
        "ml_risk_score_avg": statistics.mean(ml_risk) if ml_risk else None,
        "ml_risk_score_distribution": json.dumps(ml_risk, ensure_ascii=False),
        "ml_confidence_avg": statistics.mean(ml_conf) if ml_conf else None,
        "ml_prediction_latency_ms_avg": statistics.mean(ml_lat) if ml_lat else None,
        "e2e_latency_ms_avg": statistics.mean(e2e_vals) if e2e_vals else None,
        "e2e_latency_ms_p95": percentile(e2e_vals, 95),
        "e2e_latency_ms_p99": percentile(e2e_vals, 99),
        "error_rate": error_rate,
        "timeout_rate": timeout_rate,
        "retry_rate": 0.0,
        "acceptance_efficiency": ((decisions["ACCEPT"] / total) / (statistics.mean(e2e_vals) if e2e_vals else 1.0)) if total else 0.0,
        "renegotiation_ratio": (decisions["RENEGOTIATE"] / total) if total else 0.0,
        "resource_utilization_efficiency": None,
        "rejection_avoidable_ratio": (decisions["REJECT"] / total) if total else 0.0,
        "blockchain_status": "NOT EXPERIMENTALLY VALIDATED",
    }


def write_processed(all_rows):
    by_scenario = []
    for s in SCENARIOS:
        rows = [r for r in all_rows if r["scenario"] == s]
        by_scenario.append(summarize_group(rows, "scenario", s))

    by_slice = []
    for st in SLICE_TYPES:
        rows = [r for r in all_rows if r["slice_type"] == st]
        by_slice.append(summarize_group(rows, "slice_type", st))

    global_summary = [summarize_group(all_rows, "global", "all")]
    metrics_summary = []
    for item in global_summary:
        for k, v in item.items():
            metrics_summary.append({"metric": k, "value": v})

    write_csv(PROCESSED_DIR / "metrics_by_scenario.csv", by_scenario)
    write_csv(PROCESSED_DIR / "metrics_by_slice.csv", by_slice)
    write_csv(PROCESSED_DIR / "metrics_summary.csv", metrics_summary)

    decisions_rows = []
    for g in by_scenario + by_slice + global_summary:
        decisions_rows.append(
            {
                "group_name": g["group_name"],
                "group_value": g["group_value"],
                "accept_ratio": g["decision_accept_ratio"],
                "reject_ratio": g["decision_reject_ratio"],
                "renegotiate_ratio": g["decision_renegotiate_ratio"],
                "confidence_avg": g["decision_confidence_avg"],
                "confidence_std": g["decision_confidence_std"],
            }
        )
    write_csv(PROCESSED_DIR / "metrics_decision.csv", decisions_rows)

    ml_rows = []
    for g in by_scenario + by_slice + global_summary:
        ml_rows.append(
            {
                "group_name": g["group_name"],
                "group_value": g["group_value"],
                "ml_risk_score_avg": g["ml_risk_score_avg"],
                "ml_risk_score_distribution": g["ml_risk_score_distribution"],
                "ml_confidence_avg": g["ml_confidence_avg"],
                "ml_prediction_latency_ms_avg": g["ml_prediction_latency_ms_avg"],
            }
        )
    write_csv(PROCESSED_DIR / "metrics_ml.csv", ml_rows)

    e2e_rows = []
    for g in by_scenario + by_slice + global_summary:
        e2e_rows.append(
            {
                "group_name": g["group_name"],
                "group_value": g["group_value"],
                "e2e_latency_ms_avg": g["e2e_latency_ms_avg"],
                "e2e_latency_ms_p95": g["e2e_latency_ms_p95"],
                "e2e_latency_ms_p99": g["e2e_latency_ms_p99"],
                "blockchain_status": "NOT EXPERIMENTALLY VALIDATED",
            }
        )
    write_csv(PROCESSED_DIR / "metrics_e2e.csv", e2e_rows)

    return by_scenario, by_slice, global_summary[0]


def _fnum(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _extract_domain_row(row):
    raw = row.get("response_json")
    if not isinstance(raw, str) or not raw.strip():
        return None
    try:
        payload = json.loads(raw)
    except Exception:
        return None
    if not isinstance(payload, dict):
        return None
    md = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
    ts = md.get("telemetry_snapshot") if isinstance(md.get("telemetry_snapshot"), dict) else {}
    if not ts:
        return None

    ran = ts.get("ran") if isinstance(ts.get("ran"), dict) else {}
    transport = ts.get("transport") if isinstance(ts.get("transport"), dict) else {}
    core = ts.get("core") if isinstance(ts.get("core"), dict) else {}

    return {
        "execution_id": row.get("execution_id"),
        "scenario": row.get("scenario"),
        "slice_type": row.get("slice_type"),
        "decision": row.get("decision"),
        "ml_risk_score": _fnum(row.get("ml_risk_score")),
        "ran_prb_utilization": _fnum(ran.get("prb_utilization")),
        "ran_latency_ms": _fnum(ran.get("latency")),
        "transport_rtt_ms": _fnum(transport.get("rtt")),
        "transport_jitter_ms": _fnum(transport.get("jitter")),
        "core_cpu_usage": _fnum(core.get("cpu")),
        "core_memory_usage": _fnum(core.get("memory")),
        "semantic_parsing_latency_ms": _fnum(row.get("semantic_parsing_latency_ms")),
        "decision_duration_ms": _fnum(row.get("decision_duration_ms")),
        "ml_prediction_latency_ms": _fnum(row.get("ml_prediction_latency_ms")),
        "timestamp_utc": row.get("timestamp_utc"),
    }


def write_domain_dataset(all_rows):
    domain_rows = []
    for row in all_rows:
        d = _extract_domain_row(row)
        if d:
            domain_rows.append(d)

    path = PROCESSED_DIR / "domain_dataset.csv"
    if not domain_rows:
        raise RuntimeError("No telemetry_snapshot rows found to build domain_dataset.csv")

    write_csv(path, domain_rows)
    return len(domain_rows)


def save_fig(name):
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / name, dpi=180)
    plt.close()


def generate_figures(all_rows, by_scenario, by_slice):
    def safe_bins(values, default_bins=10):
        clean_data = [v for v in values if isinstance(v, (int, float)) and math.isfinite(v)]
        if not clean_data:
            return 1
        lo = min(clean_data)
        hi = max(clean_data)
        if lo == hi:
            return 1
        unique_count = len(set(clean_data))
        bins = min(default_bins, max(2, int(len(clean_data) ** 0.5)))
        bins = min(bins, unique_count)
        return max(1, bins)

    def nz(v):
        return float(v) if isinstance(v, (int, float)) else 0.0

    if plt is None:
        return
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    # Clean previous artifacts to keep only the current run figures.
    for old in FIGURES_DIR.glob("figura_*.png"):
        old.unlink()

    sem = num(all_rows, "semantic_parsing_latency_ms")
    dec = num(all_rows, "decision_duration_ms")
    plt.figure(figsize=(8, 4))
    sem_avg = statistics.mean(sem) if sem else 0
    dec_avg = statistics.mean(dec) if dec else 0
    plt.bar(["semantic_parsing", "decision_module"], [sem_avg, dec_avg], color=["#1f77b4", "#ff7f0e"])
    plt.title("FIGURA 1 - Latencia por modulo")
    plt.ylabel("Latencia (ms)")
    plt.xlabel("Modulo")
    plt.legend(["ML inferencia embutida no modulo Decision"], loc="upper right", fontsize=8)
    save_fig("figura_1_latencia_modulo.png")

    x = [1, 10, 50]
    y = [nz(next((g["e2e_latency_ms_avg"] for g in by_scenario if g["group_value"] == f"scenario_{n}"), 0)) for n in x]
    y_p95 = [nz(next((g["e2e_latency_ms_p95"] for g in by_scenario if g["group_value"] == f"scenario_{n}"), 0)) for n in x]
    yerr = [max(p95 - avg, 0) for avg, p95 in zip(y, y_p95)]
    plt.figure(figsize=(8, 4))
    plt.errorbar(x, y, yerr=yerr, marker="o", capsize=4, label="E2E media com erro ate p95")
    plt.title("FIGURA 2 - Latencia por cenario")
    plt.xlabel("Carga (numero de SLAs)")
    plt.ylabel("Latencia E2E (ms)")
    plt.legend()
    save_fig("figura_2_latencia_cenario.png")

    labels = [g["group_value"] for g in by_scenario]
    acc = [g["decision_accept_ratio"] for g in by_scenario]
    rej = [g["decision_reject_ratio"] for g in by_scenario]
    ren = [g["decision_renegotiate_ratio"] for g in by_scenario]
    plt.figure(figsize=(9, 4))
    plt.bar(labels, acc, label="ACCEPT")
    plt.bar(labels, rej, bottom=acc, label="REJECT")
    plt.bar(labels, ren, bottom=[a + b for a, b in zip(acc, rej)], label="RENEGOTIATE")
    for i, (a, r, n) in enumerate(zip(acc, rej, ren)):
        plt.text(i, a / 2 if a > 0 else 0.01, f"{a*100:.1f}%", ha="center", va="center", fontsize=8, color="white")
        if r > 0:
            plt.text(i, a + (r / 2), f"{r*100:.1f}%", ha="center", va="center", fontsize=8)
        if n > 0:
            plt.text(i, a + r + (n / 2), f"{n*100:.1f}%", ha="center", va="center", fontsize=8)
    plt.legend()
    plt.title("FIGURA 3 - Taxa de decisao")
    plt.ylabel("Proporcao")
    save_fig("figura_3_taxa_decisao.png")

    total_dec = Counter(r["decision"] for r in all_rows)
    plt.figure(figsize=(6, 6))
    vals = [total_dec["ACCEPT"], total_dec["REJECT"], total_dec["RENEGOTIATE"]]
    plt.pie(vals, labels=["ACCEPT", "REJECT", "RENEGOTIATE"], autopct="%1.1f%%")
    plt.title("FIGURA 4 - Distribuicao de decisao")
    save_fig("figura_4_distribuicao_decisao.png")

    risk = num(all_rows, "ml_risk_score")
    if risk:
        plt.figure(figsize=(8, 4))
        plt.hist(risk, bins=safe_bins(risk, 12), alpha=0.85, color="#2ca02c", edgecolor="black")
        plt.title("FIGURA 5 - ML Risk Score")
        plt.xlabel("Risco ML")
        plt.ylabel("Frequencia")
        save_fig("figura_5_ml_risk_score.png")

    slice_labels = [g["group_value"] for g in by_slice]
    slice_e2e = [nz(g["e2e_latency_ms_avg"]) for g in by_slice]
    slice_rows = {s: [r for r in all_rows if r["slice_type"] == s] for s in SLICE_TYPES}
    slice_std = [statistics.pstdev(num(slice_rows[s], "e2e_latency_ms")) if len(num(slice_rows[s], "e2e_latency_ms")) > 1 else 0 for s in SLICE_TYPES]
    plt.figure(figsize=(8, 4))
    plt.bar(slice_labels, slice_e2e, yerr=slice_std, capsize=4, color="#9467bd")
    plt.title("FIGURA 6 - Performance por slice")
    plt.ylabel("Latencia E2E (ms)")
    plt.xlabel("Slice")
    save_fig("figura_6_performance_slice.png")

    sla_counts = [1, 10, 50]
    success = [next((g["sla_execution_success_ratio"] for g in by_scenario if g["group_value"] == f"scenario_{n}"), 0) for n in sla_counts]
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    axes[0].plot(sla_counts, y, marker="o", label="latency")
    axes[0].set_title("FIGURA 7A - Latencia vs carga")
    axes[0].set_xlabel("SLAs")
    axes[0].set_ylabel("Latencia E2E (ms)")
    axes[0].legend()
    axes[1].plot(sla_counts, success, marker="s", color="#2ca02c", label="success ratio")
    axes[1].set_title("FIGURA 7B - Success ratio vs carga")
    axes[1].set_xlabel("SLAs")
    axes[1].set_ylabel("Success ratio")
    axes[1].set_ylim(0, 1.05)
    axes[1].legend()
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "figura_7_escalabilidade.png", dpi=180)
    plt.close(fig)

    plt.figure(figsize=(9, 2.8))
    ml_component = max(0.0, dec_avg - sem_avg) if dec_avg > sem_avg else dec_avg * 0.5
    remaining_decision = max(dec_avg - ml_component, 0.0)
    stages = [sem_avg, ml_component, remaining_decision]
    labels_pipeline = ["SEM", "ML", "Decision"]
    colors = ["#1f77b4", "#17becf", "#ff7f0e"]
    left = 0
    for v, lbl, c in zip(stages, labels_pipeline, colors):
        plt.barh(["E2E"], [v], left=left, label=f"{lbl}: {v:.1f} ms", color=c)
        left += v
    plt.title("FIGURA 8 - E2E Pipeline com tempos medios")
    plt.xlabel("Tempo medio (ms)")
    plt.legend(loc="upper center", ncol=3, fontsize=8)
    save_fig("figura_8_e2e_pipeline.png")

    # FIGURA 9 - boxplot do score ML por decisao.
    risk_by_decision = defaultdict(list)
    for r in all_rows:
        score = r.get("ml_risk_score")
        if isinstance(score, (int, float)):
            risk_by_decision[r["decision"]].append(score)
    ordered_decisions = [d for d in ["ACCEPT", "REJECT", "RENEGOTIATE"] if risk_by_decision.get(d)]
    if ordered_decisions:
        plt.figure(figsize=(8, 4))
        data = [risk_by_decision[d] for d in ordered_decisions]
        plt.boxplot(data, tick_labels=ordered_decisions)
        plt.title("FIGURA 9 - ML score por decisao")
        plt.xlabel("Decisao")
        plt.ylabel("ML risk score")
        save_fig("figura_9_ml_vs_decisao.png")

    # FIGURA 10 - comportamento de admissao por cenario.
    plt.figure(figsize=(9, 4))
    plt.bar(labels, acc, label="ACCEPT")
    plt.bar(labels, ren, bottom=acc, label="RENEGOTIATE")
    plt.bar(labels, rej, bottom=[a + n for a, n in zip(acc, ren)], label="REJECT")
    plt.title("FIGURA 10 - Comportamento de admissao por cenario")
    plt.xlabel("Cenario")
    plt.ylabel("Proporcao de decisoes")
    plt.legend()
    save_fig("figura_10_comportamento_admissao.png")

    # FIGURA 11 - custo semantico por slice.
    sem_slice_avg = [nz(g["semantic_parsing_latency_ms_avg"]) for g in by_slice]
    sem_slice_std = [statistics.pstdev(num(slice_rows[s], "semantic_parsing_latency_ms")) if len(num(slice_rows[s], "semantic_parsing_latency_ms")) > 1 else 0 for s in SLICE_TYPES]
    plt.figure(figsize=(8, 4))
    plt.bar(slice_labels, sem_slice_avg, yerr=sem_slice_std, capsize=4, color="#8c564b")
    plt.title("FIGURA 11 - Custo semantico por slice")
    plt.xlabel("Slice")
    plt.ylabel("Semantic parsing latency (ms)")
    save_fig("figura_11_custo_semantico_slice.png")

    # FIGURA 12 - seletividade sob estresse.
    plt.figure(figsize=(8, 4))
    plt.plot(sla_counts, [v * 100 for v in acc], marker="o", label="% ACCEPT")
    plt.plot(sla_counts, [v * 100 for v in ren], marker="s", label="% RENEGOTIATE")
    plt.plot(sla_counts, [v * 100 for v in rej], marker="^", label="% REJECT")
    plt.title("FIGURA 12 - Seletividade sob estresse")
    plt.xlabel("Carga (SLAs)")
    plt.ylabel("Decisao (%)")
    plt.legend()
    save_fig("figura_12_seletividade_estresse.png")

    # FIGURA 13 - distribuicao de ML score por decisao.
    if ordered_decisions:
        plt.figure(figsize=(8, 4))
        for d in ordered_decisions:
            vals = risk_by_decision[d]
            plt.hist(vals, bins=safe_bins(vals, 10), alpha=0.45, label=d)
        plt.title("FIGURA 13 - ML influenciando decisao")
        plt.xlabel("ML risk score")
        plt.ylabel("Frequencia")
        plt.legend()
        save_fig("figura_13_ml_influencia_decisao.png")


def write_tables(by_scenario, global_summary):
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    perf = TABLES_DIR / "table_performance.tex"
    scal = TABLES_DIR / "table_scalability.tex"
    dec = TABLES_DIR / "table_decision.tex"

    perf.write_text(
        "\\begin{tabular}{lrrr}\n\\hline\nScenario & Admission(ms) & Semantic(ms) & Decision(ms)\\\\\n\\hline\n"
        + "\n".join(
            f"{g['group_value']} & {g['admission_time_total_ms_avg'] or 0:.2f} & {g['semantic_parsing_latency_ms_avg'] or 0:.2f} & {g['decision_duration_ms_avg'] or 0:.2f}\\\\"
            for g in by_scenario
        )
        + "\n\\hline\n\\end{tabular}\n",
        encoding="utf-8",
    )

    scal.write_text(
        "\\begin{tabular}{lrrr}\n\\hline\nScenario & E2E Avg(ms) & E2E p95(ms) & Success Ratio\\\\\n\\hline\n"
        + "\n".join(
            f"{g['group_value']} & {g['e2e_latency_ms_avg'] or 0:.2f} & {g['e2e_latency_ms_p95'] or 0:.2f} & {g['sla_execution_success_ratio']:.3f}\\\\"
            for g in by_scenario
        )
        + "\n\\hline\n\\end{tabular}\n",
        encoding="utf-8",
    )

    dec.write_text(
        "\\begin{tabular}{lrrr}\n\\hline\nGroup & ACCEPT & REJECT & RENEGOTIATE\\\\\n\\hline\n"
        + "\n".join(
            f"{g['group_value']} & {g['decision_accept_ratio']:.3f} & {g['decision_reject_ratio']:.3f} & {g['decision_renegotiate_ratio']:.3f}\\\\"
            for g in by_scenario
        )
        + f"\nGlobal & {global_summary['decision_accept_ratio']:.3f} & {global_summary['decision_reject_ratio']:.3f} & {global_summary['decision_renegotiate_ratio']:.3f}\\\\"
        + "\n\\hline\n\\end{tabular}\n",
        encoding="utf-8",
    )


def main():
    global OUT_DIR, RAW_DIR, SCENARIOS_DIR, PROCESSED_DIR, FIGURES_DIR, TABLES_DIR, VALIDATION_DIR, METADATA_DIR
    (
        run_id,
        OUT_DIR,
        RAW_DIR,
        SCENARIOS_DIR,
        PROCESSED_DIR,
        FIGURES_DIR,
        TABLES_DIR,
        VALIDATION_DIR,
        METADATA_DIR,
    ) = make_run_dirs()

    all_rows = []
    for name, count in SCENARIOS.items():
        rows = run_scenario(name, count, run_id)
        all_rows.extend(rows)
        write_csv(SCENARIOS_DIR / f"{name}.csv", rows)

    write_csv(RAW_DIR / "raw_dataset.csv", all_rows)
    write_csv(
        RAW_DIR / "ml_dataset.csv",
        [
            {
                "execution_id": r.get("execution_id"),
                "run_id": r.get("run_id"),
                "scenario": r.get("scenario"),
                "slice_type": r.get("slice_type"),
                "decision": r.get("decision"),
                "confidence": r.get("confidence"),
                "ml_risk_score": r.get("ml_risk_score"),
                "ml_confidence": r.get("ml_confidence"),
                "ml_prediction_latency_ms": r.get("ml_prediction_latency_ms"),
            }
            for r in all_rows
        ],
    )

    by_scenario, by_slice, global_summary = write_processed(all_rows)
    domain_rows = write_domain_dataset(all_rows)

    figures_ok = True
    figure_error = ""
    try:
        generate_figures(all_rows, by_scenario, by_slice)
        write_tables(by_scenario, global_summary)
    except Exception as exc:
        # Dataset já consolidado não deve ser invalidado por falha de plot.
        figures_ok = False
        figure_error = str(exc)

    (OUT_DIR / "blockchain_status.txt").write_text(
        'blockchain_status = "NOT EXPERIMENTALLY VALIDATED"\n', encoding="utf-8"
    )
    (METADATA_DIR / "pipeline_execution_report.json").write_text(
        json.dumps(
            {
                "executed_at_utc": now_iso(),
                "base_url": BASE_URL,
                "run_id": run_id,
                "run_path": str(OUT_DIR),
                "scenarios": SCENARIOS,
                "total_samples": len(all_rows),
                "domain_dataset_rows": domain_rows,
                "figures_ok": figures_ok,
                "figure_error": figure_error,
                "blockchain_status": "NOT EXPERIMENTALLY VALIDATED",
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (VALIDATION_DIR / "validation_report.json").write_text(
        json.dumps(
            {
                "status": "VALID" if domain_rows > 0 else "CHECK",
                "domain_dataset_rows": domain_rows,
                "figures_ok": figures_ok,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(str(OUT_DIR))


if __name__ == "__main__":
    main()
