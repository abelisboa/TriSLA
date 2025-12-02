#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FASE 3.5 — Testes de consistência slice-type
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import json
import asyncio
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from apps.ml_nsmf.src.predictor import RiskPredictor

RESULTS_DIR = BASE_DIR / "analysis" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def generate_slice_scenarios():
    """Gera cenários fixos variando apenas slice_type"""
    base = {
        "latency": 5.0,
        "throughput": 100,
        "reliability": 0.999,
        "jitter": 1.0,
        "packet_loss": 0.001,
        "cpu_utilization": 0.5,
        "memory_utilization": 0.5,
        "network_bandwidth_available": 500,
        "active_slices_count": 10
    }
    
    scenarios = []
    for slice_type in ["URLLC", "eMBB", "mMTC"]:
        scenarios.append({
            **base,
            "slice_type": slice_type,
            "scenario_name": f"Fixed_{slice_type}"
        })
    
    return scenarios


async def test_slice_scenarios(predictor, scenarios):
    """Testa cenários por slice type"""
    results = []
    
    for scenario in scenarios:
        normalized = await predictor.normalize(scenario)
        prediction = await predictor.predict(normalized)
        
        results.append({
            **scenario,
            "viability_score": float(prediction.get("viability_score", 0)),
            "risk_score": float(prediction.get("risk_score", 0)),
            "risk_level": prediction.get("risk_level", "unknown")
        })
    
    return results


def main():
    print("=" * 80)
    print("FASE 3.5 — TESTES DE CONSISTÊNCIA SLICE-TYPE")
    print("=" * 80)
    print()
    
    predictor = RiskPredictor()
    if predictor.model is None:
        print("❌ ERRO: Modelo não carregado!")
        return 1
    
    print("✅ Predictor inicializado")
    print()
    
    scenarios = generate_slice_scenarios()
    print(f"✅ {len(scenarios)} cenários gerados")
    print()
    
    print("Executando testes...")
    results = asyncio.run(test_slice_scenarios(predictor, scenarios))
    
    df = pd.DataFrame(results)
    
    # Tabela CLI
    print("\n" + "=" * 80)
    print(f"{'Slice Type':<15} {'Viability Score':<18} {'Risk Score':<15} {'Risk Level':<15}")
    print("=" * 80)
    for _, row in df.iterrows():
        print(f"{row['slice_type']:<15} {row['viability_score']:<18.6f} {row['risk_score']:<15.6f} {row['risk_level']:<15}")
    print("=" * 80)
    print()
    
    # Salvar
    csv_path = RESULTS_DIR / "FASE3_slice_type.csv"
    df.to_csv(csv_path, index=False)
    print(f"✅ CSV salvo: {csv_path}")
    
    json_path = RESULTS_DIR / "FASE3_slice_type.json"
    with open(json_path, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "results": results
        }, f, indent=2)
    print(f"✅ JSON salvo: {json_path}")
    print()
    
    print("=" * 80)
    print("RESUMO FASE 3.5")
    print("=" * 80)
    print(f"✅ Slice types testados: {len(scenarios)}")
    print("✅ FASE 3.5 CONCLUÍDA")
    return 0


if __name__ == "__main__":
    exit(main())

