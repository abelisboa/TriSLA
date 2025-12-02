#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FASE 4.3 — Teste de Integração Local
Decision Engine ↔ ML-NSMF v3.7.0

Testa o caminho completo de integração sem NASP/Kubernetes.
"""

import sys
import os
from pathlib import Path
import asyncio
import json
import pandas as pd
from datetime import datetime
from typing import Dict, Any

# Adicionar raiz do projeto ao path
BASE_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

# Importar componentes
from apps.ml_nsmf.src.predictor import RiskPredictor

# Importar Decision Engine (ajustar path se necessário)
sys.path.insert(0, str(BASE_DIR / "apps" / "decision-engine" / "src"))
from ml_client import MLClient
from models import DecisionInput, SLAIntent, SliceType

RESULTS_DIR = BASE_DIR / "analysis" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def create_test_scenarios():
    """Cria cenários de teste baseados em test_ml_nsmf_model_v3_7_0.py"""
    return [
        {
            "name": "URLLC_critico_realista",
            "slice_type": "URLLC",
            "latency": 0.8,
            "throughput": 20,
            "reliability": 0.999,
            "jitter": 0.10,
            "packet_loss": 0.0001,
            "cpu_utilization": 0.12,
            "memory_utilization": 0.18,
            "network_bandwidth_available": 150,
            "active_slices_count": 5.0,
        },
        {
            "name": "eMBB_alto_trafego",
            "slice_type": "eMBB",
            "latency": 15,
            "throughput": 250,
            "reliability": 0.995,
            "jitter": 3.0,
            "packet_loss": 0.002,
            "cpu_utilization": 0.58,
            "memory_utilization": 0.61,
            "network_bandwidth_available": 500,
            "active_slices_count": 12.0,
        },
        {
            "name": "mMTC_denso_100k_UEs",
            "slice_type": "mMTC",
            "latency": 40,
            "throughput": 1,
            "reliability": 0.98,
            "jitter": 12,
            "packet_loss": 0.01,
            "cpu_utilization": 0.37,
            "memory_utilization": 0.44,
            "network_bandwidth_available": 80,
            "active_slices_count": 120.0,
        }
    ]


def create_decision_input(scenario: Dict[str, Any]) -> DecisionInput:
    """Cria DecisionInput a partir de um cenário"""
    intent = SLAIntent(
        intent_id=f"intent-{scenario['name']}",
        service_type=SliceType(scenario["slice_type"]),
        sla_requirements={
            "latency": f"{scenario['latency']}ms",
            "throughput": f"{scenario['throughput']}Mbps",
            "reliability": scenario["reliability"],
            "jitter": f"{scenario['jitter']}ms",
            "packet_loss": scenario["packet_loss"]
        }
    )
    
    return DecisionInput(
        intent=intent,
        nest=None,  # Não usar NEST para simplificar
        context={
            "cpu_utilization": scenario["cpu_utilization"],
            "memory_utilization": scenario["memory_utilization"],
            "network_bandwidth_available": scenario["network_bandwidth_available"],
            "active_slices_count": scenario["active_slices_count"]
        }
    )


async def test_direct_model(scenario: Dict[str, Any], predictor: RiskPredictor) -> float:
    """Testa modelo diretamente (sem Decision Engine)"""
    metrics = {
        "latency": scenario["latency"],
        "throughput": scenario["throughput"],
        "reliability": scenario["reliability"],
        "jitter": scenario["jitter"],
        "packet_loss": scenario["packet_loss"],
        "slice_type": scenario["slice_type"],
        "cpu_utilization": scenario["cpu_utilization"],
        "memory_utilization": scenario["memory_utilization"],
        "network_bandwidth_available": scenario["network_bandwidth_available"],
        "active_slices_count": scenario["active_slices_count"]
    }
    
    normalized = await predictor.normalize(metrics)
    prediction = await predictor.predict(normalized)
    
    return prediction.get("viability_score", 0.0)


async def test_via_ml_client(scenario: Dict[str, Any], ml_client: MLClient) -> Dict[str, Any]:
    """Testa via MLClient (simulando Decision Engine)"""
    decision_input = create_decision_input(scenario)
    
    # Extrair features manualmente (como MLClient faria)
    features = ml_client._extract_features(decision_input)
    
    # Chamar predictor diretamente (simulando HTTP call)
    predictor = RiskPredictor()
    normalized = await predictor.normalize(features)
    prediction = await predictor.predict(normalized)
    explanation = await predictor.explain(prediction, normalized)
    
    # Simular response do ML-NSMF
    response_data = {
        "prediction": prediction,
        "explanation": explanation
    }
    
    # Processar como MLClient faria
    prediction_data = response_data.get("prediction", {})
    viability_score = prediction_data.get("viability_score")
    risk_score = prediction_data.get("risk_score", 0.5)
    
    return {
        "viability_score": float(viability_score) if viability_score is not None else None,
        "risk_score": float(risk_score),
        "risk_level": prediction_data.get("risk_level", "medium"),
        "confidence": float(prediction_data.get("confidence", 0.8)),
        "model_used": prediction_data.get("model_used", True)
    }


async def run_integration_tests():
    """Executa testes de integração"""
    print("=" * 80)
    print("FASE 4.3 — TESTE DE INTEGRAÇÃO LOCAL")
    print("Decision Engine ↔ ML-NSMF v3.7.0")
    print("=" * 80)
    print()
    
    # Inicializar componentes
    print("1. Inicializando componentes...")
    predictor = RiskPredictor()
    ml_client = MLClient()
    
    if predictor.model is None:
        print("❌ ERRO: Modelo não carregado!")
        return 1
    
    print("✅ Predictor inicializado")
    print("✅ MLClient inicializado")
    print()
    
    # Criar cenários
    print("2. Criando cenários de teste...")
    scenarios = create_test_scenarios()
    print(f"✅ {len(scenarios)} cenários criados")
    print()
    
    # Executar testes
    print("3. Executando testes de integração...")
    print()
    
    results = []
    
    for scenario in scenarios:
        print(f"  Testando: {scenario['name']} ({scenario['slice_type']})...")
        
        # Teste direto do modelo
        direct_score = await test_direct_model(scenario, predictor)
        
        # Teste via MLClient (simulando Decision Engine)
        ml_client_result = await test_via_ml_client(scenario, ml_client)
        
        # Calcular diferença
        ml_score = ml_client_result.get("viability_score")
        if ml_score is None:
            diff = None
            status = "ERROR"
        else:
            diff = abs(direct_score - ml_score)
            status = "OK" if diff < 0.02 else "DIVERGE"
        
        result = {
            "scenario": scenario["name"],
            "slice_type": scenario["slice_type"],
            "direct_viability_score": float(direct_score),
            "ml_client_viability_score": float(ml_score) if ml_score is not None else None,
            "ml_client_risk_score": ml_client_result.get("risk_score"),
            "ml_client_risk_level": ml_client_result.get("risk_level"),
            "ml_client_confidence": ml_client_result.get("confidence"),
            "ml_client_model_used": ml_client_result.get("model_used"),
            "difference": float(diff) if diff is not None else None,
            "status": status
        }
        results.append(result)
        
        ml_str = f"{ml_score:.6f}" if ml_score is not None else "None"
        diff_str = f"{diff:.6f}" if diff is not None else "N/A"
        print(f"    Direct: {direct_score:.6f}, ML-Client: {ml_str}, Diff: {diff_str}, Status: {status}")
    
    print()
    
    # Criar DataFrame
    df = pd.DataFrame(results)
    
    # Tabela CLI
    print("=" * 100)
    print(f"{'Cenário':<30} {'Tipo':<6} {'Score(Direct)':>18} {'Score(ML-Client)':>18} {'Dif':>12} {'Status':>10}")
    print("=" * 100)
    for _, row in df.iterrows():
        direct = row['direct_viability_score']
        ml = row['ml_client_viability_score']
        diff = row['difference']
        ml_str = f"{ml:18.6f}" if ml is not None else f"{'None':>18}"
        diff_str = f"{diff:12.6f}" if diff is not None else f"{'N/A':>12}"
        print(
            f"{row['scenario']:<30} {row['slice_type']:<6} "
            f"{direct:18.6f} {ml_str} "
            f"{diff_str} {row['status']:>10}"
        )
    print("=" * 100)
    print()
    
    # Estatísticas
    valid_results = df[df['difference'].notna()]
    if len(valid_results) > 0:
        max_diff = valid_results['difference'].max()
        mean_diff = valid_results['difference'].mean()
        ok_count = len(valid_results[valid_results['status'] == 'OK'])
        
        print(f"📊 Estatísticas:")
        print(f"   Diferença máxima: {max_diff:.6f}")
        print(f"   Diferença média: {mean_diff:.6f}")
        print(f"   Testes OK (< 0.02): {ok_count}/{len(valid_results)}")
        print()
    
    # Salvar resultados
    print("4. Salvando resultados...")
    
    csv_path = RESULTS_DIR / "FASE4_INTEGRATION_TESTS.csv"
    df.to_csv(csv_path, index=False)
    print(f"✅ CSV salvo: {csv_path}")
    
    json_path = RESULTS_DIR / "FASE4_INTEGRATION_TESTS.json"
    with open(json_path, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_scenarios": len(scenarios),
            "results": results,
            "statistics": {
                "max_difference": float(max_diff) if len(valid_results) > 0 else None,
                "mean_difference": float(mean_diff) if len(valid_results) > 0 else None,
                "ok_count": int(ok_count) if len(valid_results) > 0 else 0,
                "total_valid": len(valid_results)
            }
        }, f, indent=2)
    print(f"✅ JSON salvo: {json_path}")
    
    txt_path = RESULTS_DIR / "FASE4_INTEGRATION_TESTS.txt"
    with open(txt_path, 'w') as f:
        f.write("FASE 4.3 — TESTE DE INTEGRAÇÃO LOCAL\n")
        f.write("=" * 100 + "\n\n")
        f.write(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"Total de cenários: {len(scenarios)}\n\n")
        f.write("=" * 100 + "\n")
        f.write(f"{'Cenário':<30} {'Tipo':<6} {'Score(Direct)':>18} {'Score(ML-Client)':>18} {'Dif':>12} {'Status':>10}\n")
        f.write("=" * 100 + "\n")
        for _, row in df.iterrows():
            direct = row['direct_viability_score']
            ml = row['ml_client_viability_score']
            diff = row['difference']
            ml_str = f"{ml:18.6f}" if ml is not None else f"{'None':>18}"
            diff_str = f"{diff:12.6f}" if diff is not None else f"{'N/A':>12}"
            f.write(
                f"{row['scenario']:<30} {row['slice_type']:<6} "
                f"{direct:18.6f} {ml_str} "
                f"{diff_str} {row['status']:>10}\n"
            )
        f.write("=" * 100 + "\n\n")
        if len(valid_results) > 0:
            f.write(f"Diferença máxima: {max_diff:.6f}\n")
            f.write(f"Diferença média: {mean_diff:.6f}\n")
            f.write(f"Testes OK (< 0.02): {ok_count}/{len(valid_results)}\n")
    print(f"✅ TXT salvo: {txt_path}")
    print()
    
    # Resumo final
    print("=" * 80)
    print("RESUMO FASE 4.3")
    print("=" * 80)
    print(f"✅ Cenários testados: {len(scenarios)}")
    print(f"✅ Testes válidos: {len(valid_results)}")
    if len(valid_results) > 0:
        print(f"✅ Testes OK: {ok_count}/{len(valid_results)}")
        print(f"⚠️  Testes divergentes: {len(valid_results) - ok_count}/{len(valid_results)}")
    print()
    
    if len(valid_results) == len(scenarios) and ok_count == len(valid_results):
        print("✅ FASE 4.3 CONCLUÍDA COM SUCESSO")
        return 0
    else:
        print("⚠️  FASE 4.3 CONCLUÍDA COM AVISOS")
        return 1


if __name__ == "__main__":
    exit(asyncio.run(run_integration_tests()))

