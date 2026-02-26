#!/usr/bin/env python3
"""
Script de análise detalhada das evidências coletadas
PROMPT_COLETA_EVIDENCIAS_RESULTADOS_v3.9.3_FINAL
"""

import json
import csv
import os
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import statistics

BASE_DIR = Path("/home/porvir5g/gtp5g/trisla/evidencias_resultados_v3.9.3")

def parse_timestamp(ts_str):
    """Parse timestamp string to datetime"""
    try:
        # Try ISO format
        if 'T' in ts_str:
            ts_str = ts_str.replace('Z', '+00:00')
            return datetime.fromisoformat(ts_str)
    except:
        pass
    return None

def calculate_latency_ms(ts1, ts2):
    """Calculate latency in milliseconds between two timestamps"""
    if not ts1 or not ts2:
        return None
    try:
        dt1 = parse_timestamp(ts1)
        dt2 = parse_timestamp(ts2)
        if dt1 and dt2:
            delta = (dt2 - dt1).total_seconds() * 1000
            return round(delta, 2)
    except:
        pass
    return None

# FASE 2 - Latência End-to-End
print("🔹 FASE 2 - Processando Métricas de Latência...")
latency_data = []
sla_files = list(BASE_DIR.glob("01_slas/sla_*.json"))

for sla_file in sla_files:
    try:
        with open(sla_file, 'r') as f:
            sla = json.load(f)
        
        t_submit = sla.get('t_submit') or sla.get('timestamp')
        t_decision = sla.get('timestamp')
        decision = sla.get('decision', 'N/A')
        sla_id = sla.get('sla_id', 'N/A')
        intent_id = sla.get('intent_id', 'N/A')
        service_type = sla.get('service_type', 'N/A')
        
        t_decision_ms = calculate_latency_ms(t_submit, t_decision) if t_submit and t_decision else None
        
        latency_data.append({
            'sla_id': sla_id,
            'intent_id': intent_id,
            'service_type': service_type,
            't_submit': t_submit,
            't_decision': t_decision,
            't_decision_ms': t_decision_ms,
            'decision': decision
        })
    except Exception as e:
        print(f"⚠️  Erro ao processar {sla_file}: {e}")

# Salvar latência raw
latency_raw_file = BASE_DIR / "10_latency/latency_raw.csv"
with open(latency_raw_file, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['sla_id', 'intent_id', 'service_type', 't_submit', 't_decision', 't_decision_ms', 'decision'])
    writer.writeheader()
    writer.writerows(latency_data)

# Calcular estatísticas
latencies = [d['t_decision_ms'] for d in latency_data if d['t_decision_ms'] is not None]
if latencies:
    latency_summary = {
        'total_slas': len(latency_data),
        'with_latency': len(latencies),
        'mean_ms': round(statistics.mean(latencies), 2),
        'median_ms': round(statistics.median(latencies), 2),
        'min_ms': round(min(latencies), 2),
        'max_ms': round(max(latencies), 2),
    }
    if len(latencies) >= 10:
        sorted_lats = sorted(latencies)
        p95_idx = int(len(sorted_lats) * 0.95)
        p99_idx = int(len(sorted_lats) * 0.99)
        latency_summary['p95_ms'] = round(sorted_lats[p95_idx], 2)
        latency_summary['p99_ms'] = round(sorted_lats[p99_idx], 2)
else:
    latency_summary = {'total_slas': len(latency_data), 'with_latency': 0}

# Salvar resumo de latência
latency_summary_file = BASE_DIR / "10_latency/latency_summary.csv"
with open(latency_summary_file, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=latency_summary.keys())
    writer.writeheader()
    writer.writerow(latency_summary)

print(f"✅ Latência processada: {len(latency_data)} SLAs, {len(latencies)} com métricas")

# FASE 3 - Métricas ML-NSMF
print("\n🔹 FASE 3 - Extraindo Métricas do ML-NSMF...")
ml_predictions = []

