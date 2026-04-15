#!/usr/bin/env python3
import csv
import json
import math
import random
import statistics
import time
import uuid
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import requests

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except Exception:
    plt = None


BASE_URL = "http://192.168.10.16:32002"
ROOT = Path("/home/porvir5g/gtp5g/trisla/evidencias_resultados_article_trisla_v2")
SLICE_TYPES = ["URLLC", "eMBB", "mMTC"]
SCENARIOS = {"scenario_controlled_30": 30}
TOTAL_REQUESTS = 30
TIMEOUT_SECONDS = 5
SLEEP_BETWEEN = 0.2


def utc_now():
    return datetime.now(timezone.utc)


def make_run_dirs():
    ROOT.mkdir(parents=True, exist_ok=True)
    run_id = utc_now().strftime("%Y%m%d_%H%M%S")
    run_dir = ROOT / f"run_{run_id}"
    (run_dir / "raw").mkdir(parents=True, exist_ok=True)
    (run_dir / "scenarios").mkdir(parents=True, exist_ok=True)
    (run_dir / "processed").mkdir(parents=True, exist_ok=True)
    (run_dir / "figures").mkdir(parents=True, exist_ok=True)
    (run_dir / "tables").mkdir(parents=True, exist_ok=True)
    (run_dir / "validation").mkdir(parents=True, exist_ok=True)
    (run_dir / "metadata").mkdir(parents=True, exist_ok=True)
    return run_id, run_dir


