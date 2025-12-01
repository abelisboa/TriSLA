#!/usr/bin/env python3
"""
FASE 2: Normalização e conversão JSONL → CSV
Converte todos os arquivos JSONL de tests/results/ para CSV normalizado
"""

import json
import csv
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import re

# Diretórios (relativos à raiz do repositório)
SCRIPT_DIR = Path(__file__).parent.parent.parent
RESULTS_DIR = SCRIPT_DIR / "tests" / "results"
CSV_DIR = SCRIPT_DIR / "analysis" / "csv"

# Criar diretório CSV se não existir
CSV_DIR.mkdir(parents=True, exist_ok=True)

# Esquema canônico de campos
CANONICAL_FIELDS = [
    'intent_id',
    'service_type',           # URLLC, eMBB, mMTC, basic
    'scenario',               # BASIC, URLLC_BATCH, MIXED_135
    'created_at',             # timestamp
    'timestamp_received',
    'timestamp_decision',
    'timestamp_completed',
    'status_final',           # ACCEPTED, RENEGOTIATED, REJECTED, ERROR
    'latency_total_ms',
    'latency_sem_csmf_ms',
    'latency_ml_nsmf_ms',
    'latency_decision_engine_ms',
    'latency_bc_nssmf_ms',
    'error_type',
    'error_message',
    'nest_id',
    'bert',                   # Bit Error Rate (se disponível)
    'ber',                    # Alternativa para BERT
    'source_file',            # Arquivo de origem
]


def detect_scenario(filename: str) -> str:
    """Detecta o cenário baseado no nome do arquivo"""
    filename_lower = filename.lower()
    
    if 'basic' in filename_lower:
        return 'BASIC'
    elif 'urlcc' in filename_lower or 'urllc' in filename_lower:
        return 'URLLC_BATCH'
    elif 'mixed' in filename_lower and '135' in filename_lower:
        return 'MIXED_135'
    else:
        return 'UNKNOWN'


def detect_service_type(record: Dict, scenario: str) -> str:
    """Detecta o tipo de serviço baseado no registro ou cenário"""
    # Tentar extrair do registro
    service_type = record.get('service_type') or record.get('type') or record.get('slice_type')
    
    if service_type:
        return str(service_type).upper()
    
    # Inferir do cenário
    if scenario == 'URLLC_BATCH':
        return 'URLLC'
    elif scenario == 'BASIC':
        return 'BASIC'  # Pode ser misto, mas marcamos como basic
    else:
        return 'UNKNOWN'


def normalize_timestamp(value: Any) -> Optional[str]:
    """Normaliza timestamp para formato ISO"""
    if not value:
        return None
    
    if isinstance(value, (int, float)):
        # Timestamp Unix
        try:
            return datetime.fromtimestamp(value).isoformat()
        except (ValueError, OSError):
            return None
    
    if isinstance(value, str):
        # Já está em formato string
        return value
    
    return None


def extract_latency(record: Dict, key_variations: List[str]) -> Optional[float]:
    """Extrai latência tentando várias variações de chaves"""
    for key in key_variations:
        value = record.get(key)
        if value is not None:
            try:
                return float(value)
            except (ValueError, TypeError):
                continue
    return None


def normalize_record(record: Dict, source_file: str, scenario: str) -> Dict:
    """
    Normaliza um registro JSON para o esquema canônico
    
    Mapeamento de campos:
    - status → status_final
    - message → error_message (se status != accepted)
    - total_latency_ms → latency_total_ms
    - sem_latency → latency_sem_csmf_ms
    - ml_latency → latency_ml_nsmf_ms
    - de_latency → latency_decision_engine_ms
    - bc_latency → latency_bc_nssmf_ms
    """
    normalized = {field: None for field in CANONICAL_FIELDS}
    
    # Campos diretos
    normalized['intent_id'] = record.get('intent_id') or record.get('id')
    normalized['nest_id'] = record.get('nest_id')
    normalized['source_file'] = source_file
    normalized['scenario'] = scenario
    
    # Status
    status = record.get('status') or record.get('status_final') or record.get('decision_status')
    if status:
        status_upper = str(status).upper()
        # Normalizar variações
        if 'accept' in status_upper:
            normalized['status_final'] = 'ACCEPTED'
        elif 'renegot' in status_upper or 'renog' in status_upper:
            normalized['status_final'] = 'RENEGOTIATED'
        elif 'reject' in status_upper:
            normalized['status_final'] = 'REJECTED'
        elif 'error' in status_upper or 'fail' in status_upper:
            normalized['status_final'] = 'ERROR'
        else:
            normalized['status_final'] = status_upper
    
    # Service type
    normalized['service_type'] = detect_service_type(record, scenario)
    
    # Timestamps
    normalized['created_at'] = normalize_timestamp(
        record.get('created_at') or record.get('timestamp') or record.get('ts')
    )
    normalized['timestamp_received'] = normalize_timestamp(
        record.get('timestamp_received') or record.get('received') or record.get('ts_received')
    )
    normalized['timestamp_decision'] = normalize_timestamp(
        record.get('timestamp_decision') or record.get('decision') or record.get('ts_decision')
    )
    normalized['timestamp_completed'] = normalize_timestamp(
        record.get('timestamp_completed') or record.get('completed') or record.get('ts_completed')
    )
    
    # Latências
    normalized['latency_total_ms'] = extract_latency(record, [
        'latency_total_ms', 'total_latency', 'latency', 'total_ms',
        'latency_ms', 'total_latency_ms'
    ])
    
    normalized['latency_sem_csmf_ms'] = extract_latency(record, [
        'latency_sem_csmf_ms', 'sem_csmf_latency', 'sem_latency',
        'sem_csmf_ms', 'sem_latency_ms'
    ])
    
    normalized['latency_ml_nsmf_ms'] = extract_latency(record, [
        'latency_ml_nsmf_ms', 'ml_nsmf_latency', 'ml_latency',
        'ml_nsmf_ms', 'ml_latency_ms'
    ])
    
    normalized['latency_decision_engine_ms'] = extract_latency(record, [
        'latency_decision_engine_ms', 'decision_latency', 'de_latency',
        'decision_engine_ms', 'de_latency_ms', 'decision_ms'
    ])
    
    normalized['latency_bc_nssmf_ms'] = extract_latency(record, [
        'latency_bc_nssmf_ms', 'bc_nssmf_latency', 'bc_latency',
        'bc_nssmf_ms', 'bc_latency_ms', 'blockchain_latency_ms'
    ])
    
    # Calcular latência total se não existir mas houver latências parciais
    if normalized['latency_total_ms'] is None:
        latencies = [
            normalized['latency_sem_csmf_ms'],
            normalized['latency_ml_nsmf_ms'],
            normalized['latency_decision_engine_ms'],
            normalized['latency_bc_nssmf_ms'],
        ]
        if any(l is not None for l in latencies):
            normalized['latency_total_ms'] = sum(l for l in latencies if l is not None)
    
    # Erros
    error_message = record.get('message') or record.get('error_message') or record.get('error')
    if error_message:
        normalized['error_message'] = str(error_message)
        # Tentar extrair tipo de erro
        error_str = str(error_message).upper()
        if 'GRPC' in error_str or 'RPC' in error_str:
            normalized['error_type'] = 'GRPC_ERROR'
        elif 'TIMEOUT' in error_str:
            normalized['error_type'] = 'TIMEOUT'
        elif 'CONNECTION' in error_str or 'REFUSED' in error_str:
            normalized['error_type'] = 'CONNECTION_ERROR'
        elif 'KAFKA' in error_str:
            normalized['error_type'] = 'KAFKA_ERROR'
        else:
            normalized['error_type'] = 'UNKNOWN_ERROR'
    
    # BERT/BER
    normalized['bert'] = record.get('bert') or record.get('bit_error_rate')
    normalized['ber'] = record.get('ber') or normalized['bert']
    
    return normalized


