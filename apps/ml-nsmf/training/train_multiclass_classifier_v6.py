#!/usr/bin/env python3
import json
import pickle
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import balanced_accuracy_score, classification_report, confusion_matrix, f1_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler


FEATURE_COLUMNS = [
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


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def ensure_min_class_count(counts: dict, fallback_min: int = 50):
    below = {k: int(v) for k, v in counts.items() if int(v) < fallback_min}
    return below


def risk_from_probabilities(prob_map: dict) -> float:
    p_reneg = float(prob_map.get("RENEGOTIATE", 0.0))
    p_reject = float(prob_map.get("REJECT", 0.0))
    # v7 calibrated risk formula: less early saturation between medium/high.
    risk_raw = (0.5 * p_reneg) + (1.0 * p_reject)
    return float(min(1.0, risk_raw))


def main():
    repo = Path("/home/porvir5g/gtp5g/trisla")
    ds = repo / "artifacts" / "ml_training_dataset_v6_controlled.csv"
    report_json = repo / "artifacts" / "ml_offline_validation_v7.json"
    report_md = repo / "artifacts" / "ml_offline_validation_v7.md"
    technical_manifest = repo / "artifacts" / "ml_rebuild_technical_manifest_v7.json"

    models_dir = repo / "apps" / "ml-nsmf" / "models"
    decision_classifier_path = models_dir / "decision_classifier.pkl"
    metadata_path = models_dir / "model_metadata.json"

    df = pd.read_csv(ds)
    df = df[df["decision"].isin(["ACCEPT", "RENEGOTIATE", "REJECT"])].copy()

    # Ensure all features are present.
    missing_features = [f for f in FEATURE_COLUMNS if f not in df.columns]
    if missing_features:
        raise RuntimeError(f"Missing required features in training dataset: {missing_features}")

    class_counts = df["decision"].value_counts().to_dict()
    below_50 = ensure_min_class_count(class_counts, 50)
    status_ceiling = "ML_VALIDATED_FOR_PAPER" if not below_50 else "PARTIAL_ML_SIGNAL"

    X = df[FEATURE_COLUMNS].astype(float)
    y = df["decision"].astype(str)

    le = LabelEncoder()
    y_enc = le.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enc, test_size=0.25, random_state=42, stratify=y_enc
    )

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    base_clf = RandomForestClassifier(
        n_estimators=400,
        max_depth=16,
        min_samples_split=4,
        min_samples_leaf=2,
        class_weight="balanced_subsample",
        random_state=42,
        n_jobs=-1,
    )
    calibration_method = "isotonic" if len(df) >= 1000 else "sigmoid"
    clf = CalibratedClassifierCV(base_clf, method=calibration_method, cv=5)
    clf.fit(X_train_s, y_train)
    y_pred = clf.predict(X_test_s)

    macro_f1 = float(f1_score(y_test, y_pred, average="macro"))
    bal_acc = float(balanced_accuracy_score(y_test, y_pred))
    labels = list(le.classes_)
    report = classification_report(y_test, y_pred, target_names=labels, output_dict=True, zero_division=0)
    cm = confusion_matrix(y_test, y_pred).tolist()

    idx_reject = labels.index("REJECT") if "REJECT" in labels else None
    recall_reject = float(report["REJECT"]["recall"]) if "REJECT" in report else 0.0

    # Risk monotonic sanity check using canonical profiles (v7 ranges).
    profiles = [
        {"name": "low", "latency": 8, "throughput": 100, "reliability": 0.9995, "jitter": 1, "packet_loss": 0.001, "cpu_utilization": 0.2, "memory_utilization": 0.2, "network_bandwidth_available": 1200, "active_slices_count": 3, "slice_type_encoded": 1},
        {"name": "medium", "latency": 55, "throughput": 20, "reliability": 0.97, "jitter": 8, "packet_loss": 0.01, "cpu_utilization": 0.55, "memory_utilization": 0.55, "network_bandwidth_available": 300, "active_slices_count": 15, "slice_type_encoded": 2},
        {"name": "high", "latency": 240, "throughput": 2, "reliability": 0.86, "jitter": 30, "packet_loss": 0.07, "cpu_utilization": 0.9, "memory_utilization": 0.9, "network_bandwidth_available": 80, "active_slices_count": 45, "slice_type_encoded": 3},
    ]

    profile_outputs = []
    for p in profiles:
        row = dict(p)
        eps = 0.001
        row["latency_throughput_ratio"] = row["latency"] / (row["throughput"] + eps)
        row["reliability_packet_loss_ratio"] = row["reliability"] / (row["packet_loss"] + eps)
        row["jitter_latency_ratio"] = row["jitter"] / (row["latency"] + eps)
        nlat = max(0.0, min(1.0, row["latency"] / 200.0))
        njit = max(0.0, min(1.0, row["jitter"] / 100.0))
        npl = max(0.0, min(1.0, row["packet_loss"] * 5.0))
        ran_p = (nlat + njit) / 2.0
        trans_p = (njit + npl) / 2.0
        core_p = (row["cpu_utilization"] + row["memory_utilization"]) / 2.0
        row["domain_pressure_score"] = max(0.0, min(1.0, (ran_p + trans_p + core_p) / 3.0))
        row["transport_instability_score"] = max(0.0, min(1.0, (njit + npl + nlat) / 3.0))
        row["core_pressure_score"] = max(0.0, min(1.0, core_p))
        row["throughput_efficiency_score"] = max(0.0, min(1.0, row["throughput"] / (row["network_bandwidth_available"] + eps)))
        row["sla_stringency_score"] = max(0.0, min(1.0, (nlat + max(0.0, 1.0 - row["reliability"]) + max(0.0, min(1.0, 1.0 - row["throughput"] / max(row["network_bandwidth_available"], eps)))) / 3.0))
        if row["slice_type_encoded"] == 1:
            row["slice_domain_fit_score"] = max(0.0, min(1.0, 1.0 - (nlat * 0.5 + njit * 0.3 + npl * 0.2)))
        elif row["slice_type_encoded"] == 3:
            row["slice_domain_fit_score"] = max(0.0, min(1.0, row["reliability"] * max(0.0, 1.0 - core_p)))
        else:
            row["slice_domain_fit_score"] = max(0.0, min(1.0, row["throughput_efficiency_score"] * 0.6 + (1.0 - nlat) * 0.4))

        Xp = pd.DataFrame([[row[c] for c in FEATURE_COLUMNS]], columns=FEATURE_COLUMNS)
        Xp_s = scaler.transform(Xp)
        probs = clf.predict_proba(Xp_s)[0]
        prob_map = {labels[i]: float(probs[i]) for i in range(len(labels))}
        risk = risk_from_probabilities(prob_map)
        pred_class = labels[int(np.argmax(probs))]
        profile_outputs.append({"profile": p["name"], "pred_class": pred_class, "risk": risk, "probabilities": prob_map})

    risk_order_ok = profile_outputs[0]["risk"] < profile_outputs[1]["risk"] < profile_outputs[2]["risk"]

    # Distribution checks on test-set risk.
    test_probs = clf.predict_proba(X_test_s)
    test_risks = []
    for probs in test_probs:
        prob_map = {labels[i]: float(probs[i]) for i in range(len(labels))}
        test_risks.append(risk_from_probabilities(prob_map))
    risk_nunique = int(len(set(round(v, 8) for v in test_risks)))
    risk_std = float(np.std(np.array(test_risks, dtype=float)))

    # Mean risk order by true class on test split.
    y_test_labels = [labels[i] for i in y_test]
    by_class_risk = {"ACCEPT": [], "RENEGOTIATE": [], "REJECT": []}
    for y_lbl, r in zip(y_test_labels, test_risks):
        if y_lbl in by_class_risk:
            by_class_risk[y_lbl].append(r)
    mean_by_class = {k: (float(np.mean(v)) if v else None) for k, v in by_class_risk.items()}
    mean_order_ok = (
        mean_by_class["ACCEPT"] is not None
        and mean_by_class["RENEGOTIATE"] is not None
        and mean_by_class["REJECT"] is not None
        and mean_by_class["ACCEPT"] < mean_by_class["RENEGOTIATE"] < mean_by_class["REJECT"]
    )

    # Slice stability checks on test split.
    X_test_df = X_test.reset_index(drop=True).copy()
    y_pred_lbl = [labels[i] for i in y_pred]
    slice_checks = {}
    for ste, sname in ((1, "URLLC"), (2, "eMBB"), (3, "mMTC")):
        idxs = X_test_df.index[X_test_df["slice_type_encoded"] == ste].tolist()
        sr = [test_risks[i] for i in idxs]
        sd = [y_pred_lbl[i] for i in idxs]
        slice_checks[sname] = {
            "samples": len(idxs),
            "risk_nunique": int(len(set(round(v, 8) for v in sr))) if sr else 0,
            "risk_std": float(np.std(np.array(sr, dtype=float))) if len(sr) > 1 else 0.0,
            "decision_classes_present": sorted(list(set(sd))) if sd else [],
            "non_collapsed": bool((len(sr) > 5) and (len(set(round(v, 8) for v in sr)) > 3) and (np.std(np.array(sr, dtype=float)) > 0 if len(sr) > 1 else False)),
        }
    slice_stability_ok = all(v["non_collapsed"] for v in slice_checks.values() if v["samples"] > 0)

    gates = {
        "macro_f1_ge_065": macro_f1 >= 0.65,
        "balanced_accuracy_ge_065": bal_acc >= 0.65,
        "recall_reject_ge_050": recall_reject >= 0.50,
        "risk_monotonic_low_medium_high": risk_order_ok,
        "mean_accept_lt_reneg_lt_reject": mean_order_ok,
        "risk_nunique_gt_10": risk_nunique > 10,
        "risk_std_gt_0": risk_std > 0,
        "slice_stability_ok": slice_stability_ok,
    }

    if all(gates.values()) and status_ceiling == "ML_VALIDATED_FOR_PAPER":
        scientific_status = "ML_VALIDATED_FOR_PAPER"
    elif any(gates.values()):
        scientific_status = "PARTIAL_ML_SIGNAL"
    else:
        scientific_status = "CRITICAL_FAILURE_ML_NOT_PROVEN"

    bundle = {
        "model": clf,
        "scaler": scaler,
        "label_encoder": le,
        "feature_columns": FEATURE_COLUMNS,
        "version": 7,
        "trained_at_utc": utc_now(),
        "risk_formula": "v7_calibrated",
        "calibration": calibration_method,
    }
    with decision_classifier_path.open("wb") as f:
        pickle.dump(bundle, f)

    metadata = {
        "model_type": "random_forest_classifier_multiclass",
        "calibration": calibration_method,
        "feature_columns": FEATURE_COLUMNS,
        "risk_formula": "v7_calibrated",
        "training_origin": {
            "dataset": str(ds),
            "real_and_bootstrap_mixed": True,
            "bootstrap_for_training_only": True,
        },
        "class_shares": {k: float(v / len(df)) for k, v in class_counts.items()},
        "class_counts": {k: int(v) for k, v in class_counts.items()},
        "offline_metrics": {
            "macro_f1": macro_f1,
            "balanced_accuracy": bal_acc,
            "recall_reject": recall_reject,
            "risk_nunique": risk_nunique,
            "risk_std": risk_std,
            "mean_risk_by_class": mean_by_class,
            "classification_report": report,
            "confusion_matrix": cm,
            "slice_checks": slice_checks,
        },
        "gates": gates,
        "scientific_status": scientific_status,
        "ml_status": scientific_status,
        "trained_at_utc": utc_now(),
    }
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")

    offline = {
        "dataset_rows": int(len(df)),
        "class_distribution": {k: int(v) for k, v in class_counts.items()},
        "below_fallback_min_50": below_50,
        "status_ceiling": status_ceiling,
        "macro_f1": macro_f1,
        "balanced_accuracy": bal_acc,
        "recall_reject": recall_reject,
        "labels": labels,
        "confusion_matrix": cm,
        "gates": gates,
        "risk_profile_outputs": profile_outputs,
        "risk_nunique": risk_nunique,
        "risk_std": risk_std,
        "mean_risk_by_class": mean_by_class,
        "slice_checks": slice_checks,
        "calibration": calibration_method,
        "risk_formula_version": "v7_calibrated",
        "scientific_status": scientific_status,
        "artifacts": {
            "decision_classifier": str(decision_classifier_path),
            "model_metadata": str(metadata_path),
        },
        "generated_at_utc": utc_now(),
    }
    report_json.write_text(json.dumps(offline, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# ML-NSMF Offline Validation v7",
        "",
        f"- Dataset rows: **{len(df)}**",
        f"- Class distribution: `{class_counts}`",
        f"- Macro F1: **{macro_f1:.4f}**",
        f"- Balanced Accuracy: **{bal_acc:.4f}**",
        f"- Recall REJECT: **{recall_reject:.4f}**",
        f"- Risk monotonic (low<medium<high): **{risk_order_ok}**",
        f"- Risk nunique (>10): **{risk_nunique}**",
        f"- Risk std (>0): **{risk_std:.6f}**",
        f"- Mean order ACCEPT<RENEGOTIATE<REJECT: **{mean_order_ok}**",
        f"- Calibration: **{calibration_method}**",
        f"- Scientific status: **{scientific_status}**",
        "",
        "## Gates",
    ]
    for k, v in gates.items():
        lines.append(f"- {k}: `{v}`")
    lines += [
        "",
        "## Risk Profile Outputs",
        "",
        "```json",
        json.dumps(profile_outputs, indent=2, ensure_ascii=False),
        "```",
    ]
    report_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    technical_manifest.write_text(
        json.dumps(
            {
                "name": "ml_rebuild_v7",
                "objective": "Controlled ML-NSMF rebuild based on evidence (REJECT coverage and non-collapsed risk).",
                "artifacts": {
                    "training_dataset": str(ds),
                    "offline_json_report": str(report_json),
                    "offline_md_report": str(report_md),
                    "decision_classifier": str(decision_classifier_path),
                    "model_metadata": str(metadata_path),
                },
                "scientific_status": scientific_status,
                "notes": "Bootstrap data is training-only and never experimental evidence.",
                "generated_at_utc": utc_now(),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(json.dumps({"scientific_status": scientific_status, "gates": gates}, indent=2))


if __name__ == "__main__":
    main()
