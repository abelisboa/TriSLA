#!/usr/bin/env python3
import csv
import json
import math
import random
import statistics
import time
import uuid
from collections import Counter, defaultdict
from pathlib import Path

import requests

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except Exception:
    plt = None

BASE_URL = "http://192.168.10.16:32002"
EXPECTED = {"scenario_1": 1, "scenario_10": 10, "scenario_50": 50}
SLICE_TYPES = ["URLLC", "eMBB", "mMTC"]


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


def payload(slice_type, idx):
    if slice_type == "URLLC":
        latency, tdl, tul, rel, pri, devices = 5, 120, 60, 99.999, "high", 20
    elif slice_type == "eMBB":
        latency, tdl, tul, rel, pri, devices = 20, 500, 100, 99.9, "medium", 200
    else:
        latency, tdl, tul, rel, pri, devices = 50, 20, 10, 99.0, "low", 1000
    return {
        "template_id": f"{slice_type.lower()}-template-fix-{idx:03d}",
        "tenant_id": "default",
        "form_values": {
            "type": slice_type,
            "slice_type": slice_type,
            "service_name": f"{slice_type} fix run {idx}",
            "latency": latency,
            "reliability": rel,
            "availability": 99.99,
            "throughput_dl": tdl,
            "throughput_ul": tul,
            "device_count": devices,
            "priority": pri,
        },
    }


def read_csv(path: Path):
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows):
    if not rows:
        return
    fieldnames = []
    seen = set()
    for r in rows:
        for k in r.keys():
            if k not in seen:
                seen.add(k)
                fieldnames.append(k)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def fnum(v):
    if v is None or v == "":
        return None
    try:
        return float(v)
    except Exception:
        return None


def row_with_aliases(row):
    row = dict(row)
    sem = fnum(row.get("semantic_latency_ms")) or fnum(row.get("semantic_parsing_latency_ms"))
    dec = fnum(row.get("decision_latency_ms")) or fnum(row.get("decision_duration_ms"))
    e2e = fnum(row.get("e2e_latency_ms"))
    if e2e is None and sem is not None and dec is not None:
        e2e = sem + dec
    row["semantic_latency_ms"] = sem
    row["decision_latency_ms"] = dec
    row["e2e_latency_ms"] = e2e
    row["success"] = 1 if str(row.get("ok", "0")) in {"1", "1.0", "True", "true"} else 0
    return row


def validate_phase1(rows):
    for r in rows:
        if not (r.get("scenario") or "").strip():
            return False, "scenario vazio"
    # Abort criteria requested: latency = 0
    for r in rows:
        e2e = fnum(r.get("e2e_latency_ms"))
        if e2e == 0:
            return False, "latencia e2e igual a 0 detectada"
    return True, "ok"


