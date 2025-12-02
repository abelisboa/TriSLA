#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FASE 3.1 — Testes básicos com 50 cenários sintéticos
Valida estabilidade e comportamento básico do modelo ML-NSMF v3.7.0
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


def generate_scenarios(n=50):
    """Gera n cenários sintéticos realistas"""
    np.random.seed(42)  # Reproducibilidade
    
    scenarios = []
    slice_types = ["URLLC", "eMBB", "mMTC"]
    
    for i in range(n):
        # Distribuir slice types de forma balanceada
        slice_type = slice_types[i % 3]
        
        # Ranges realistas por tipo de slice
        if slice_type == "URLLC":
            latency = np.random.uniform(0.5, 5.0)
            throughput = np.random.uniform(10, 100)
            reliability = np.random.uniform(0.999, 0.9999)
            jitter = np.random.uniform(0.05, 1.0)
            packet_loss = np.random.uniform(0.0001, 0.001)
        elif slice_type == "eMBB":
            latency = np.random.uniform(5, 30)
            throughput = np.random.uniform(50, 1000)
            reliability = np.random.uniform(0.99, 0.999)
            jitter = np.random.uniform(1, 10)
            packet_loss = np.random.uniform(0.001, 0.01)
        else:  # mMTC
            latency = np.random.uniform(20, 80)
            throughput = np.random.uniform(1, 50)
            reliability = np.random.uniform(0.97, 0.99)
            jitter = np.random.uniform(5, 20)
            packet_loss = np.random.uniform(0.01, 0.05)
        
        scenario = {
            "scenario_id": i + 1,
            "slice_type": slice_type,
            "latency": float(latency),
            "throughput": float(throughput),
            "reliability": float(reliability),
            "jitter": float(jitter),
            "packet_loss": float(packet_loss),
            "cpu_utilization": float(np.random.uniform(0.1, 0.8)),
            "memory_utilization": float(np.random.uniform(0.1, 0.8)),
            "network_bandwidth_available": float(np.random.uniform(100, 1000)),
            "active_slices_count": float(np.random.randint(1, 50))
        }
        scenarios.append(scenario)
    
    return scenarios


async def predict_scenarios(scenarios, predictor):
    """Executa predições para todos os cenários"""
    results = []
    errors = []
    
    for scenario in scenarios:
        try:
            # Normalizar métricas
            normalized = await predictor.normalize(scenario)
            
            # Predizer
            prediction = await predictor.predict(normalized)
            
            # Validar resultado
            if prediction is None:
                errors.append(f"Scenario {scenario['scenario_id']}: prediction is None")
                continue
            
            viability_score = prediction.get("viability_score")
            if viability_score is None:
                errors.append(f"Scenario {scenario['scenario_id']}: viability_score is None")
                continue
            
            if not (0 <= viability_score <= 1):
                errors.append(f"Scenario {scenario['scenario_id']}: viability_score out of range: {viability_score}")
            
            # Adicionar resultados
            result = {
                **scenario,
                "viability_score": float(viability_score),
                "risk_score": float(prediction.get("risk_score", 1.0 - viability_score)),
                "risk_level": prediction.get("risk_level", "unknown"),
                "confidence": float(prediction.get("confidence", 0.5)),
                "model_used": prediction.get("model_used", False)
            }
            results.append(result)
            
        except Exception as e:
            errors.append(f"Scenario {scenario['scenario_id']}: {str(e)}")
    
    return results, errors


