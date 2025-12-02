#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FASE 3.2 — Testes de monotonicidade
Valida comportamento monotônico do modelo ML-NSMF v3.7.0
"""

import sys
import os
from pathlib import Path
import numpy as np
import pandas as pd
import json
import asyncio
import matplotlib.pyplot as plt
from datetime import datetime

# Adicionar raiz do projeto ao path
BASE_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from apps.ml_nsmf.src.predictor import RiskPredictor

# Configuração de resultados
RESULTS_DIR = BASE_DIR / "analysis" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


async def test_latency_monotonicity(predictor, n_points=50):
    """Testa monotonicidade aumentando latência"""
    print("  Testando monotonicidade de latência...")
    
    base_metrics = {
        "latency": 0.5,
        "throughput": 100,
        "reliability": 0.999,
        "jitter": 1.0,
        "packet_loss": 0.001,
        "cpu_utilization": 0.5,
        "memory_utilization": 0.5,
        "network_bandwidth_available": 500,
        "active_slices_count": 10,
        "slice_type": "URLLC"
    }
    
    latencies = np.linspace(0.5, 80, n_points)
    scores = []
    
    for latency in latencies:
        metrics = {**base_metrics, "latency": float(latency)}
        normalized = await predictor.normalize(metrics)
        prediction = await predictor.predict(normalized)
        scores.append(prediction.get("viability_score", None))
    
    return latencies, scores


async def test_reliability_monotonicity(predictor, n_points=50):
    """Testa monotonicidade reduzindo reliability"""
    print("  Testando monotonicidade de reliability...")
    
    base_metrics = {
        "latency": 5.0,
        "throughput": 100,
        "reliability": 0.9999,
        "jitter": 1.0,
        "packet_loss": 0.001,
        "cpu_utilization": 0.5,
        "memory_utilization": 0.5,
        "network_bandwidth_available": 500,
        "active_slices_count": 10,
        "slice_type": "eMBB"
    }
    
    reliabilities = np.linspace(0.9999, 0.97, n_points)
    scores = []
    
    for reliability in reliabilities:
        metrics = {**base_metrics, "reliability": float(reliability)}
        normalized = await predictor.normalize(metrics)
        prediction = await predictor.predict(normalized)
        scores.append(prediction.get("viability_score", None))
    
    return reliabilities, scores


async def test_packet_loss_monotonicity(predictor, n_points=50):
    """Testa monotonicidade aumentando packet_loss"""
    print("  Testando monotonicidade de packet_loss...")
    
    base_metrics = {
        "latency": 5.0,
        "throughput": 100,
        "reliability": 0.999,
        "jitter": 1.0,
        "packet_loss": 0.0,
        "cpu_utilization": 0.5,
        "memory_utilization": 0.5,
        "network_bandwidth_available": 500,
        "active_slices_count": 10,
        "slice_type": "eMBB"
    }
    
    packet_losses = np.linspace(0.0, 0.05, n_points)
    scores = []
    
    for packet_loss in packet_losses:
        metrics = {**base_metrics, "packet_loss": float(packet_loss)}
        normalized = await predictor.normalize(metrics)
        prediction = await predictor.predict(normalized)
        scores.append(prediction.get("viability_score", None))
    
    return packet_losses, scores


def calculate_monotonicity(latencies, scores):
    """Calcula métricas de monotonicidade"""
    # Remover None
    valid_indices = [i for i, s in enumerate(scores) if s is not None]
    if len(valid_indices) < 2:
        return None, None, None
    
    valid_scores = [scores[i] for i in valid_indices]
    valid_latencies = [latencies[i] for i in valid_indices]
    
    # Calcular correlação (deve ser negativa para latência)
    correlation = np.corrcoef(valid_latencies, valid_scores)[0, 1]
    
    # Contar violações (quando score aumenta ao invés de diminuir)
    violations = 0
    for i in range(1, len(valid_scores)):
        if valid_scores[i] > valid_scores[i-1]:
            violations += 1
    
    violation_rate = violations / (len(valid_scores) - 1) if len(valid_scores) > 1 else 0
    
    return correlation, violations, violation_rate


def create_plots(results, output_dir):
    """Cria gráficos de monotonicidade"""
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    # Teste 1: Latência
    latencies, scores = results['latency']
    axes[0].plot(latencies, scores, 'b-', linewidth=2, marker='o', markersize=3)
    axes[0].set_xlabel('Latency (ms)', fontsize=12)
    axes[0].set_ylabel('Viability Score', fontsize=12)
    axes[0].set_title('Monotonicidade: Latência', fontsize=14, fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    axes[0].invert_yaxis()  # Esperamos que score diminua com latência
    
    # Teste 2: Reliability
    reliabilities, scores = results['reliability']
    axes[1].plot(reliabilities, scores, 'g-', linewidth=2, marker='o', markersize=3)
    axes[1].set_xlabel('Reliability', fontsize=12)
    axes[1].set_ylabel('Viability Score', fontsize=12)
    axes[1].set_title('Monotonicidade: Reliability', fontsize=14, fontweight='bold')
    axes[1].grid(True, alpha=0.3)
    
    # Teste 3: Packet Loss
    packet_losses, scores = results['packet_loss']
    axes[2].plot(packet_losses, scores, 'r-', linewidth=2, marker='o', markersize=3)
    axes[2].set_xlabel('Packet Loss', fontsize=12)
    axes[2].set_ylabel('Viability Score', fontsize=12)
    axes[2].set_title('Monotonicidade: Packet Loss', fontsize=14, fontweight='bold')
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plot_path = output_dir / "FASE3_monotonicity_plots.png"
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Gráficos salvos: {plot_path}")
    return plot_path


def main():
    print("=" * 80)
    print("FASE 3.2 — TESTES DE MONOTONICIDADE")
    print("=" * 80)
    print()
    
    # 1. Inicializar predictor
    print("1. Inicializando predictor...")
    predictor = RiskPredictor()
    
    if predictor.model is None:
        print("❌ ERRO: Modelo não carregado!")
        return 1
    
    print("✅ Predictor inicializado")
    print()
    
    # 2. Executar testes de monotonicidade
    print("2. Executando testes de monotonicidade...")
    print()
    
    results = {}
    metrics = {}
    
    # Teste 1: Latência
    latencies, scores = asyncio.run(test_latency_monotonicity(predictor))
    results['latency'] = (latencies, scores)
    corr, violations, violation_rate = calculate_monotonicity(latencies, scores)
    metrics['latency'] = {
        "correlation": float(corr) if corr is not None else None,
        "violations": int(violations) if violations is not None else None,
        "violation_rate": float(violation_rate) if violation_rate is not None else None,
        "expected_negative": True
    }
    print(f"   ✅ Latência: correlação={corr:.4f}, violações={violations}, taxa={violation_rate:.4f}")
    
    # Teste 2: Reliability
    reliabilities, scores = asyncio.run(test_reliability_monotonicity(predictor))
    results['reliability'] = (reliabilities, scores)
    corr, violations, violation_rate = calculate_monotonicity(reliabilities, scores)
    metrics['reliability'] = {
        "correlation": float(corr) if corr is not None else None,
        "violations": int(violations) if violations is not None else None,
        "violation_rate": float(violation_rate) if violation_rate is not None else None,
        "expected_positive": True
    }
    print(f"   ✅ Reliability: correlação={corr:.4f}, violações={violations}, taxa={violation_rate:.4f}")
    
    # Teste 3: Packet Loss
    packet_losses, scores = asyncio.run(test_packet_loss_monotonicity(predictor))
    results['packet_loss'] = (packet_losses, scores)
    corr, violations, violation_rate = calculate_monotonicity(packet_losses, scores)
    metrics['packet_loss'] = {
        "correlation": float(corr) if corr is not None else None,
        "violations": int(violations) if violations is not None else None,
        "violation_rate": float(violation_rate) if violation_rate is not None else None,
        "expected_negative": True
    }
    print(f"   ✅ Packet Loss: correlação={corr:.4f}, violações={violations}, taxa={violation_rate:.4f}")
    print()
    
    # 3. Criar gráficos
    print("3. Gerando gráficos...")
    plot_path = create_plots(results, RESULTS_DIR)
    print()
    
    # 4. Salvar resultados
    print("4. Salvando resultados...")
    
    # Preparar dados para CSV
    df_data = []
    for test_name, (x_vals, y_vals) in results.items():
        for x, y in zip(x_vals, y_vals):
            df_data.append({
                "test": test_name,
                "x_value": float(x),
                "viability_score": float(y) if y is not None else None
            })
    
    df = pd.DataFrame(df_data)
    csv_path = RESULTS_DIR / "FASE3_monotonicity.csv"
    df.to_csv(csv_path, index=False)
    print(f"✅ CSV salvo: {csv_path}")
    
    # 5. Gerar relatório Markdown
    report_path = RESULTS_DIR / "FASE3_MONOTONICITY.md"
    with open(report_path, 'w') as f:
        f.write("# FASE 3.2 — TESTES DE MONOTONICIDADE\n\n")
        f.write(f"**Data:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## Resumo Executivo\n\n")
        f.write("Este relatório apresenta os resultados dos testes de monotonicidade do modelo ML-NSMF v3.7.0.\n\n")
        f.write("## Resultados\n\n")
        
        for test_name, metric in metrics.items():
            f.write(f"### {test_name.upper()}\n\n")
            f.write(f"- **Correlação:** {metric['correlation']:.4f}\n")
            f.write(f"- **Violações:** {metric['violations']}\n")
            f.write(f"- **Taxa de Violação:** {metric['violation_rate']:.4f}\n")
            
            if test_name in ['latency', 'packet_loss']:
                if metric['correlation'] < -0.7:
                    f.write("- **Status:** ✅ Monotônico (correlação negativa forte)\n\n")
                else:
                    f.write("- **Status:** ⚠️  Monotonicidade fraca\n\n")
            else:  # reliability
                if metric['correlation'] > 0.7:
                    f.write("- **Status:** ✅ Monotônico (correlação positiva forte)\n\n")
                else:
                    f.write("- **Status:** ⚠️  Monotonicidade fraca\n\n")
        
        f.write("## Gráficos\n\n")
        f.write(f"![Monotonicidade](FASE3_monotonicity_plots.png)\n\n")
        f.write("## Conclusão\n\n")
        
        all_good = all(
            (m['correlation'] < -0.7 if test in ['latency', 'packet_loss'] else m['correlation'] > 0.7)
            for test, m in metrics.items()
            if m['correlation'] is not None
        )
        
        if all_good:
            f.write("✅ **O modelo apresenta comportamento monotônico adequado para todas as features testadas.**\n")
        else:
            f.write("⚠️  **Algumas features apresentam monotonicidade fraca. Revisar modelo pode ser necessário.**\n")
    
    print(f"✅ Relatório salvo: {report_path}")
    print()
    
    # 6. Resumo final
    print("=" * 80)
    print("RESUMO FASE 3.2")
    print("=" * 80)
    print(f"✅ Testes executados: 3")
    print(f"✅ Arquivos exportados:")
    print(f"   - {csv_path}")
    print(f"   - {report_path}")
    print(f"   - {plot_path}")
    print()
    
    print("✅ FASE 3.2 CONCLUÍDA")
    return 0


if __name__ == "__main__":
    exit(main())

