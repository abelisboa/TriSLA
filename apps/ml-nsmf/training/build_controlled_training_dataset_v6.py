#!/usr/bin/env python3
import json
from pathlib import Path

import numpy as np
import pandas as pd


REQUIRED_FEATURES = [
    "latency",
    "throughput",
    "reliability",
    "jitter",
    "packet_loss",
    "cpu_utilization",
    "memory_utilization",
    "network_bandwidth_available",
    "active_slices_count",
    "slice_type_encoded",
    "latency_throughput_ratio",
    "reliability_packet_loss_ratio",
    "jitter_latency_ratio",
    "domain_pressure_score",
    "transport_instability_score",
    "core_pressure_score",
    "throughput_efficiency_score",
    "sla_stringency_score",
    "slice_domain_fit_score",
]


def pick_decision_column(df: pd.DataFrame) -> str:
    for candidate in ("decision", "decision_label", "predicted_decision_class"):
        if candidate in df.columns:
            return candidate
    raise RuntimeError("No decision label column found in source dataset")


def compute_derived(row: dict) -> dict:
    eps = 0.001
    latency = float(row["latency"])
    throughput = float(row["throughput"])
    reliability = float(row["reliability"])
    jitter = float(row["jitter"])
    packet_loss = float(row["packet_loss"])
    cpu = float(row["cpu_utilization"])
    mem = float(row["memory_utilization"])
    bw = float(row["network_bandwidth_available"])
    ste = int(row["slice_type_encoded"])

    nlat = max(0.0, min(1.0, latency / 200.0))
    njit = max(0.0, min(1.0, jitter / 100.0))
    npl = max(0.0, min(1.0, packet_loss * 5.0))
    ran_p = (nlat + njit) / 2.0
    trans_p = (njit + npl) / 2.0
    core_p = (cpu + mem) / 2.0
    domain_pressure = max(0.0, min(1.0, (ran_p + trans_p + core_p) / 3.0))
    transport_instability = max(0.0, min(1.0, (njit + npl + nlat) / 3.0))
    core_pressure = max(0.0, min(1.0, core_p))
    te = throughput / (bw + eps)
    throughput_eff = max(0.0, min(1.0, te))
    sla_stringency = max(
        0.0,
        min(1.0, (nlat + max(0.0, 1.0 - reliability) + max(0.0, min(1.0, 1.0 - throughput / max(bw, eps)))) / 3.0),
    )
    if ste == 1:
        fit = max(0.0, min(1.0, 1.0 - (nlat * 0.5 + njit * 0.3 + npl * 0.2)))
    elif ste == 3:
        fit = max(0.0, min(1.0, reliability * max(0.0, 1.0 - core_p)))
    else:
        fit = max(0.0, min(1.0, throughput_eff * 0.6 + (1.0 - nlat) * 0.4))

    row["latency_throughput_ratio"] = latency / (throughput + eps)
    row["reliability_packet_loss_ratio"] = reliability / (packet_loss + eps)
    row["jitter_latency_ratio"] = jitter / (latency + eps)
    row["domain_pressure_score"] = domain_pressure
    row["transport_instability_score"] = transport_instability
    row["core_pressure_score"] = core_pressure
    row["throughput_efficiency_score"] = throughput_eff
    row["sla_stringency_score"] = sla_stringency
    row["slice_domain_fit_score"] = fit
    return row


def bootstrap_row(label: str, rng: np.random.Generator) -> dict:
    if label == "ACCEPT":
        latency = rng.uniform(5, 18)
        reliability = rng.uniform(0.9991, 0.9999)
        throughput = rng.uniform(60, 220)
        jitter = rng.uniform(0.1, 2.0)
        packet_loss = rng.uniform(0.0001, 0.005)
        cpu = rng.uniform(0.1, 0.45)
        mem = rng.uniform(0.1, 0.45)
        bw = rng.uniform(500, 2500)
        active = int(rng.integers(1, 10))
        ste = int(rng.choice([1, 2]))
        viability = rng.uniform(0.80, 0.98)
    elif label == "RENEGOTIATE":
        latency = rng.uniform(25, 95)
        reliability = rng.uniform(0.952, 0.9989)
        throughput = rng.uniform(10, 80)
        jitter = rng.uniform(1.0, 15.0)
        packet_loss = rng.uniform(0.005, 0.03)
        cpu = rng.uniform(0.3, 0.75)
        mem = rng.uniform(0.3, 0.8)
        bw = rng.uniform(120, 1200)
        active = int(rng.integers(5, 30))
        ste = int(rng.choice([1, 2, 3]))
        viability = rng.uniform(0.45, 0.78)
    else:  # REJECT
        latency = rng.uniform(100, 260)
        reliability = rng.uniform(0.75, 0.95)
        throughput = rng.uniform(1, 25)
        jitter = rng.uniform(10.0, 45.0)
        packet_loss = rng.uniform(0.02, 0.12)
        cpu = rng.uniform(0.7, 0.98)
        mem = rng.uniform(0.7, 0.98)
        bw = rng.uniform(20, 300)
        active = int(rng.integers(20, 80))
        ste = int(rng.choice([1, 2, 3]))
        viability = rng.uniform(0.05, 0.40)

    row = {
        "latency": latency,
        "throughput": throughput,
        "reliability": reliability,
        "jitter": jitter,
        "packet_loss": packet_loss,
        "cpu_utilization": cpu,
        "memory_utilization": mem,
        "network_bandwidth_available": bw,
        "active_slices_count": active,
        "slice_type_encoded": ste,
        "decision": label,
        "viability_score": viability,
        "data_origin": "bootstrap_controlled",
    }
    return compute_derived(row)


