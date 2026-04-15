#!/usr/bin/env python3
"""
PROMPT — VALIDAR TELEMETRIA

Fases:
  1 — Prometheus: cada TELEMETRY_PROMQL_* (dados, variância, unidade só via operador)
  2 — 3 POST /api/v1/sla/submit (baixa / média / alta carga via form_values.scenario)
  3 — Inspecionar metadata.telemetry_snapshot
  4 — Gerar processed/domain_dataset_v2.csv
  5 — Sanity: variância > 0, correlação possível com decisão

Uso (repo root ou com PYTHONPATH):
  export PROMETHEUS_URL=http://...
  export TELEMETRY_PROMQL_RAN_PRB='...'
  # ... demais TELEMETRY_PROMQL_*
  python apps/portal-backend/tools/validate_telemetry.py --backend-url http://localhost:8001

Env:
  PROMETHEUS_URL, BACKEND_URL (default --backend-url), TELEMETRY_PROMQL_*
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

# Repo root: .../trisla
REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CSV = REPO_ROOT / "processed" / "domain_dataset_v2.csv"

TELEMETRY_KEYS = [
    ("RAN_PRB", "ran PRB / carga RAN"),
    ("RAN_LATENCY", "ran latência"),
    ("TRANSPORT_RTT", "transport RTT"),
    ("TRANSPORT_JITTER", "transport jitter"),
    ("CORE_CPU", "core CPU"),
    ("CORE_MEMORY", "core memória"),
]


def _http_get_json(url: str, timeout: float = 60.0) -> Any:
    req = Request(url, method="GET")
    with urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _http_post_json(url: str, body: Dict[str, Any], timeout: float = 120.0) -> Tuple[int, Union[Dict[str, Any], str]]:
    data = json.dumps(body).encode("utf-8")
    req = Request(
        url,
        data=data,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            code = resp.getcode()
            if not raw:
                return code, {}
            try:
                return code, json.loads(raw)
            except json.JSONDecodeError:
                return code, {"_parse_error": raw[:800]}
    except HTTPError as e:
        err_body = ""
        try:
            err_body = e.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        try:
            return e.code, json.loads(err_body) if err_body else {}
        except json.JSONDecodeError:
            return e.code, (err_body or str(e.reason))[:800]


def _prom_base() -> str:
    return os.getenv("PROMETHEUS_URL", "http://prometheus-operated.monitoring:9090").rstrip("/")


def _get_promql(suffix: str) -> Optional[str]:
    v = os.getenv(f"TELEMETRY_PROMQL_{suffix}")
    if v is not None and str(v).strip():
        return str(v).strip()
    return None


def _mean(vals: List[float]) -> float:
    return sum(vals) / len(vals) if vals else 0.0


def _variance(vals: List[float]) -> float:
    if len(vals) < 2:
        return 0.0
    m = _mean(vals)
    return sum((x - m) ** 2 for x in vals) / (len(vals) - 1)


def _pearson(xs: List[float], ys: List[float]) -> Optional[float]:
    n = len(xs)
    if n != len(ys) or n < 2:
        return None
    mx, my = _mean(xs), _mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    denx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    deny = math.sqrt(sum((y - my) ** 2 for y in ys))
    if denx == 0 or deny == 0:
        return None
    return num / (denx * deny)


def phase1_prometheus() -> Tuple[bool, List[Dict[str, Any]]]:
    """query_range últimos ~5min, step 15s — verifica dados e variância."""
    base = _prom_base()
    end = time.time()
    start = end - 300.0
    path = f"{base}/api/v1/query_range"
    rows: List[Dict[str, Any]] = []
    all_ok = True

    for suffix, label in TELEMETRY_KEYS:
        q = _get_promql(suffix)
        row: Dict[str, Any] = {
            "suffix": suffix,
            "label": label,
            "configured": bool(q),
            "has_data": False,
            "variance": None,
            "samples": 0,
            "error": None,
        }
        if not q:
            row["error"] = "TELEMETRY_PROMQL_%s não definido" % suffix
            rows.append(row)
            all_ok = False
            continue
        try:
            full_url = path + "?" + urlencode(
                {
                    "query": q,
                    "start": str(start),
                    "end": str(end),
                    "step": "15s",
                }
            )
            data = _http_get_json(full_url, timeout=45.0)
        except (URLError, HTTPError, OSError, ValueError, json.JSONDecodeError) as e:
            row["error"] = str(e)
            rows.append(row)
            all_ok = False
            continue

        if data.get("status") != "success":
            row["error"] = "status != success: %s" % data.get("error", data)[:200]
            rows.append(row)
            all_ok = False
            continue

        vals: List[float] = []
        for series in data.get("data", {}).get("result") or []:
            for pair in series.get("values") or []:
                if len(pair) >= 2:
                    try:
                        vals.append(float(pair[1]))
                    except (TypeError, ValueError):
                        pass
        row["samples"] = len(vals)
        row["has_data"] = len(vals) > 0
        if vals:
            v = _variance(vals)
            row["variance"] = v
            if v == 0.0 and len(vals) > 1:
                row["error"] = "valores constantes no intervalo (variância 0)"
                all_ok = False
            elif len(vals) == 1:
                row["error"] = "apenas 1 amostra — não dá para avaliar variância"
                all_ok = False
        else:
            row["error"] = "sem amostras no query_range"
            all_ok = False
        rows.append(row)

    return all_ok, rows


def phase2_submit(backend_url: str, scenarios: List[str]) -> List[Dict[str, Any]]:
    backend = backend_url.rstrip("/")
    out: List[Dict[str, Any]] = []
    payload_base = {
        "template_id": "urllc-template-001",
        "tenant_id": "default",
        "form_values": {
            "type": "URLLC",
            "latency": 10,
            "reliability": 99.99,
            "availability": 99.99,
            "throughput_dl": 100,
            "throughput_ul": 50,
            "device_count": 10,
            "coverage_area": "urban",
            "mobility": "low",
            "duration": 3600,
            "priority": "high",
        },
    }

    for scenario in scenarios:
        body = json.loads(json.dumps(payload_base))
        body["form_values"]["scenario"] = scenario
        row: Dict[str, Any] = {
            "scenario": scenario,
            "ok": False,
            "status_code": None,
            "telemetry_snapshot": None,
            "execution_id": None,
            "decision": None,
            "ml_risk_score": None,
            "error": None,
        }
        try:
            code, payload = _http_post_json(f"{backend}/api/v1/sla/submit", body, timeout=120.0)
            row["status_code"] = code
            if code != 200:
                row["error"] = str(payload)[:500]
                out.append(row)
                continue
            if not isinstance(payload, dict):
                row["error"] = "resposta não-JSON"
                out.append(row)
                continue
            js = payload
            md = js.get("metadata") or {}
            row["telemetry_snapshot"] = md.get("telemetry_snapshot")
            row["execution_id"] = md.get("execution_id")
            row["decision"] = js.get("decision")
            row["ml_risk_score"] = md.get("ml_risk_score")
            row["ok"] = True
        except Exception as e:
            row["error"] = str(e)
        out.append(row)
        time.sleep(0.5)
    return out


def _snapshot_metrics(
    snap: Optional[Dict[str, Any]]
) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[float], Optional[float]]:
    if not snap:
        return None, None, None, None, None
    ran = snap.get("ran") or {}
    tr = snap.get("transport") or {}
    core = snap.get("core") or {}
    return (
        ran.get("prb_utilization"),
        tr.get("jitter"),
        tr.get("rtt"),
        core.get("cpu"),
        core.get("memory"),
    )


def phase4_write_dataset(rows: List[Dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "execution_id",
        "decision",
        "ml_risk_score",
        "ran_prb",
        "transport_jitter",
        "transport_rtt",
        "core_cpu",
        "core_memory",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            if not r.get("ok"):
                continue
            snap = r.get("telemetry_snapshot") or {}
            prb, jitter, rtt, cpu, memory = _snapshot_metrics(snap if isinstance(snap, dict) else None)
            w.writerow(
                {
                    "execution_id": r.get("execution_id") or "",
                    "decision": r.get("decision") or "",
                    "ml_risk_score": r.get("ml_risk_score") if r.get("ml_risk_score") is not None else "",
                    "ran_prb": "" if prb is None else prb,
                    "transport_jitter": "" if jitter is None else jitter,
                    "transport_rtt": "" if rtt is None else rtt,
                    "core_cpu": "" if cpu is None else cpu,
                    "core_memory": "" if memory is None else memory,
                }
            )


def phase5_sanity(path: Path) -> Dict[str, Any]:
    if not path.is_file():
        return {"error": "CSV não encontrado"}
    rows: List[Dict[str, str]] = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append(row)
    if len(rows) < 2:
        return {"n_rows": len(rows), "ok": False, "note": "precisa ≥2 linhas para variância/correlação"}

    def col_float(name: str) -> List[Optional[float]]:
        out: List[Optional[float]] = []
        for r in rows:
            v = r.get(name, "").strip()
            if v == "":
                out.append(None)
            else:
                try:
                    out.append(float(v))
                except ValueError:
                    out.append(None)
        return out

    numeric_cols = [
        "ran_prb",
        "transport_jitter",
        "transport_rtt",
        "core_cpu",
        "core_memory",
        "ml_risk_score",
    ]
    report: Dict[str, Any] = {"n_rows": len(rows), "columns": {}}
    all_constant = True
    for c in numeric_cols:
        vals = [x for x in col_float(c) if x is not None]
        if len(vals) < 2:
            report["columns"][c] = {"variance": None, "note": "poucos valores"}
            continue
        v = _variance(vals)
        report["columns"][c] = {"variance": v, "non_null": len(vals)}
        if v > 0:
            all_constant = False

    # decisão: ACCEPT=1 REJECT=0 RENEGOTIATE=0.5
    def dec_y(s: str) -> Optional[float]:
        u = (s or "").upper()
        if u == "ACCEPT":
            return 1.0
        if u == "REJECT":
            return 0.0
        if u == "RENEGOTIATE":
            return 0.5
        return None

    ys = [dec_y(r.get("decision", "")) for r in rows]
    for c in ["ran_prb", "transport_jitter", "transport_rtt", "core_cpu", "core_memory"]:
        xs = col_float(c)
        pairs = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
        if len(pairs) >= 2:
            px, py = zip(*pairs)
            report["columns"][c]["corr_decision"] = _pearson(list(px), list(py))

    report["all_numeric_constant"] = all_constant
    report["ok"] = not all_constant and len(rows) >= 2
    return report


def main() -> int:
    ap = argparse.ArgumentParser(description="Validar telemetria TriSLA (Prometheus + submit)")
    ap.add_argument("--backend-url", default=os.getenv("BACKEND_URL", "http://localhost:8001"))
    ap.add_argument("--output-csv", type=Path, default=DEFAULT_CSV)
    ap.add_argument("--skip-phase1", action="store_true")
    ap.add_argument("--skip-phase2", action="store_true", help="não chama backend (só FASE 5 em CSV existente)")
    args = ap.parse_args()

    print("=== FASE 1 — Prometheus (query_range 5m, step 15s) ===\n")
    p1_ok = True
    p1_rows: List[Dict[str, Any]] = []
    if not args.skip_phase1:
        p1_ok, p1_rows = phase1_prometheus()
        for r in p1_rows:
            line = f"  {r['suffix']}: configured={r['configured']} samples={r['samples']}"
            if r.get("variance") is not None:
                line += f" variance={r['variance']:.6g}"
            if r.get("error"):
                line += f" | {r['error']}"
            print(line)
        print(f"\nFASE 1 resultado: {'OK' if p1_ok else 'FALHOU — ajustar queries'}\n")
    else:
        print("  (pulado)\n")

    submit_rows: List[Dict[str, Any]] = []
    if not args.skip_phase2:
        print("=== FASE 2 e 3 — Submit (3 cenários) + inspeção snapshot ===\n")
        scenarios = ["baixa_carga", "media_carga", "alta_carga"]
        submit_rows = phase2_submit(args.backend_url, scenarios)
        for r in submit_rows:
            print(f"  cenário={r['scenario']} http={r.get('status_code')} ok={r.get('ok')}")
            if r.get("error"):
                print(f"    erro: {r['error'][:300]}")
            snap = r.get("telemetry_snapshot")
            if isinstance(snap, dict):
                prb, jitter, rtt, cpu, memory = _snapshot_metrics(snap)
                print(
                    f"    telemetry: prb={prb} jitter={jitter} rtt={rtt} cpu={cpu} memory={memory} execution_id={r.get('execution_id')}"
                )
            elif r.get("ok"):
                print("    telemetry_snapshot ausente ou inválido")
        print()
    else:
        print("=== FASE 2/3 — pulado ===\n")

    if submit_rows:
        print("=== FASE 4 — dataset ===\n")
        phase4_write_dataset(submit_rows, args.output_csv)
        print(f"  escrito: {args.output_csv}\n")

    print("=== FASE 5 — sanity check ===\n")
    rep = phase5_sanity(args.output_csv)
    print(json.dumps(rep, indent=2, ensure_ascii=False))

    # Critério global
    if args.skip_phase1:
        p1_eval = True  # não avaliado nesta execução
    else:
        p1_eval = p1_ok
    valid = p1_eval and any(r.get("ok") for r in submit_rows) if submit_rows else False
    if submit_rows:
        non_null_any = False
        for r in submit_rows:
            if not r.get("ok"):
                continue
            prb, jitter, rtt, cpu, memory = _snapshot_metrics(
                r.get("telemetry_snapshot") if isinstance(r.get("telemetry_snapshot"), dict) else None
            )
            if prb is not None or jitter is not None or rtt is not None or cpu is not None or memory is not None:
                non_null_any = True
        if not non_null_any:
            valid = False

    print("\n=== CRITÉRIO ===")
    if args.skip_phase2 and not submit_rows:
        print("TELEMETRY: execução parcial (sem FASE 2). Configure backend e rode sem --skip-phase2.")
        return 1
    print("TELEMETRY VALID" if valid else "TELEMETRY NÃO VALID — ajustar Prometheus e/ou queries")
    return 0 if valid else 1


if __name__ == "__main__":
    sys.exit(main())