def load_jsonl_files() -> Dict[str, List[Dict]]:
    """Carrega todos os arquivos JSONL de tests/results/"""
    files_data = {}
    
    if not RESULTS_DIR.exists():
        print(f"⚠️ Diretório {RESULTS_DIR} não encontrado!")
        return files_data
    
    jsonl_files = sorted(RESULTS_DIR.glob("*.jsonl"))
    
    if not jsonl_files:
        print(f"⚠️ Nenhum arquivo .jsonl encontrado em {RESULTS_DIR}")
        return files_data
    
    print(f"\n📂 Encontrados {len(jsonl_files)} arquivos JSONL:")
    
    for jsonl_file in jsonl_files:
        # Pular arquivos vazios
        if jsonl_file.stat().st_size == 0:
            print(f"   ⚠️ {jsonl_file.name} está vazio, pulando...")
            continue
        
        data = []
        scenario = detect_scenario(jsonl_file.name)
        
        try:
            with open(jsonl_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        record = json.loads(line)
                        normalized = normalize_record(record, jsonl_file.name, scenario)
                        data.append(normalized)
                    except json.JSONDecodeError as e:
                        print(f"      ⚠️ Erro na linha {line_num} de {jsonl_file.name}: {e}")
            
            if data:
                files_data[jsonl_file.stem] = {
                    'data': data,
                    'scenario': scenario,
                    'filename': jsonl_file.name
                }
                print(f"   ✅ {jsonl_file.name}: {len(data)} registros (cenário: {scenario})")
            
        except Exception as e:
            print(f"   ❌ Erro ao ler {jsonl_file.name}: {e}")
    
    return files_data


def save_csv(files_data: Dict[str, Dict], output_consolidated: bool = True):
    """Salva CSVs normalizados"""
    
    # CSV consolidado com todos os intents
    if output_consolidated:
        all_records = []
        for file_stem, file_info in files_data.items():
            all_records.extend(file_info['data'])
        
        if all_records:
            csv_path = CSV_DIR / "merged_all_intents.csv"
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=CANONICAL_FIELDS)
                writer.writeheader()
                writer.writerows(all_records)
            print(f"\n✅ CSV consolidado criado: {csv_path} ({len(all_records)} registros)")
    
    # CSVs por cenário
    scenarios_data = {}
    for file_stem, file_info in files_data.items():
        scenario = file_info['scenario']
        if scenario not in scenarios_data:
            scenarios_data[scenario] = []
        scenarios_data[scenario].extend(file_info['data'])
    
    for scenario, records in scenarios_data.items():
        if records:
            csv_path = CSV_DIR / f"merged_{scenario.lower()}.csv"
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=CANONICAL_FIELDS)
                writer.writeheader()
                writer.writerows(records)
            print(f"✅ CSV por cenário criado: {csv_path} ({len(records)} registros)")


def main():
    """Função principal"""
    print("=" * 60)
    print("🟩 FASE 2 — NORMALIZAÇÃO E CONVERSÃO JSONL → CSV")
    print("=" * 60)
    
    # Carregar arquivos
    files_data = load_jsonl_files()
    
    if not files_data:
        print("\n❌ Nenhum arquivo carregado. Encerrando.")
        return
    
    # Salvar CSVs
    save_csv(files_data)
    
    print("\n✅ Normalização concluída!")
    print(f"📁 Arquivos CSV salvos em: {CSV_DIR}")


if __name__ == "__main__":
    main()