for sla_file in sla_files:
    try:
        with open(sla_file, 'r') as f:
            sla = json.load(f)
        
        ml_pred = sla.get('ml_prediction', {})
        if ml_pred:
            ml_predictions.append({
                'timestamp_utc': sla.get('timestamp', 'N/A'),
                'sla_id': sla.get('sla_id', 'N/A'),
                'service_type': sla.get('service_type', 'N/A'),
                'model_used': ml_pred.get('model_used', False),
                'confidence': ml_pred.get('confidence', 'N/A'),
                'risk_score': ml_pred.get('risk_score', 'N/A'),
                'risk_level': ml_pred.get('risk_level', 'N/A'),
                'real_metrics_count': ml_pred.get('metrics_used', {}).get('real_metrics_count', 0)
            })
    except Exception as e:
        print(f"⚠️  Erro ao processar ML {sla_file}: {e}")

# Salvar predições ML
ml_raw_file = BASE_DIR / "03_ml_predictions/ml_predictions_raw.csv"
if ml_predictions:
    with open(ml_raw_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=ml_predictions[0].keys())
        writer.writeheader()
        writer.writerows(ml_predictions)
    
    # Resumo ML
    model_used_count = sum(1 for p in ml_predictions if p.get('model_used') == True)
    ml_summary = {
        'total_predictions': len(ml_predictions),
        'model_used_true': model_used_count,
        'model_used_false': len(ml_predictions) - model_used_count,
        'avg_confidence': round(statistics.mean([p.get('confidence', 0) for p in ml_predictions if isinstance(p.get('confidence'), (int, float))]), 3) if ml_predictions else 'N/A'
    }
    
    ml_summary_file = BASE_DIR / "03_ml_predictions/ml_predictions_summary.csv"
    with open(ml_summary_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=ml_summary.keys())
        writer.writeheader()
        writer.writerow(ml_summary)

print(f"✅ ML processado: {len(ml_predictions)} predições")

# FASE 8 - Consolidação Quantitativa
print("\n🔹 FASE 8 - Consolidação Quantitativa...")

# Ler registry de SLAs
sla_registry_file = BASE_DIR / "01_slas/sla_registry.csv"
scenario_stats = defaultdict(lambda: {'total': 0, 'by_type': defaultdict(int), 'by_decision': defaultdict(int)})

