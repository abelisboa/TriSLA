#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FASE 3.3 — Testes de robustez a valores extremos
Valida que o modelo não quebra com valores fora do range esperado
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


def generate_extreme_scenarios():
    """Gera cenários com valores extremos"""
    scenarios = [
        {"name": "latency_zero", "latency": 0, "throughput": 100, "reliability": 0.999, "jitter": 1.0, "packet_loss": 0.001, "slice_type": "URLLC"},
        {"name": "latency_extreme", "latency": 500, "throughput": 100, "reliability": 0.999, "jitter": 1.0, "packet_loss": 0.001, "slice_type": "URLLC"},
        {"name": "throughput_zero", "latency": 5, "throughput": 0, "reliability": 0.999, "jitter": 1.0, "packet_loss": 0.001, "slice_type": "eMBB"},
        {"name": "throughput_extreme", "latency": 5, "throughput": 5000, "reliability": 0.999, "jitter": 1.0, "packet_loss": 0.001, "slice_type": "eMBB"},
        {"name": "reliability_above_1", "latency": 5, "throughput": 100, "reliability": 1.5, "jitter": 1.0, "packet_loss": 0.001, "slice_type": "eMBB"},
        {"name": "reliability_negative", "latency": 5, "throughput": 100, "reliability": -0.1, "jitter": 1.0, "packet_loss": 0.001, "slice_type": "eMBB"},
        {"name": "packet_loss_above_1", "latency": 5, "throughput": 100, "reliability": 0.999, "jitter": 1.0, "packet_loss": 1.5, "slice_type": "mMTC"},
        {"name": "packet_loss_negative", "latency": 5, "throughput": 100, "reliability": 0.999, "jitter": 1.0, "packet_loss": -0.1, "slice_type": "mMTC"},
    ]
    
    # Adicionar métricas padrão
    for s in scenarios:
        s.update({
            "cpu_utilization": 0.5,
            "memory_utilization": 0.5,
            "network_bandwidth_available": 500,
            "active_slices_count": 10
        })
    
    return scenarios


async def test_extreme_scenarios(predictor, scenarios):
    """Testa cenários extremos"""
    results = []
    errors = []
    
    for scenario in scenarios:
        try:
            normalized = await predictor.normalize(scenario)
            prediction = await predictor.predict(normalized)
            
            viability_score = prediction.get("viability_score")
            is_valid = viability_score is not None and 0 <= viability_score <= 1
            
            result = {
                **scenario,
                "viability_score": float(viability_score) if viability_score is not None else None,
                "risk_score": float(prediction.get("risk_score", 0.5)) if prediction else None,
                "is_valid": is_valid,
                "error": None
            }
            results.append(result)
            
        except Exception as e:
            errors.append({"scenario": scenario["name"], "error": str(e)})
            results.append({
                **scenario,
                "viability_score": None,
                "risk_score": None,
                "is_valid": False,
                "error": str(e)
            })
    
    return results, errors


def main():
    print("=" * 80)
    print("FASE 3.3 — TESTES DE ROBUSTEZ A VALORES EXTREMOS")
    print("=" * 80)
    print()
    
    predictor = RiskPredictor()
    if predictor.model is None:
        print("❌ ERRO: Modelo não carregado!")
        return 1
    
    print("✅ Predictor inicializado")
    print()
    
    scenarios = generate_extreme_scenarios()
    print(f"✅ {len(scenarios)} cenários extremos gerados")
    print()
    
    print("Executando testes...")
    results, errors = asyncio.run(test_extreme_scenarios(predictor, scenarios))
    
    df = pd.DataFrame(results)
    
    # Validações
    valid_count = df['is_valid'].sum()
    invalid_count = len(df) - valid_count
    
    print(f"✅ Cenários válidos: {valid_count}/{len(scenarios)}")
    print(f"⚠️  Cenários inválidos: {invalid_count}/{len(scenarios)}")
    if errors:
        print(f"⚠️  Erros: {len(errors)}")
        for err in errors:
            print(f"   - {err['scenario']}: {err['error']}")
    print()
    
    # Salvar resultados
    csv_path = RESULTS_DIR / "FASE3_extremes.csv"
    df.to_csv(csv_path, index=False)
    print(f"✅ CSV salvo: {csv_path}")
    
    json_path = RESULTS_DIR / "FASE3_extremes.json"
    with open(json_path, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_scenarios": len(scenarios),
            "valid_scenarios": int(valid_count),
            "invalid_scenarios": int(invalid_count),
            "errors": errors,
            "results": results
        }, f, indent=2)
    print(f"✅ JSON salvo: {json_path}")
    print()
    
    print("=" * 80)
    print("RESUMO FASE 3.3")
    print("=" * 80)
    print(f"✅ Testes executados: {len(scenarios)}")
    print(f"✅ Robustez: {'✅ ALTA' if invalid_count == 0 else '⚠️  MÉDIA'}")
    print()
    
    print("✅ FASE 3.3 CONCLUÍDA")
    return 0


if __name__ == "__main__":
    exit(main())

