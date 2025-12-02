#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FASE 3.4 — Sensibilidade por feature (One-Factor-At-A-Time)
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import json
import asyncio
import matplotlib.pyplot as plt
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from apps.ml_nsmf.src.predictor import RiskPredictor

RESULTS_DIR = BASE_DIR / "analysis" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


async def test_feature_sensitivity(predictor, feature_name, min_val, max_val, n_points=50):
    """Testa sensibilidade de uma feature"""
    base_metrics = {
        "latency": 5.0,
        "throughput": 100,
        "reliability": 0.999,
        "jitter": 1.0,
        "packet_loss": 0.001,
        "cpu_utilization": 0.5,
        "memory_utilization": 0.5,
        "network_bandwidth_available": 500,
        "active_slices_count": 10,
        "slice_type": "eMBB"
    }
    
    values = np.linspace(min_val, max_val, n_points)
    scores = []
    
    for val in values:
        metrics = {**base_metrics, feature_name: float(val)}
        normalized = await predictor.normalize(metrics)
        prediction = await predictor.predict(normalized)
        scores.append(prediction.get("viability_score", None))
    
    return values, scores


def main():
    print("=" * 80)
    print("FASE 3.4 — SENSIBILIDADE POR FEATURE")
    print("=" * 80)
    print()
    
    predictor = RiskPredictor()
    if predictor.model is None:
        print("❌ ERRO: Modelo não carregado!")
        return 1
    
    print("✅ Predictor inicializado")
    print()
    
    # Features principais para testar
    features = [
        ("latency", 0.5, 80),
        ("throughput", 1, 1000),
        ("reliability", 0.97, 0.9999),
        ("jitter", 0, 20),
        ("packet_loss", 0, 0.05),
    ]
    
    all_results = {}
    
    print("Executando testes de sensibilidade...")
    for feature_name, min_val, max_val in features:
        print(f"  Testando {feature_name}...")
        values, scores = asyncio.run(test_feature_sensitivity(predictor, feature_name, min_val, max_val))
        all_results[feature_name] = (values, scores)
    
    print()
    
    # Criar gráficos
    print("Gerando gráficos...")
    n_features = len(features)
    cols = 3
    rows = (n_features + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(15, 5*rows))
    axes = axes.flatten() if n_features > 1 else [axes]
    
    for idx, (feature_name, (values, scores)) in enumerate(all_results.items()):
        ax = axes[idx]
        ax.plot(values, scores, 'b-', linewidth=2, marker='o', markersize=2)
        ax.set_xlabel(feature_name.replace('_', ' ').title(), fontsize=10)
        ax.set_ylabel('Viability Score', fontsize=10)
        ax.set_title(f'Sensibilidade: {feature_name}', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
    
    # Ocultar eixos extras
    for idx in range(n_features, len(axes)):
        axes[idx].axis('off')
    
    plt.tight_layout()
    plot_path = RESULTS_DIR / "FASE3_sensitivity_plots.png"
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Gráficos salvos: {plot_path}")
    print()
    
    # Salvar resultados
    df_data = []
    for feature_name, (values, scores) in all_results.items():
        for x, y in zip(values, scores):
            df_data.append({
                "feature": feature_name,
                "value": float(x),
                "viability_score": float(y) if y is not None else None
            })
    
    df = pd.DataFrame(df_data)
    csv_path = RESULTS_DIR / "FASE3_sensitivity.csv"
    df.to_csv(csv_path, index=False)
    print(f"✅ CSV salvo: {csv_path}")
    
    # Relatório
    report_path = RESULTS_DIR / "FASE3_SENSITIVITY.md"
    with open(report_path, 'w') as f:
        f.write("# FASE 3.4 — SENSIBILIDADE POR FEATURE\n\n")
        f.write(f"**Data:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## Resumo\n\n")
        f.write("Análise de sensibilidade One-Factor-At-A-Time para features principais.\n\n")
        f.write("## Gráficos\n\n")
        f.write(f"![Sensibilidade](FASE3_sensitivity_plots.png)\n\n")
        f.write("## Conclusão\n\n")
        f.write("✅ Análise de sensibilidade concluída.\n")
    
    print(f"✅ Relatório salvo: {report_path}")
    print()
    
    print("=" * 80)
    print("RESUMO FASE 3.4")
    print("=" * 80)
    print(f"✅ Features testadas: {len(features)}")
    print("✅ FASE 3.4 CONCLUÍDA")
    return 0


if __name__ == "__main__":
    exit(main())