if sla_registry_file.exists():
    with open(sla_registry_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            scenario = row.get('scenario', 'N/A')
            sla_type = row.get('type', 'N/A')
            decision = row.get('decision', 'N/A')
            
            scenario_stats[scenario]['total'] += 1
            scenario_stats[scenario]['by_type'][sla_type] += 1
            scenario_stats[scenario]['by_decision'][decision] += 1

# Tabela por cenário
scenario_table_file = BASE_DIR / "11_tables/scenario_summary.csv"
with open(scenario_table_file, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['scenario', 'total_slas', 'urllc', 'embb', 'mmtc', 'accept', 'reneg', 'reject'])
    for scenario in sorted(scenario_stats.keys()):
        stats = scenario_stats[scenario]
        writer.writerow([
            scenario,
            stats['total'],
            stats['by_type'].get('URLLC', 0),
            stats['by_type'].get('eMBB', 0),
            stats['by_type'].get('mMTC', 0),
            stats['by_decision'].get('ACCEPT', 0),
            stats['by_decision'].get('RENEG', 0),
            stats['by_decision'].get('REJECT', 0)
        ])

# Tabela por domínio/tipo
type_stats = defaultdict(lambda: {'total': 0, 'by_decision': defaultdict(int)})
for sla_file in sla_files:
    try:
        with open(sla_file, 'r') as f:
            sla = json.load(f)
        service_type = sla.get('service_type', 'N/A')
        decision = sla.get('decision', 'N/A')
        type_stats[service_type]['total'] += 1
        type_stats[service_type]['by_decision'][decision] += 1
    except:
        pass

domain_table_file = BASE_DIR / "11_tables/domain_summary.csv"
with open(domain_table_file, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['service_type', 'total', 'accept', 'reneg', 'reject'])
    for service_type in sorted(type_stats.keys()):
        stats = type_stats[service_type]
        writer.writerow([
            service_type,
            stats['total'],
            stats['by_decision'].get('ACCEPT', 0),
            stats['by_decision'].get('RENEG', 0),
            stats['by_decision'].get('REJECT', 0)
        ])

print("✅ Consolidação concluída")

# FASE 9 - Datasets para Gráficos
print("\n🔹 FASE 9 - Preparando Datasets para Gráficos...")

# Dataset: Latência vs Carga
latency_vs_load_file = BASE_DIR / "12_graphs/latency_vs_load.csv"
with open(latency_vs_load_file, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['sla_number', 'scenario', 'latency_ms', 'service_type'])
    for i, data in enumerate(latency_data, 1):
        if data['t_decision_ms']:
            # Determinar cenário do arquivo
            scenario = 'A'  # default
            for sla_file in sla_files:
                if data['sla_id'] in sla_file.name:
                    if '_A_' in sla_file.name:
                        scenario = 'A'
                    elif '_B_' in sla_file.name:
                        scenario = 'B'
                    elif '_C_' in sla_file.name:
                        scenario = 'C'
                    elif '_D_' in sla_file.name:
                        scenario = 'D'
                    break
            writer.writerow([i, scenario, data['t_decision_ms'], data['service_type']])

# Dataset: Decisão vs Slice
decision_vs_slice_file = BASE_DIR / "12_graphs/decision_vs_slice.csv"
with open(decision_vs_slice_file, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['service_type', 'decision', 'count'])
    for service_type in sorted(type_stats.keys()):
        for decision, count in type_stats[service_type]['by_decision'].items():
            writer.writerow([service_type, decision, count])

# Dataset: Confiança ML vs Decisão
ml_confidence_vs_decision_file = BASE_DIR / "12_graphs/ml_confidence_vs_decision.csv"
with open(ml_confidence_vs_decision_file, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['sla_id', 'confidence', 'model_used', 'decision', 'service_type'])
    for pred in ml_predictions:
        # Buscar decisão correspondente
        decision = 'N/A'
        for data in latency_data:
            if data['sla_id'] == pred['sla_id']:
                decision = data['decision']
                break
        writer.writerow([
            pred['sla_id'],
            pred.get('confidence', 'N/A'),
            pred.get('model_used', False),
            decision,
            pred.get('service_type', 'N/A')
        ])

print("✅ Datasets para gráficos preparados")

# FASE 10 - Validação
print("\n🔹 FASE 10 - Validação Linha-a-Linha...")
validation_report = []

# Validar arquivos obrigatórios
required_files = [
    ("01_slas/sla_registry.csv", "Registry de SLAs"),
    ("10_latency/latency_raw.csv", "Latência raw"),
    ("03_ml_predictions/ml_predictions_raw.csv", "Predições ML"),
    ("11_tables/scenario_summary.csv", "Resumo por cenário"),
]

for file_path, description in required_files:
    full_path = BASE_DIR / file_path
    if full_path.exists():
        size = full_path.stat().st_size
        if size > 0:
            validation_report.append(f"✅ {description}: {file_path} ({size} bytes)")
        else:
            validation_report.append(f"⚠️  {description}: {file_path} (vazio)")
    else:
        validation_report.append(f"❌ {description}: {file_path} (não encontrado)")

# Validar dados
if latency_data:
    validation_report.append(f"✅ Latência: {len(latency_data)} registros processados")
else:
    validation_report.append("❌ Latência: Nenhum dado processado")

if ml_predictions:
    validation_report.append(f"✅ ML: {len(ml_predictions)} predições processadas")
else:
    validation_report.append("⚠️  ML: Nenhuma predição encontrada")

# Salvar relatório de validação
validation_file = BASE_DIR / "15_integrity_and_diagnostics/validation_report.md"
with open(validation_file, 'w') as f:
    f.write("# Relatório de Validação\n\n")
    f.write(f"Data: {datetime.utcnow().isoformat()}Z\n\n")
    f.write("## Validação de Arquivos\n\n")
    for line in validation_report:
        f.write(f"{line}\n")

print("✅ Validação concluída")

print("\n" + "="*50)
print("✅ ANÁLISE DETALHADA CONCLUÍDA")
print("="*50)
print(f"📊 SLAs processados: {len(sla_files)}")
print(f"📊 Latências calculadas: {len(latencies)}")
print(f"📊 Predições ML: {len(ml_predictions)}")
print(f"📁 Diretório: {BASE_DIR}")
print("="*50)