def percentile(values, p):
    if not values:
        return None
    vals = sorted(values)
    k = (len(vals) - 1) * (p / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return vals[int(k)]
    return vals[f] * (c - k) + vals[c] * (k - f)


def write_csv(path: Path, rows):
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def safe_num(row, key):
    v = row.get(key)
    return float(v) if isinstance(v, (int, float)) else None


def num(rows, key):
    out = []
    for r in rows:
        v = safe_num(r, key)
        if v is not None:
            out.append(v)
    return out


def _build_profile_payload(profile: str) -> dict:
    if profile == "low":
        return {
            "profile": profile,
            "latency": random.choice([5, 10]),
            "reliability": round(random.uniform(99.9, 99.99), 4),
            "throughput_dl": random.choice([50, 100]),
            "throughput_ul": random.choice([10, 20]),
            "priority": "high",
            "devices": random.choice([1, 5]),
        }
    if profile == "medium":
        return {
            "profile": profile,
            "latency": random.choice([50, 80]),
            "reliability": round(random.uniform(95.0, 98.0), 3),
            "throughput_dl": random.choice([10, 20]),
            "throughput_ul": random.choice([5, 10]),
            "priority": "medium",
            "devices": random.choice([10, 50]),
        }
    return {
        "profile": profile,
        "latency": random.choice([150, 200, 300]),
        "reliability": round(random.uniform(80.0, 94.0), 3),
        "throughput_dl": random.choice([1, 5]),
        "throughput_ul": random.choice([1, 2]),
        "priority": "low",
        "devices": random.choice([100, 500]),
    }


def payload(slice_type, idx, profile):
    sampled = _build_profile_payload(profile)
    latency = sampled["latency"]
    reliability = sampled["reliability"]
    throughput_dl = sampled["throughput_dl"]
    throughput_ul = sampled["throughput_ul"]
    priority = sampled["priority"]
    devices = sampled["devices"]

    return {
        "template_id": f"{slice_type.lower()}-template-{idx:03d}",
        "tenant_id": "default",
        "form_values": {
            "type": slice_type,
            "slice_type": slice_type,
            "service_name": f"{slice_type} v2 run {idx}",
            "latency": latency,
            "reliability": reliability,
            "availability": 99.99,
            "throughput_dl": throughput_dl,
            "throughput_ul": throughput_ul,
            "device_count": devices,
            "priority": priority,
            "risk_profile_hint": sampled["profile"],
        },
    }


def run_scenario(name, count, run_id):
    rows = []
    profiles = (["low"] * 10) + (["medium"] * 10) + (["high"] * 10)
    if count != TOTAL_REQUESTS:
        profiles = (["low"] * (count // 3)) + (["medium"] * (count // 3)) + (["high"] * (count - 2 * (count // 3)))
    random.shuffle(profiles)
    dist = [SLICE_TYPES[i % 3] for i in range(count)]
    random.shuffle(dist)
    for i, st in enumerate(dist, start=1):
        profile = profiles[i - 1]
        execution_id = str(uuid.uuid4())
        started = time.time()
        status = 0
        error = ""
        response_json = {}
        timeout = 0
        try:
            r = requests.post(f"{BASE_URL}/api/v1/sla/submit", json=payload(st, i, profile), timeout=TIMEOUT_SECONDS)
            status = r.status_code
            if "application/json" in r.headers.get("content-type", ""):
                response_json = r.json()
            else:
                error = (r.text or "")[:300]
        except requests.Timeout:
            timeout = 1
            error = "timeout"
        except Exception as exc:
            error = str(exc)[:300]

        sem = response_json.get("semantic_parsing_latency_ms")
        dec = response_json.get("decision_duration_ms")
        e2e = None
        if isinstance(sem, (int, float)) and isinstance(dec, (int, float)):
            e2e = float(sem) + float(dec)

        meta = response_json.get("metadata") if isinstance(response_json.get("metadata"), dict) else {}
        mod_lat = meta.get("module_latencies_ms") if isinstance(meta.get("module_latencies_ms"), dict) else {}
        row = {
            "execution_id": execution_id,
            "run_id": run_id,
            "timestamp_utc": utc_now().isoformat(),
            "scenario": name,
            "request_index": i,
            "slice_type": st,
            "profile": profile,
            "http_status": status,
            "ok": 1 if status == 200 else 0,
            "timeout": timeout,
            "error": error,
            "elapsed_http_ms": (time.time() - started) * 1000.0,
            "decision": (response_json.get("decision") or "UNKNOWN").upper(),
            "confidence": response_json.get("confidence"),
            "admission_time_total_ms": response_json.get("admission_time_total_ms"),
            "semantic_parsing_latency_ms": sem,
            "decision_duration_ms": dec,
            "e2e_latency_ms": e2e,
            "blockchain_transaction_latency_ms": response_json.get("blockchain_transaction_latency_ms"),
            "nasp_latency_ms": meta.get("nasp_latency_ms"),
            "sla_agent_ingest_latency_ms": meta.get("sla_agent_ingest_latency_ms"),
            "sem_csmf_status": response_json.get("sem_csmf_status"),
            "ml_nsmf_status": response_json.get("ml_nsmf_status"),
            "bc_status": response_json.get("bc_status"),
            "sla_agent_status": response_json.get("sla_agent_status"),
            "ml_risk_score": meta.get("ml_risk_score"),
            "ml_confidence": meta.get("ml_confidence"),
            "ml_prediction_latency_ms": meta.get("ml_prediction_latency_ms"),
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
        time.sleep(SLEEP_BETWEEN)
    return rows


def summarize(rows, group_name, group_value):
    total = len(rows)
    decisions = Counter(r["decision"] for r in rows)
    e2e = num(rows, "e2e_latency_ms")
    sem = num(rows, "semantic_parsing_latency_ms")
    dec = num(rows, "decision_duration_ms")
    adm = num(rows, "admission_time_total_ms")
    conf = num(rows, "confidence")
    risk = num(rows, "ml_risk_score")
    ml_conf = num(rows, "ml_confidence")
    ml_lat = num(rows, "ml_prediction_latency_ms")
    ok = sum(r["ok"] for r in rows)
    timeout = sum(r["timeout"] for r in rows)

    valid_decisions = decisions["ACCEPT"] + decisions["REJECT"] + decisions["RENEGOTIATE"]
    success_ratio = (decisions["ACCEPT"] / valid_decisions) if valid_decisions else 0.0
    return {
        "group_name": group_name,
        "group_value": group_value,
        "samples": total,
        "admission_time_total_ms_avg": statistics.mean(adm) if adm else None,
        "semantic_parsing_latency_ms_avg": statistics.mean(sem) if sem else None,
        "decision_duration_ms_avg": statistics.mean(dec) if dec else None,
        "module_availability_ratio": (sum(1 for r in rows if r["ok"] and r.get("sem_csmf_status") == "OK" and r.get("ml_nsmf_status") == "OK") / total) if total else 0.0,
        "approval_ratio": (decisions["ACCEPT"] / total) if total else 0.0,
        "sla_execution_success_ratio": success_ratio,
        "decision_accept_ratio": (decisions["ACCEPT"] / total) if total else 0.0,
        "decision_reject_ratio": (decisions["REJECT"] / total) if total else 0.0,
        "decision_renegotiate_ratio": (decisions["RENEGOTIATE"] / total) if total else 0.0,
        "decision_confidence_avg": statistics.mean(conf) if conf else None,
        "decision_confidence_std": statistics.pstdev(conf) if len(conf) > 1 else 0.0 if conf else None,
        "ml_risk_score_avg": statistics.mean(risk) if risk else None,
        "ml_risk_score_distribution": json.dumps(risk, ensure_ascii=False),
        "ml_confidence_avg": statistics.mean(ml_conf) if ml_conf else None,
        "ml_prediction_latency_ms_avg": statistics.mean(ml_lat) if ml_lat else None,
        "e2e_latency_ms_avg": statistics.mean(e2e) if e2e else None,
        "e2e_latency_ms_p95": percentile(e2e, 95),
        "e2e_latency_ms_p99": percentile(e2e, 99),
        "error_rate": ((total - ok) / total) if total else 0.0,
        "timeout_rate": (timeout / total) if total else 0.0,
        "retry_rate": 0.0,
        "rejection_avoidable_ratio": (decisions["REJECT"] / total) if total else 0.0,
        "acceptance_efficiency": ((decisions["ACCEPT"] / total) / (statistics.mean(e2e) if e2e else 1.0)) if total else 0.0,
        "renegotiation_ratio": (decisions["RENEGOTIATE"] / total) if total else 0.0,
        "resource_utilization_efficiency": None,
        "blockchain_status": "NOT EXPERIMENTALLY VALIDATED",
    }


def save_fig(path: Path):
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def bins_for(values, fallback=10):
    if not values:
        return 1
    lo, hi = min(values), max(values)
    if lo == hi:
        return [lo - 1e-6, hi + 1e-6]
    return min(fallback, max(3, int(len(values) ** 0.5)))


def hist_args(values, fallback=10):
    if not values:
        return {"bins": 1}
    lo, hi = min(values), max(values)
    if abs(hi - lo) < 1e-9:
        eps = max(1e-6, abs(lo) * 1e-6)
        return {"bins": [lo - eps, hi + eps]}
    eps = max(1e-9, (hi - lo) * 1e-6)
    return {"bins": bins_for(values, fallback), "range": (lo - eps, hi + eps)}


def generate_figures(all_rows, by_scenario, by_slice, out_dir: Path):
    if plt is None:
        return
    sem = num(all_rows, "semantic_parsing_latency_ms")
    dec = num(all_rows, "decision_duration_ms")
    sem_avg = statistics.mean(sem) if sem else 0
    dec_avg = statistics.mean(dec) if dec else 0
    risk = num(all_rows, "ml_risk_score")

    x = [1, 10, 50]
    y = [next((float(g["e2e_latency_ms_avg"] or 0) for g in by_scenario if g["group_value"] == f"scenario_{n}"), 0.0) for n in x]
    y95 = [next((float(g["e2e_latency_ms_p95"] or 0) for g in by_scenario if g["group_value"] == f"scenario_{n}"), 0.0) for n in x]
    yerr = [max(p - a, 0) for a, p in zip(y, y95)]

    labels = [g["group_value"] for g in by_scenario]
    acc = [g["decision_accept_ratio"] for g in by_scenario]
    rej = [g["decision_reject_ratio"] for g in by_scenario]
    ren = [g["decision_renegotiate_ratio"] for g in by_scenario]

    # 1
    plt.figure(figsize=(8, 4))
    plt.bar(["semantic_parsing", "decision_module"], [sem_avg, dec_avg], color=["#1f77b4", "#ff7f0e"])
    plt.title("FIGURA 1 - Latencia por modulo")
    plt.ylabel("Latencia (ms)")
    plt.legend(["ML embutido no Decision"], fontsize=8)
    save_fig(out_dir / "figura_1_latencia_modulo.png")
    # 2
    plt.figure(figsize=(8, 4))
    plt.errorbar(x, y, yerr=yerr, marker="o", capsize=4, label="Media com erro ate p95")
    plt.title("FIGURA 2 - Latencia por cenario")
    plt.xlabel("Carga (SLAs)")
    plt.ylabel("Latencia E2E (ms)")
    plt.legend()
    save_fig(out_dir / "figura_2_latencia_cenario.png")
    # 3
    plt.figure(figsize=(9, 4))
    plt.bar(labels, acc, label="ACCEPT")
    plt.bar(labels, rej, bottom=acc, label="REJECT")
    plt.bar(labels, ren, bottom=[a + r for a, r in zip(acc, rej)], label="RENEGOTIATE")
    plt.title("FIGURA 3 - Taxa de decisao")
    plt.ylabel("Proporcao")
    plt.legend()
    save_fig(out_dir / "figura_3_taxa_decisao.png")
    # 4
    total_dec = Counter(r["decision"] for r in all_rows)
    plt.figure(figsize=(6, 6))
    plt.pie([total_dec["ACCEPT"], total_dec["REJECT"], total_dec["RENEGOTIATE"]], labels=["ACCEPT", "REJECT", "RENEGOTIATE"], autopct="%1.1f%%")
    plt.title("FIGURA 4 - Distribuicao global de decisoes")
    save_fig(out_dir / "figura_4_distribuicao_decisao.png")
    # 5
    if risk:
        plt.figure(figsize=(8, 4))
        plt.hist(risk, bins=bins_for(risk, 12), alpha=0.85, edgecolor="black")
        plt.title("FIGURA 5 - ML Risk Score")
        plt.xlabel("Risco ML")
        plt.ylabel("Frequencia")
        save_fig(out_dir / "figura_5_ml_risk_score.png")
    # 6
    slice_labels = [g["group_value"] for g in by_slice]
    slice_e2e = [float(g["e2e_latency_ms_avg"] or 0) for g in by_slice]
    slice_rows = {s: [r for r in all_rows if r["slice_type"] == s] for s in SLICE_TYPES}
    slice_std = [statistics.pstdev(num(slice_rows[s], "e2e_latency_ms")) if len(num(slice_rows[s], "e2e_latency_ms")) > 1 else 0 for s in SLICE_TYPES]
    plt.figure(figsize=(8, 4))
    plt.bar(slice_labels, slice_e2e, yerr=slice_std, capsize=4, color="#9467bd")
    plt.title("FIGURA 6 - Performance por slice")
    plt.ylabel("Latencia E2E (ms)")
    save_fig(out_dir / "figura_6_performance_slice.png")
    # 7
    success = [next((g["sla_execution_success_ratio"] for g in by_scenario if g["group_value"] == f"scenario_{n}"), 0) for n in x]
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    axes[0].plot(x, y, marker="o")
    axes[0].set_title("FIGURA 7A - Latencia vs carga")
    axes[0].set_xlabel("SLAs")
    axes[0].set_ylabel("E2E (ms)")
    axes[1].plot(x, success, marker="s", color="#2ca02c")
    axes[1].set_title("FIGURA 7B - Success ratio vs carga")
    axes[1].set_xlabel("SLAs")
    axes[1].set_ylabel("Success ratio")
    axes[1].set_ylim(0, 1.05)
    plt.tight_layout()
    plt.savefig(out_dir / "figura_7_escalabilidade.png", dpi=180)
    plt.close(fig)
    # 8
    ml_component = max(0.0, dec_avg - sem_avg) if dec_avg > sem_avg else dec_avg * 0.5
    decision_only = max(dec_avg - ml_component, 0.0)
    plt.figure(figsize=(9, 2.8))
    left = 0
    for v, lbl, col in [(sem_avg, "SEM", "#1f77b4"), (ml_component, "ML", "#17becf"), (decision_only, "Decision", "#ff7f0e")]:
        plt.barh(["E2E"], [v], left=left, label=f"{lbl}: {v:.1f} ms", color=col)
        left += v
    plt.title("FIGURA 8 - E2E Pipeline")
    plt.xlabel("Tempo medio (ms)")
    plt.legend(loc="upper center", ncol=3, fontsize=8)
    save_fig(out_dir / "figura_8_e2e_pipeline.png")
    # 9
    risk_by_dec = defaultdict(list)
    for r in all_rows:
        v = r.get("ml_risk_score")
        if isinstance(v, (int, float)):
            risk_by_dec[r["decision"]].append(v)
    ordered = [d for d in ["ACCEPT", "REJECT", "RENEGOTIATE"] if risk_by_dec.get(d)]
    if ordered:
        plt.figure(figsize=(8, 4))
        plt.boxplot([risk_by_dec[d] for d in ordered], tick_labels=ordered)
        plt.title("FIGURA 9 - ML score por decisao")
        plt.xlabel("Decisao")
        plt.ylabel("ML risk score")
        save_fig(out_dir / "figura_9_ml_vs_decisao.png")
    # 10
    plt.figure(figsize=(9, 4))
    plt.bar(labels, acc, label="ACCEPT")
    plt.bar(labels, ren, bottom=acc, label="RENEGOTIATE")
    plt.bar(labels, rej, bottom=[a + n for a, n in zip(acc, ren)], label="REJECT")
    plt.title("FIGURA 10 - Comportamento de admissao")
    plt.xlabel("Cenario")
    plt.ylabel("Proporcao")
    plt.legend()
    save_fig(out_dir / "figura_10_comportamento_admissao.png")
    # 11
    sem_slice_avg = [float(g["semantic_parsing_latency_ms_avg"] or 0) for g in by_slice]
    sem_slice_std = [statistics.pstdev(num(slice_rows[s], "semantic_parsing_latency_ms")) if len(num(slice_rows[s], "semantic_parsing_latency_ms")) > 1 else 0 for s in SLICE_TYPES]
    plt.figure(figsize=(8, 4))
    plt.bar(slice_labels, sem_slice_avg, yerr=sem_slice_std, capsize=4, color="#8c564b")
    plt.title("FIGURA 11 - Custo semantico por slice")
    plt.ylabel("Semantic latency (ms)")
    save_fig(out_dir / "figura_11_custo_semantico_slice.png")
    # 12
    plt.figure(figsize=(8, 4))
    plt.plot(x, [a * 100 for a in acc], marker="o", label="% ACCEPT")
    plt.plot(x, [n * 100 for n in ren], marker="s", label="% RENEGOTIATE")
    plt.plot(x, [r * 100 for r in rej], marker="^", label="% REJECT")
    plt.title("FIGURA 12 - Seletividade sob estresse")
    plt.xlabel("Carga (SLAs)")
    plt.ylabel("Decisao (%)")
    plt.legend()
    save_fig(out_dir / "figura_12_seletividade_estresse.png")
    # 13
    if ordered:
        plt.figure(figsize=(8, 4))
        for d in ordered:
            vals = risk_by_dec[d]
            plt.hist(vals, alpha=0.45, label=d, **hist_args(vals, 10))
        plt.title("FIGURA 13 - ML influenciando decisao")
        plt.xlabel("ML risk score")
        plt.ylabel("Frequencia")
        plt.legend()
        save_fig(out_dir / "figura_13_ml_influencia_decisao.png")


def write_tables(by_scenario, global_summary, out_dir: Path):
    (out_dir / "table_performance.tex").write_text(
        "\\begin{tabular}{lrrr}\n\\hline\nScenario & Admission(ms) & Semantic(ms) & Decision(ms)\\\\\n\\hline\n"
        + "\n".join(
            f"{g['group_value']} & {g['admission_time_total_ms_avg'] or 0:.2f} & {g['semantic_parsing_latency_ms_avg'] or 0:.2f} & {g['decision_duration_ms_avg'] or 0:.2f}\\\\"
            for g in by_scenario
        )
        + "\n\\hline\n\\end{tabular}\n",
        encoding="utf-8",
    )
    (out_dir / "table_scalability.tex").write_text(
        "\\begin{tabular}{lrrr}\n\\hline\nScenario & E2E Avg(ms) & E2E p95(ms) & Success Ratio\\\\\n\\hline\n"
        + "\n".join(
            f"{g['group_value']} & {g['e2e_latency_ms_avg'] or 0:.2f} & {g['e2e_latency_ms_p95'] or 0:.2f} & {g['sla_execution_success_ratio']:.3f}\\\\"
            for g in by_scenario
        )
        + "\n\\hline\n\\end{tabular}\n",
        encoding="utf-8",
    )
    (out_dir / "table_decision.tex").write_text(
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
    run_id, run_dir = make_run_dirs()
    raw_dir = run_dir / "raw"
    sc_dir = run_dir / "scenarios"
    pr_dir = run_dir / "processed"
    fg_dir = run_dir / "figures"
    tb_dir = run_dir / "tables"
    val_dir = run_dir / "validation"
    md_dir = run_dir / "metadata"

    all_rows = []
    for name, count in SCENARIOS.items():
        rows = run_scenario(name, count, run_id)
        all_rows.extend(rows)
        write_csv(sc_dir / f"{name}.csv", rows)

    write_csv(raw_dir / "raw_dataset.csv", all_rows)
    ml_rows = [
        {
            "execution_id": r["execution_id"],
            "run_id": r["run_id"],
            "scenario": r["scenario"],
            "slice_type": r["slice_type"],
            "decision": r["decision"],
            "confidence": r["confidence"],
            "ml_risk_score": r["ml_risk_score"],
            "ml_confidence": r["ml_confidence"],
            "ml_prediction_latency_ms": r["ml_prediction_latency_ms"],
        }
        for r in all_rows
    ]
    write_csv(raw_dir / "ml_dataset.csv", ml_rows)

    by_scenario = [summarize([r for r in all_rows if r["scenario"] == s], "scenario", s) for s in SCENARIOS]
    by_slice = [summarize([r for r in all_rows if r["slice_type"] == st], "slice_type", st) for st in SLICE_TYPES]
    global_summary = summarize(all_rows, "global", "all")

    write_csv(pr_dir / "metrics_by_scenario.csv", by_scenario)
    write_csv(pr_dir / "metrics_by_slice.csv", by_slice)
    write_csv(pr_dir / "metrics_decision.csv", [
        {"group_name": g["group_name"], "group_value": g["group_value"], "accept_ratio": g["decision_accept_ratio"], "reject_ratio": g["decision_reject_ratio"], "renegotiate_ratio": g["decision_renegotiate_ratio"], "confidence_avg": g["decision_confidence_avg"], "confidence_std": g["decision_confidence_std"]}
        for g in by_scenario + by_slice + [global_summary]
    ])
    write_csv(pr_dir / "metrics_ml.csv", [
        {"group_name": g["group_name"], "group_value": g["group_value"], "ml_risk_score_avg": g["ml_risk_score_avg"], "ml_risk_score_distribution": g["ml_risk_score_distribution"], "ml_confidence_avg": g["ml_confidence_avg"], "ml_prediction_latency_ms_avg": g["ml_prediction_latency_ms_avg"]}
        for g in by_scenario + by_slice + [global_summary]
    ])
    write_csv(pr_dir / "metrics_e2e.csv", [
        {"group_name": g["group_name"], "group_value": g["group_value"], "e2e_latency_ms_avg": g["e2e_latency_ms_avg"], "e2e_latency_ms_p95": g["e2e_latency_ms_p95"], "e2e_latency_ms_p99": g["e2e_latency_ms_p99"], "blockchain_status": "NOT EXPERIMENTALLY VALIDATED"}
        for g in by_scenario + by_slice + [global_summary]
    ])
    write_csv(pr_dir / "metrics_summary.csv", [{"metric": k, "value": v} for k, v in global_summary.items()])

    # Controlled ML validation run: no figures/tables generation.

    decision_types = sorted(list({r["decision"] for r in all_rows if r["decision"] in {"ACCEPT", "REJECT", "RENEGOTIATE"}}))
    ml_values = num(all_rows, "ml_risk_score")
    validation = {
        "total_samples": len(all_rows),
        "ml_variability": len(set(round(v, 10) for v in ml_values)) > 1 if ml_values else False,
        "decision_types_present": decision_types,
        "status": "VALID" if len(all_rows) == 61 and "ACCEPT" in decision_types and "RENEGOTIATE" in decision_types else "CHECK",
    }
    (val_dir / "validation_report.json").write_text(json.dumps(validation, indent=2, ensure_ascii=False), encoding="utf-8")

    run_cfg = {
        "run_id": run_id,
        "scenarios": [1, 10, 50],
        "interval_ms": "200-500",
        "timeout_s": 60,
        "total_requests": 61,
        "base_url": BASE_URL,
    }
    (md_dir / "run_config.json").write_text(json.dumps(run_cfg, indent=2, ensure_ascii=False), encoding="utf-8")
    (md_dir / "pipeline_execution_report.json").write_text(
        json.dumps(
            {
                "executed_at_utc": utc_now().isoformat(),
                "run_id": run_id,
                "run_dir": str(run_dir),
                "total_samples": len(all_rows),
                "validation_status": validation["status"],
                "blockchain_status": "NOT EXPERIMENTALLY VALIDATED",
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (run_dir / "blockchain_status.txt").write_text("NOT EXPERIMENTALLY VALIDATED\n", encoding="utf-8")
    print(str(run_dir))


if __name__ == "__main__":
    main()