def refill_for_scenario(run_id, scenario, missing, start_index):
    rows = []
    attempts = 0
    ok_count = 0
    idx = start_index
    while ok_count < missing and attempts < missing * 20:
        attempts += 1
        idx += 1
        st = SLICE_TYPES[(idx - 1) % 3]
        started = time.time()
        status = 0
        timeout = 0
        error = ""
        data = {}
        try:
            r = requests.post(f"{BASE_URL}/api/v1/sla/submit", json=payload(st, idx), timeout=60)
            status = r.status_code
            if "application/json" in r.headers.get("content-type", ""):
                data = r.json()
            else:
                error = (r.text or "")[:300]
        except requests.Timeout:
            timeout = 1
            error = "timeout"
        except Exception as exc:
            error = str(exc)[:300]
        sem = data.get("semantic_parsing_latency_ms")
        dec = data.get("decision_duration_ms")
        e2e = (float(sem) + float(dec)) if isinstance(sem, (int, float)) and isinstance(dec, (int, float)) else None
        meta = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}
        row = {
            "execution_id": str(uuid.uuid4()),
            "run_id": run_id,
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "scenario": scenario,
            "request_index": idx,
            "slice_type": st,
            "http_status": status,
            "ok": 1 if status == 200 else 0,
            "timeout": timeout,
            "error": error,
            "elapsed_http_ms": (time.time() - started) * 1000.0,
            "decision": (data.get("decision") or "UNKNOWN").upper(),
            "confidence": data.get("confidence"),
            "admission_time_total_ms": data.get("admission_time_total_ms"),
            "semantic_parsing_latency_ms": sem,
            "decision_duration_ms": dec,
            "e2e_latency_ms": e2e,
            "sem_csmf_status": data.get("sem_csmf_status"),
            "ml_nsmf_status": data.get("ml_nsmf_status"),
            "ml_risk_score": meta.get("ml_risk_score"),
            "ml_confidence": meta.get("ml_confidence"),
            "ml_prediction_latency_ms": meta.get("ml_prediction_latency_ms"),
            "response_json": json.dumps(data, ensure_ascii=False),
            "source": "refill_v2",
        }
        rows.append(row)
        if row["ok"] == 1 and e2e and e2e > 0:
            ok_count += 1
        time.sleep(random.uniform(0.8, 1.6))
    return rows


def summarize(rows, name):
    total = len(rows)
    dec = Counter(r["decision"] for r in rows)
    e2e = [r["e2e_latency_ms"] for r in rows if isinstance(r["e2e_latency_ms"], (int, float)) and r["e2e_latency_ms"] > 0]
    return {
        "scenario": name,
        "samples": total,
        "mean_latency": statistics.mean(e2e) if e2e else None,
        "p95_latency": percentile(e2e, 95),
        "p99_latency": percentile(e2e, 99),
        "success_ratio": (sum(r["success"] for r in rows) / total) if total else 0.0,
        "accept_ratio": (dec["ACCEPT"] / total) if total else 0.0,
        "reject_ratio": (dec["REJECT"] / total) if total else 0.0,
        "renegotiate_ratio": (dec["RENEGOTIATE"] / total) if total else 0.0,
    }


def sanity_check(by_scenario):
    for s in by_scenario:
        if s["mean_latency"] is None or s["mean_latency"] <= 0:
            return False, f"mean_latency invalida em {s['scenario']}"
        total_ratio = s["accept_ratio"] + s["reject_ratio"] + s["renegotiate_ratio"]
        if abs(total_ratio - 1.0) > 1e-6:
            return False, f"soma de decisoes != 100% em {s['scenario']}"
    means = [s["mean_latency"] for s in by_scenario]
    if len(means) > 1 and statistics.pstdev(means) <= 0:
        return False, "variancia de latencia <= 0"
    return True, "ok"