def create_plots(df, output_dir):
    """Cria gráficos de análise"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Scatter: viability_score vs latency
    axes[0].scatter(df['latency'], df['viability_score'], alpha=0.6, s=50)
    axes[0].set_xlabel('Latency (ms)', fontsize=12)
    axes[0].set_ylabel('Viability Score', fontsize=12)
    axes[0].set_title('Viability Score vs Latency', fontsize=14, fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    
    # Scatter: viability_score vs reliability
    axes[1].scatter(df['reliability'], df['viability_score'], alpha=0.6, s=50, c='green')
    axes[1].set_xlabel('Reliability', fontsize=12)
    axes[1].set_ylabel('Viability Score', fontsize=12)
    axes[1].set_title('Viability Score vs Reliability', fontsize=14, fontweight='bold')
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plot_path = output_dir / "FASE3_basic_scenarios_plots.png"
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Gráficos salvos: {plot_path}")
    return plot_path


def main():
    print("=" * 80)
    print("FASE 3.1 — TESTES BÁSICOS COM 50 CENÁRIOS SINTÉTICOS")
    print("=" * 80)
    print()
    
    # 1. Inicializar predictor
    print("1. Inicializando predictor...")
    predictor = RiskPredictor()
    
    if predictor.model is None:
        print("❌ ERRO: Modelo não carregado!")
        return 1
    
    if predictor.scaler is None:
        print("❌ ERRO: Scaler não carregado!")
        return 1
    
    print("✅ Predictor inicializado com sucesso")
    print()
    
    # 2. Gerar cenários
    print("2. Gerando 50 cenários sintéticos...")
    scenarios = generate_scenarios(50)
    print(f"✅ {len(scenarios)} cenários gerados")
    print()
    
    # 3. Executar predições
    print("3. Executando predições...")
    results, errors = asyncio.run(predict_scenarios(scenarios, predictor))
    
    if errors:
        print(f"⚠️  {len(errors)} erros encontrados:")
        for error in errors[:5]:  # Mostrar apenas os 5 primeiros
            print(f"   - {error}")
        if len(errors) > 5:
            print(f"   ... e mais {len(errors) - 5} erros")
    else:
        print("✅ Nenhum erro encontrado")
    
    print(f"✅ {len(results)} predições bem-sucedidas")
    print()
    
    # 4. Validar resultados
    print("4. Validando resultados...")
    df = pd.DataFrame(results)
    
    # Verificar NaN
    nan_count = df.isna().sum().sum()
    if nan_count > 0:
        print(f"⚠️  {nan_count} valores NaN encontrados")
    else:
        print("✅ Nenhum NaN encontrado")
    
    # Verificar range de viability_score
    invalid_scores = df[(df['viability_score'] < 0) | (df['viability_score'] > 1)]
    if len(invalid_scores) > 0:
        print(f"⚠️  {len(invalid_scores)} scores fora do range [0,1]")
    else:
        print("✅ Todos os scores no range [0,1]")
    
    # Estatísticas
    print(f"\n📊 Estatísticas dos scores:")
    print(f"   Média: {df['viability_score'].mean():.4f}")
    print(f"   Mediana: {df['viability_score'].median():.4f}")
    print(f"   Desvio padrão: {df['viability_score'].std():.4f}")
    print(f"   Min: {df['viability_score'].min():.4f}")
    print(f"   Max: {df['viability_score'].max():.4f}")
    print()
    
    # 5. Salvar resultados
    print("5. Salvando resultados...")
    
    # CSV
    csv_path = RESULTS_DIR / "FASE3_basic_scenarios.csv"
    df.to_csv(csv_path, index=False)
    print(f"✅ CSV salvo: {csv_path}")
    
    # JSON
    json_path = RESULTS_DIR / "FASE3_basic_scenarios.json"
    with open(json_path, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_scenarios": len(scenarios),
            "successful_predictions": len(results),
            "errors": len(errors),
            "statistics": {
                "mean_viability": float(df['viability_score'].mean()),
                "median_viability": float(df['viability_score'].median()),
                "std_viability": float(df['viability_score'].std()),
                "min_viability": float(df['viability_score'].min()),
                "max_viability": float(df['viability_score'].max())
            },
            "results": results
        }, f, indent=2)
    print(f"✅ JSON salvo: {json_path}")
    
    # 6. Criar gráficos
    print("6. Gerando gráficos...")
    plot_path = create_plots(df, RESULTS_DIR)
    print()
    
    # 7. Resumo final
    print("=" * 80)
    print("RESUMO FASE 3.1")
    print("=" * 80)
    print(f"✅ Cenários gerados: {len(scenarios)}")
    print(f"✅ Predições bem-sucedidas: {len(results)}")
    print(f"⚠️  Erros: {len(errors)}")
    print(f"✅ Arquivos exportados:")
    print(f"   - {csv_path}")
    print(f"   - {json_path}")
    print(f"   - {plot_path}")
    print()
    
    if len(errors) == 0 and nan_count == 0 and len(invalid_scores) == 0:
        print("✅ FASE 3.1 CONCLUÍDA COM SUCESSO")
        return 0
    else:
        print("⚠️  FASE 3.1 CONCLUÍDA COM AVISOS")
        return 1


if __name__ == "__main__":
    exit(main())