def main():
    repo = Path("/home/porvir5g/gtp5g/trisla")
    src = repo / "artifacts" / "ml_training_dataset_v5.csv"
    out_csv = repo / "artifacts" / "ml_training_dataset_v6_controlled.csv"
    out_report = repo / "artifacts" / "ml_training_dataset_v6_report.json"

    df = pd.read_csv(src)
    decision_col = pick_decision_column(df)
    df["decision"] = df[decision_col].astype(str).str.upper().str.strip()
    df = df[df["decision"].isin(["ACCEPT", "RENEGOTIATE", "REJECT"])].copy()
    df["data_origin"] = "real_or_prior_controlled"

    # Keep only known feature columns when present.
    for col in REQUIRED_FEATURES:
        if col not in df.columns:
            df[col] = np.nan

    # Fill missing base fields from compatible aliases where available.
    if "devices" in df.columns and "active_slices_count" in df.columns:
        df["active_slices_count"] = df["active_slices_count"].fillna(df["devices"])

    # Generate missing derived fields row-wise when needed.
    prepared_rows = []
    for _, r in df.iterrows():
        row = r.to_dict()
        # Base defaults for sparse historical rows.
        row["latency"] = float(row.get("latency") if pd.notna(row.get("latency")) else 50.0)
        row["throughput"] = float(row.get("throughput") if pd.notna(row.get("throughput")) else 30.0)
        row["reliability"] = float(row.get("reliability") if pd.notna(row.get("reliability")) else 0.98)
        row["jitter"] = float(row.get("jitter") if pd.notna(row.get("jitter")) else 5.0)
        row["packet_loss"] = float(row.get("packet_loss") if pd.notna(row.get("packet_loss")) else 0.01)
        row["cpu_utilization"] = float(row.get("cpu_utilization") if pd.notna(row.get("cpu_utilization")) else 0.5)
        row["memory_utilization"] = float(row.get("memory_utilization") if pd.notna(row.get("memory_utilization")) else 0.5)
        row["network_bandwidth_available"] = float(
            row.get("network_bandwidth_available") if pd.notna(row.get("network_bandwidth_available")) else 500.0
        )
        row["active_slices_count"] = int(row.get("active_slices_count") if pd.notna(row.get("active_slices_count")) else 10)
        row["slice_type_encoded"] = int(row.get("slice_type_encoded") if pd.notna(row.get("slice_type_encoded")) else 2)
        row["viability_score"] = float(row.get("viability_score") if pd.notna(row.get("viability_score")) else 0.5)
        row = compute_derived(row)
        prepared_rows.append(row)

    base_df = pd.DataFrame(prepared_rows)
    counts = base_df["decision"].value_counts().to_dict()
    target_per_class = 200
    rng = np.random.default_rng(42)
    boot_rows = []
    for cls in ("ACCEPT", "RENEGOTIATE", "REJECT"):
        need = max(0, target_per_class - int(counts.get(cls, 0)))
        for _ in range(need):
            boot_rows.append(bootstrap_row(cls, rng))

    out_df = pd.concat([base_df, pd.DataFrame(boot_rows)], ignore_index=True)
    out_df = out_df.sample(frac=1.0, random_state=42).reset_index(drop=True)
    out_df.to_csv(out_csv, index=False)

    report = {
        "source_dataset": str(src),
        "output_dataset": str(out_csv),
        "rows_input": int(len(base_df)),
        "rows_bootstrap_added": int(len(boot_rows)),
        "rows_output": int(len(out_df)),
        "class_distribution_input": {k: int(v) for k, v in counts.items()},
        "class_distribution_output": {k: int(v) for k, v in out_df["decision"].value_counts().to_dict().items()},
        "target_per_class": target_per_class,
        "feature_columns": REQUIRED_FEATURES,
        "note": "Bootstrap rows are for training only; not for experimental evidence.",
    }
    out_report.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
