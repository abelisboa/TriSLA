#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FASE N.2 — Validação local do predictor.py (ML-NSMF v3.7.0)

Esta versão foi ajustada para refletir fielmente a lógica real do predictor.py,
incluindo:
  - slice_type_encoded = {URLLC:1, eMBB:2, mMTC:3}
  - epsilon = 0.001
  - active_slices_count convertido para float
"""

from pathlib import Path
import json
import numpy as np
import pandas as pd
import joblib

# Import real predictor
from apps.ml_nsmf.src.predictor import RiskPredictor


# ================================================================
# 1. Criar instância real do predictor
# ================================================================
def build_predictor():
    return RiskPredictor()


# ================================================================
# 2. Carregar modelo e metadata
# ================================================================
def load_model_and_meta():
    model_dir = Path("apps/ml_nsmf/models")

    rf = joblib.load(model_dir / "viability_model.pkl")
    scaler = joblib.load(model_dir / "scaler.pkl")
    meta = json.loads((model_dir / "model_metadata.json").read_text())

    return rf, scaler, meta


# ================================================================
# 3. Cenários sintéticos
# ================================================================
def build_scenarios():
    data = [
        dict(
            name="URLLC_critico_realista",
            slice_type="URLLC",
            latency=0.8,
            throughput=20,
            reliability=0.999,
            jitter=0.10,
            packet_loss=0.0001,
            cpu_utilization=0.12,
            memory_utilization=0.18,
            network_bandwidth_available=150,
            active_slices_count=5.0,
        ),
        dict(
            name="eMBB_alto_trafego",
            slice_type="eMBB",
            latency=15,
            throughput=250,
            reliability=0.995,
            jitter=3.0,
            packet_loss=0.002,
            cpu_utilization=0.58,
            memory_utilization=0.61,
            network_bandwidth_available=500,
            active_slices_count=12.0,
        ),
        dict(
            name="mMTC_denso_100k_UEs",
            slice_type="mMTC",
            latency=40,
            throughput=1,
            reliability=0.98,
            jitter=12,
            packet_loss=0.01,
            cpu_utilization=0.37,
            memory_utilization=0.44,
            network_bandwidth_available=80,
            active_slices_count=120.0,
        )
    ]

    df = pd.DataFrame(data)

    # Usar epsilon real do predictor
    eps = 0.001

    df["latency_throughput_ratio"] = df["latency"] / (df["throughput"] + eps)
    df["reliability_packet_loss_ratio"] = df["reliability"] / (df["packet_loss"] + eps)
    df["jitter_latency_ratio"] = df["jitter"] / (df["latency"] + eps)

    # Encoding igual ao predictor
    df["slice_type_encoded"] = df["slice_type"].map({
        "URLLC": 1,
        "eMBB": 2,
        "mMTC": 3
    })

    return df


# ================================================================
# 4. Predição direta (modelo real)
# ================================================================
def predict_direct(rf, scaler, meta, df):
    X = df[meta["feature_columns"]].values
    X_scaled = scaler.transform(X)
    return rf.predict(X_scaled)


# ================================================================
# 5. Predição via predictor real
# ================================================================
def predict_via_predictor(df, predictor):
    scores = []

    import asyncio

    for i in range(len(df)):
        row = df.iloc[i]

        payload = {
            "latency": float(row["latency"]),
            "throughput": float(row["throughput"]),
            "reliability": float(row["reliability"]),
            "jitter": float(row["jitter"]),
            "packet_loss": float(row["packet_loss"]),
            "cpu_utilization": float(row["cpu_utilization"]),
            "memory_utilization": float(row["memory_utilization"]),
            "network_bandwidth_available": float(row["network_bandwidth_available"]),
            "active_slices_count": float(row["active_slices_count"]),
            "slice_type": row["slice_type"]
        }

        # predictor.normalize() é async
        norm = asyncio.run(predictor.normalize(payload))
        pred = asyncio.run(predictor.predict(norm))

        scores.append(pred["viability_score"])

    return np.array(scores)


# ================================================================
# 6. Impressão CLI
# ================================================================
def pretty_print(df, direct, pred):
    print("\n" + "="*140)
    print(
        f"{'Cenário':<30} {'Tipo':<6} "
        f"{'Score(Modelo)':>18} {'Score(Predictor)':>18} {'Dif.Abs':>12} {'Status':>10}"
    )
    print("="*140)

    for i in range(len(df)):
        d = float(direct[i])
        p = float(pred[i])
        diff = abs(d - p)

        status = "OK" if diff < 1e-6 else "DIVERGE"

        print(
            f"{df.loc[i,'name']:<30} {df.loc[i,'slice_type']:<6} "
            f"{d:18.6f} {p:18.6f} {diff:12.6f} {status:>10}"
        )

    print("="*140)


# ================================================================
# 7. Main
# ================================================================
def main():
    print("\n=== FASE N.2 — Validação do predictor.py ===")

    predictor = build_predictor()
    rf, scaler, meta = load_model_and_meta()
    df = build_scenarios()

    y_direct = predict_direct(rf, scaler, meta, df)
    y_pred = predict_via_predictor(df, predictor)

    pretty_print(df, y_direct, y_pred)

    print("\nFASE N.2 concluída — veja divergências na tabela.")


if __name__ == "__main__":
    main()