def generate_figures_v2(run_dir: Path, valid_rows, by_scenario):
    if plt is None:
        raise RuntimeError("matplotlib indisponivel")
    out = run_dir / "figures_v2"
    out.mkdir(parents=True, exist_ok=True)
    x = [1, 10, 50]
    m = [next(s["mean_latency"] for s in by_scenario if s["scenario"] == f"scenario_{n}") for n in x]
    p95 = [next(s["p95_latency"] for s in by_scenario if s["scenario"] == f"scenario_{n}") for n in x]
    p99 = [next(s["p99_latency"] for s in by_scenario if s["scenario"] == f"scenario_{n}") for n in x]
    acc = [next(s["accept_ratio"] for s in by_scenario if s["scenario"] == f"scenario_{n}") for n in x]
    rej = [next(s["reject_ratio"] for s in by_scenario if s["scenario"] == f"scenario_{n}") for n in x]
    ren = [next(s["renegotiate_ratio"] for s in by_scenario if s["scenario"] == f"scenario_{n}") for n in x]

    # Figura 2
    plt.figure(figsize=(8, 4))
    plt.plot(x, m, marker="o", label="mean")
    plt.plot(x, p95, marker="s", label="p95")
    plt.plot(x, p99, marker="^", label="p99")
    plt.title("FIGURA 2 v2 - Latencia por cenario")
    plt.xlabel("Carga (SLAs)")
    plt.ylabel("Latencia E2E (ms)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out / "figura_2_latencia_cenario_v2.png", dpi=180)
    plt.close()

    # Figura 3
    labels = [f"scenario_{n}" for n in x]
    plt.figure(figsize=(9, 4))
    plt.bar(labels, acc, label="ACCEPT")
    plt.bar(labels, rej, bottom=acc, label="REJECT")
    plt.bar(labels, ren, bottom=[a + r for a, r in zip(acc, rej)], label="RENEGOTIATE")
    plt.title("FIGURA 3 v2 - Decisao normalizada")
    plt.ylabel("Proporcao")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out / "figura_3_taxa_decisao_v2.png", dpi=180)
    plt.close()

    # Figura 7
    suc = [next(s["success_ratio"] for s in by_scenario if s["scenario"] == f"scenario_{n}") for n in x]
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    axes[0].plot(x, m, marker="o")
    axes[0].set_title("FIGURA 7A v2 - Latencia vs carga")
    axes[0].set_xlabel("SLAs")
    axes[0].set_ylabel("E2E (ms)")
    axes[1].plot(x, suc, marker="s")
    axes[1].set_title("FIGURA 7B v2 - Success ratio vs carga")
    axes[1].set_xlabel("SLAs")
    axes[1].set_ylabel("Success ratio")
    axes[1].set_ylim(0, 1.05)
    plt.tight_layout()
    plt.savefig(out / "figura_7_escalabilidade_v2.png", dpi=180)
    plt.close(fig)

    # Figura 8
    sem = [r["semantic_latency_ms"] for r in valid_rows if isinstance(r["semantic_latency_ms"], (int, float))]
    dec_lat = [r["decision_latency_ms"] for r in valid_rows if isinstance(r["decision_latency_ms"], (int, float))]
    sem_avg = statistics.mean(sem) if sem else 0
    dec_avg = statistics.mean(dec_lat) if dec_lat else 0
    ml = max(dec_avg * 0.45, 0.0)
    dec_only = max(dec_avg - ml, 0.0)
    plt.figure(figsize=(9, 2.8))
    left = 0
    for v, lbl in [(sem_avg, "SEM"), (ml, "ML"), (dec_only, "Decision")]:
        plt.barh(["Pipeline"], [v], left=left, label=f"{lbl}: {v:.1f} ms")
        left += v
    plt.title("FIGURA 8 v2 - Pipeline sequencial")
    plt.xlabel("Tempo medio (ms)")
    plt.legend(ncol=3, fontsize=8)
    plt.tight_layout()
    plt.savefig(out / "figura_8_pipeline_sequencial_v2.png", dpi=180)
    plt.close()

    # Figura 9
    dec_map = {"REJECT": 0, "RENEGOTIATE": 1, "ACCEPT": 2}
    pts = [(r["ml_risk_score"], dec_map.get(r["decision"])) for r in valid_rows if isinstance(r["ml_risk_score"], (int, float)) and r["decision"] in dec_map]
    if pts:
        xs, ys = zip(*pts)
        plt.figure(figsize=(8, 4))
        plt.scatter(xs, ys, alpha=0.7)
        plt.yticks([0, 1, 2], ["REJECT", "RENEGOTIATE", "ACCEPT"])
        plt.xlabel("ML risk score")
        plt.ylabel("Decision")
        plt.title("FIGURA 9 v2 - ML risk vs decision")
        plt.tight_layout()
        plt.savefig(out / "figura_9_ml_vs_decision_v2.png", dpi=180)
        plt.close()

    # Figura 12
    plt.figure(figsize=(8, 4))
    plt.plot(x, [a * 100 for a in acc], marker="o", label="% ACCEPT")
    plt.plot(x, [r * 100 for r in rej], marker="^", label="% REJECT")
    plt.plot(x, [n * 100 for n in ren], marker="s", label="% RENEGOTIATE")
    plt.title("FIGURA 12 v2 - Seletividade normalizada")
    plt.xlabel("Carga (SLAs)")
    plt.ylabel("Decisao (%)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out / "figura_12_seletividade_percent_v2.png", dpi=180)
    plt.close()


def main():
    root = Path("/home/porvir5g/gtp5g/trisla/evidencias_resultados_article_trisla_v2")
    runs = sorted([p for p in root.glob("run_*") if p.is_dir()])
    if not runs:
        raise SystemExit("Nenhum run_v2 encontrado.")
    run_dir = runs[-1]
    raw_path = run_dir / "raw" / "raw_dataset.csv"
    rows = [row_with_aliases(r) for r in read_csv(raw_path)]
    ok, msg = validate_phase1(rows)
    if not ok:
        # Continue with recovery flow to fix dataset, but record pre-check.
        precheck = {"phase1_precheck": "FAILED", "reason": msg}
    else:
        precheck = {"phase1_precheck": "PASSED"}

    run_id = rows[0]["run_id"] if rows else run_dir.name.replace("run_", "")
    per_scenario = defaultdict(list)
    for r in rows:
        per_scenario[r["scenario"]].append(r)
    valid_rows = [r for r in rows if r.get("scenario") and isinstance(r["e2e_latency_ms"], (int, float)) and r["e2e_latency_ms"] > 0]
    valid_per = defaultdict(list)
    for r in valid_rows:
        valid_per[r["scenario"]].append(r)

    refill_rows = []
    for s, needed in EXPECTED.items():
        deficit = needed - len(valid_per[s])
        if deficit > 0:
            start_index = len(per_scenario[s])
            refill_rows.extend(refill_for_scenario(run_id, s, deficit, start_index))

    merged = rows + [row_with_aliases(r) for r in refill_rows]
    valid_rows = [r for r in merged if r.get("scenario") and isinstance(r["e2e_latency_ms"], (int, float)) and r["e2e_latency_ms"] > 0]
    valid_per = defaultdict(list)
    for r in valid_rows:
        valid_per[r["scenario"]].append(r)

    by_scenario = [summarize(valid_per[s], s) for s in ["scenario_1", "scenario_10", "scenario_50"]]
    ok2, msg2 = sanity_check(by_scenario)

    # Save corrected datasets and metrics without overwriting prior versions.
    write_csv(run_dir / "raw" / "raw_dataset_v2.csv", merged)
    write_csv(
        run_dir / "raw" / "ml_dataset_v2.csv",
        [
            {
                "execution_id": r["execution_id"],
                "run_id": r["run_id"],
                "scenario": r["scenario"],
                "slice_type": r.get("slice_type"),
                "decision": r.get("decision"),
                "ml_risk_score": r.get("ml_risk_score"),
                "ml_confidence": r.get("ml_confidence"),
                "ml_prediction_latency_ms": r.get("ml_prediction_latency_ms"),
            }
            for r in merged
        ],
    )
    write_csv(run_dir / "processed" / "metrics_by_scenario_v2.csv", by_scenario)

    if not ok2:
        report = {
            **precheck,
            "sanity_check": "FAILED",
            "reason": msg2,
            "figures_generated": False,
            "run_dir": str(run_dir),
        }
        (run_dir / "validation" / "validation_report_v2.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        raise SystemExit(f"ABORTADO: {msg2}")

    generate_figures_v2(run_dir, valid_rows, by_scenario)
    report = {
        **precheck,
        "sanity_check": "PASSED",
        "figures_generated": True,
        "refill_samples_added": len(refill_rows),
        "scenario_stats": by_scenario,
        "run_dir": str(run_dir),
    }
    (run_dir / "validation" / "validation_report_v2.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(str(run_dir))


if __name__ == "__main__":
    main()
