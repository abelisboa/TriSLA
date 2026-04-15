#!/usr/bin/env python3
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, pstdev


VALID_DECISIONS = {"ACCEPT", "RENEGOTIATE", "REJECT", "UNKNOWN"}
SCIENTIFIC_DECISIONS = {"ACCEPT", "RENEGOTIATE", "REJECT"}


def fnum(v):
    if v is None or v == "":
        return None
    try:
        return float(v)
    except Exception:
        return None


def normalize_decision(v):
    if v is None:
        return None
    s = str(v).strip().upper()
    return s if s in VALID_DECISIONS else None


def parse_json_field(raw):
    if not isinstance(raw, str) or not raw.strip():
        return None, False
    try:
        return json.loads(raw), True
    except Exception:
        return None, False


def classify_request(row):
    timeout = str(row.get("timeout", "")).strip() in {"1", "1.0", "true", "True"}
    http_status = int(fnum(row.get("http_status")) or 0)
    err = str(row.get("error") or "").strip()
    response_raw = row.get("response_json")
    parsed_json, json_valid = parse_json_field(response_raw)
    response_received = bool(http_status > 0 or (isinstance(response_raw, str) and response_raw.strip()))

    decision_from_json = None
    decision_field_present = False
    if isinstance(parsed_json, dict) and "decision" in parsed_json:
        decision_field_present = True
        decision_from_json = parsed_json.get("decision")

    decision_value_raw = decision_from_json if decision_field_present else row.get("decision")
    decision_value_normalized = normalize_decision(decision_value_raw)

    # Request status taxonomy (operational)
    if timeout:
        request_status = "TIMEOUT"
        failure_reason = "timeout"
    elif http_status >= 400:
        request_status = "HTTP_ERROR"
        failure_reason = "http_error"
    elif not response_received:
        request_status = "EMPTY_RESPONSE"
        failure_reason = "empty_body"
    elif not json_valid:
        request_status = "JSON_PARSE_ERROR"
        failure_reason = "invalid_json"
    elif not decision_field_present:
        request_status = "SUCCESS"
        failure_reason = "missing_decision_field"
        decision_value_normalized = None
    elif decision_value_normalized is None:
        request_status = "SUCCESS"
        failure_reason = "missing_decision_field"
    else:
        request_status = "SUCCESS"
        failure_reason = "none"

    # Only keep normalized decision when structurally valid.
    if not (
        request_status == "SUCCESS"
        and json_valid
        and decision_field_present
        and decision_value_normalized in VALID_DECISIONS
    ):
        decision_value_normalized = None

    return {
        "request_status": request_status,
        "http_status_code": http_status,
        "response_received": response_received,
        "response_json_valid": json_valid,
        "decision_field_present": decision_field_present,
        "decision_value_raw": decision_value_raw,
        "decision_value_normalized": decision_value_normalized,
        "collection_failure_reason": failure_reason,
    }


