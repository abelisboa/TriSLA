#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste oficial do modelo ML-NSMF v3.7.0
Gera:
  - tabela CLI
  - resultados em CSV
  - resultados em JSON
  - relatório TXT idêntico ao terminal
"""

from pathlib import Path
import json
import pandas as pd
import numpy as np
import joblib


# ================================================================
# 1. Carregamento do modelo e metadados
# ================================================================
def load_model():
    model_dir = Path("apps/ml-nsmf/models")

    rf = joblib.load(model_dir / "viability_model.pkl")
    scaler = joblib.load(model_dir / "scaler.pkl")

    meta = json.loads((model_dir / "model_metadata.json").read_text())

    return rf, scaler, meta


# ================================================================
# 2. Criação dos cenários sintéticos (URLLC / eMBB / mMTC)
# ================================================================
def build_scenarios():
    data = [
        # URLLC — latência ultra-baixa, jitter mínimo, loss quase zero
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
            active_slices_count=5,
            slice_type_encoded=0,
        ),

        # eMBB — alta banda, baixa perda, jitter moderado
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
            active_slices_count=12,
            slice_type_encoded=1,
        ),

        # mMTC — grande densidade, baixa banda, latência mais alta
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
            active_slices_count=120,
            slice_type_encoded=2,
        )
    ]

    df = pd.DataFrame(data)

    # Features derivadas (iguais ao notebook)
    df["latency_throughput_ratio"] = df["latency"] / (df["throughput"] + 1e-9)
    df["reliability_packet_loss_ratio"] = df["reliability"] / (df["packet_loss"] + 1e-9)
    df["jitter_latency_ratio"] = df["jitter"] / (df["latency"] + 1e-9)

    return df


# ================================================================
# 3. Formatação CLI corrigida (sem erros)
# ================================================================
def pretty_print_results(df, predictions):
    print("\n" + "=" * 120)
    print(f"{'Cenário':<35} {'Tipo':<10} {'Lat(ms)':>8} {'Thr(Mbps)':>10} "
          f"{'Rel':>8} {'Jitt(ms)':>10} {'Ploss':>12} {'Score':>10}")
    print("=" * 120)

    lines = []

    for i in range(len(df)):
        name = str(df.loc[i, "name"])
        slice_type = str(df.loc[i, "slice_type"])

        latency = float(df.loc[i, "latency"])
        throughput = float(df.loc[i, "throughput"])
        reliability = float(df.loc[i, "reliability"])
        jitter = float(df.loc[i, "jitter"])
        packet_loss = float(df.loc[i, "packet_loss"])

        score = float(predictions[i])

        line = (
            f"{name:<35} "
            f"{slice_type:<10} "
            f"{latency:8.2f} "
            f"{throughput:10.2f} "
            f"{reliability:8.3f} "
            f"{jitter:10.2f} "
            f"{packet_loss:12.5f} "
            f"{score:10.4f}"
        )
        print(line)
        lines.append(line)

    print("=" * 120)
    return "\n".join(lines)


# ================================================================
# 4. Exportação dos resultados
# ================================================================
def export_results(df, predictions, cli_table_text):
    out_dir = Path("analysis/results")
    out_dir.mkdir(parents=True, exist_ok=True)

    df_out = df.copy()
    df_out["viability_score"] = predictions

    # CSV
    df_out.to_csv(out_dir / "ml_nsmf_test_results_v3_7_0.csv", index=False)

    # JSON
    df_out.to_json(out_dir / "ml_nsmf_test_results_v3_7_0.json", orient="records", indent=2)

    # TXT CLI table
    (out_dir / "ml_nsmf_test_results_v3_7_0.txt").write_text(cli_table_text)

    print("\nArquivos exportados para:", out_dir.resolve())


# ================================================================
# 5. Execução principal
# ================================================================
def main():
    rf, scaler, meta = load_model()

    print("\n=== Resumo do modelo ML-NSMF v3.7.0 ===")
    print("Tipo de modelo:", meta["model_type"])
    print("Features:", len(meta["feature_columns"]), meta["feature_columns"])

    print("\nMétricas de treino/teste:")
    h = meta["training_history"]
    print("  Train R²:", h["train_r2"])
    print("  Test  R²:", h["test_r2"])
    print("  Train MAE:", h["train_mae"])
    print("  Test  MAE:", h["test_mae"])
    print("  CV mean R²:", h["cv_mean"])
    print("  CV std  R²:", h["cv_std"])
    print("  Timestamp treino:", h["timestamp"])

    # Construção dos cenários
    df = build_scenarios()

    # Ordenação das colunas exatamente como o modelo espera
    X = df[meta["feature_columns"]].values

    # Normalização
    X_scaled = scaler.transform(X)

    # Predição
    predictions = rf.predict(X_scaled)

    # CLI table
    cli_text = pretty_print_results(df, predictions)

    # Exportação
    export_results(df, predictions, cli_text)

    print("\nTeste concluído com sucesso.")


if __name__ == "__main__":
    main()