def main():
    base = Path("/home/porvir5g/gtp5g/trisla/evidencias_resultados_article1_final_IEEE_LEVEL/raw")
    src = base / "raw_dataset_v2.csv"
    out_qualified = base / "raw_dataset_v3_qualified.csv"
    out_scientific = base / "raw_dataset_v3_scientific.csv"
    out_unknown_report = base / "unknown_causality_report.md"
    out_manifest = base / "DATASET_QUALITY_MANIFEST.json"

    rows = list(csv.DictReader(src.open(newline="", encoding="utf-8")))
    if not rows:
        raise SystemExit("No rows in raw_dataset_v2.csv")

    qualified = []
    old_unknown = 0
    failure_counts = Counter()
    request_status_counts = Counter()
    valid_backend_decisions = Counter()
    profile_counts = Counter()

    for row in rows:
        q = classify_request(row)
        merged = dict(row)
        merged.update(q)
        qualified.append(merged)

        if str(row.get("decision") or "").strip().upper() == "UNKNOWN":
            old_unknown += 1
        request_status_counts[q["request_status"]] += 1
        failure_counts[q["collection_failure_reason"]] += 1
        if q["decision_value_normalized"] in VALID_DECISIONS:
            valid_backend_decisions[q["decision_value_normalized"]] += 1
        profile_counts[str(row.get("profile") or "").strip().lower() or "unlabeled"] += 1

    # Scientific dataset: only real valid decisions.
    scientific = [
        r
        for r in qualified
        if r["request_status"] == "SUCCESS"
        and str(r["response_json_valid"]).lower() in {"true", "1"}
        and str(r["decision_field_present"]).lower() in {"true", "1"}
        and (r["decision_value_normalized"] in SCIENTIFIC_DECISIONS)
    ]

    # ML gate on scientific dataset.
    risks = [fnum(r.get("ml_risk_score")) for r in scientific]
    risks = [v for v in risks if v is not None]
    by_decision = defaultdict(list)
    for r in scientific:
        d = r["decision_value_normalized"]
        v = fnum(r.get("ml_risk_score"))
        if d in SCIENTIFIC_DECISIONS and v is not None:
            by_decision[d].append(v)

    unique_risk = len(set(round(v, 10) for v in risks)) if risks else 0
    std_risk = pstdev(risks) if len(risks) > 1 else 0.0
    classes_present = [d for d in ("ACCEPT", "RENEGOTIATE", "REJECT") if len(by_decision[d]) > 0]
    means = {d: mean(vs) for d, vs in by_decision.items() if vs}

    if unique_risk > 10 and std_risk > 0 and len(classes_present) >= 3:
        ml_status = "ML_VALIDATED_FOR_PAPER"
    elif unique_risk > 3 and std_risk > 0 and len(classes_present) >= 2:
        ml_status = "PARTIAL_ML_SIGNAL"
    else:
        ml_status = "CRITICAL_FAILURE_ML_NOT_PROVEN"

    # Write datasets
    qualified_fields = list(qualified[0].keys())
    with out_qualified.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=qualified_fields)
        w.writeheader()
        w.writerows(qualified)

    if scientific:
        with out_scientific.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(scientific[0].keys()))
            w.writeheader()
            w.writerows(scientific)
    else:
        out_scientific.write_text("", encoding="utf-8")

    # Unknown causality report
    report = []
    report.append("# UNKNOWN Causality Report")
    report.append("")
    report.append(f"- Source dataset: `{src}`")
    report.append(f"- Total rows: **{len(rows)}**")
    report.append(f"- Rows previously labeled UNKNOWN: **{old_unknown}**")
    report.append("")
    report.append("## Reclassification (absolute and percentage)")
    for k in ["timeout", "http_error", "missing_decision_field", "empty_body", "invalid_json", "connection_error", "none"]:
        c = failure_counts.get(k, 0)
        pct = (c / len(rows)) * 100.0 if rows else 0.0
        report.append(f"- {k}: {c} ({pct:.2f}%)")
    report.append("")
    report.append("## Valid backend decisions observed")
    for d in ["ACCEPT", "RENEGOTIATE", "REJECT", "UNKNOWN"]:
        c = valid_backend_decisions.get(d, 0)
        pct = (c / len(rows)) * 100.0 if rows else 0.0
        report.append(f"- {d}: {c} ({pct:.2f}%)")
    report.append("")
    report.append("## Scientific dataset summary")
    report.append(f"- Scientific rows: **{len(scientific)}**")
    report.append(f"- ml_risk_score.nunique: **{unique_risk}**")
    report.append(f"- ml_risk_score.std: **{std_risk:.6f}**")
    report.append(f"- Classes present: **{', '.join(classes_present) if classes_present else 'none'}**")
    out_unknown_report.write_text("\n".join(report) + "\n", encoding="utf-8")

    manifest = {
        "datasets": [
            {
                "name": "raw_dataset_v2.csv",
                "origin": str(src),
                "filter_applied": "none",
                "total_requests": len(rows),
                "valid_responses": int(request_status_counts.get("SUCCESS", 0)),
                "failures_by_category": dict(failure_counts),
                "valid_decisions_by_class": dict(valid_backend_decisions),
                "scientific_status": "SOURCE_DATASET",
            },
            {
                "name": "raw_dataset_v3_qualified.csv",
                "origin": str(out_qualified),
                "filter_applied": "operational taxonomy + decision normalization",
                "total_requests": len(qualified),
                "valid_responses": int(sum(1 for r in qualified if r["decision_value_normalized"] is not None)),
                "failures_by_category": dict(failure_counts),
                "valid_decisions_by_class": dict(valid_backend_decisions),
                "scientific_status": "QUALIFIED",
            },
            {
                "name": "raw_dataset_v3_scientific.csv",
                "origin": str(out_scientific),
                "filter_applied": "SUCCESS + valid JSON + decision present + decision in ACCEPT/RENEGOTIATE/REJECT",
                "total_requests": len(scientific),
                "valid_responses": len(scientific),
                "failures_by_category": {},
                "valid_decisions_by_class": {
                    k: len(v) for k, v in by_decision.items()
                },
                "scientific_status": ml_status,
                "ml_gate": {
                    "ml_risk_score_nunique": unique_risk,
                    "ml_risk_score_std": std_risk,
                    "classes_present": classes_present,
                    "mean_by_decision": means,
                },
            },
        ]
    }
    out_manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    print(
        json.dumps(
            {
                "qualified_dataset": str(out_qualified),
                "scientific_dataset": str(out_scientific),
                "unknown_report": str(out_unknown_report),
                "quality_manifest": str(out_manifest),
                "ml_status": ml_status,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
