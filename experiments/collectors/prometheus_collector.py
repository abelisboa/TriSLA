#!/usr/bin/env python3
"""
Coletor de Métricas do Prometheus - TriSLA
Coleta métricas brutas do Prometheus sem agregação

USO:
    python3 prometheus_collector.py --scenario C1_eMBB_5

NOTAS:
    - NÃO agrega dados
    - NÃO aplica filtros
    - Exporta dados brutos em JSON/CSV
"""

import argparse
import json
import csv
import sys
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
import requests
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PrometheusCollector:
    """Coletor de métricas do Prometheus"""
    
    def __init__(self, prometheus_url: str = None):
        """
        Inicializa o coletor
        
        Args:
            prometheus_url: URL do Prometheus (padrão: http://10.233.24.185:9090)
        """
        self.prometheus_url = prometheus_url or os.getenv(
            "PROMETHEUS_URL", 
            "http://10.233.24.185:9090"
        )
        self.metrics_data = []
    
    def query_prometheus(self, query: str, time_range_minutes: int = 30) -> List[Dict[str, Any]]:
        """
        Consulta métrica no Prometheus via API
        
        Args:
            query: Query PromQL
            time_range_minutes: Janela de tempo em minutos
            
        Returns:
            Lista de séries temporais retornadas
        """
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(minutes=time_range_minutes)
        
        params = {
            "query": query,
            "start": start_time.timestamp(),
            "end": end_time.timestamp(),
            "step": "15s"  # Resolução de 15 segundos
        }
        
        try:
            response = requests.get(
                f"{self.prometheus_url}/api/v1/query_range",
                params=params,
                timeout=60
            )
            response.raise_for_status()
            
            data = response.json()
            if data['status'] == 'success':
                return data['data']['result']
            else:
                logger.error(f"Erro na query Prometheus: {data.get('error', 'Unknown')}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao consultar Prometheus: {e}")
            return []
    
    def collect_metrics(self, metric_names: List[str], time_range_minutes: int = 30) -> Dict[str, Any]:
        """
        Coleta múltiplas métricas
        
        Args:
            metric_names: Lista de nomes de métricas
            time_range_minutes: Janela de tempo
            
        Returns:
            Dicionário com dados brutos de todas as métricas
        """
        logger.info(f"Coletando {len(metric_names)} métricas (janela: {time_range_minutes}min)")
        
        collected_data = {
            "collection_timestamp": datetime.now(timezone.utc).isoformat(),
            "time_range_minutes": time_range_minutes,
            "metrics": {}
        }
        
        for metric_name in metric_names:
            logger.info(f"Coletando métrica: {metric_name}")
            
            # Query PromQL simples (ajustar conforme métricas reais)
            query = metric_name
            
            series = self.query_prometheus(query, time_range_minutes)
            
            collected_data["metrics"][metric_name] = {
                "series_count": len(series),
                "data": series
            }
            
            logger.info(f"Métrica {metric_name}: {len(series)} séries coletadas")
        
        return collected_data
    
    def save_json(self, data: Dict[str, Any], output_path: str):
        """Salva dados em JSON"""
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Dados salvos em JSON: {output_path}")
    
    def save_csv(self, data: Dict[str, Any], output_path: str):
        """
        Salva dados em CSV (formato simplificado)
        Cada métrica vira uma linha com timestamps e valores
        """
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Cabeçalho
            writer.writerow(['metric_name', 'timestamp', 'value', 'labels'])
            
            # Dados
            for metric_name, metric_data in data['metrics'].items():
                for series in metric_data['data']:
                    metric = series.get('metric', {})
                    values = series.get('values', [])
                    
                    for timestamp, value in values:
                        labels_str = json.dumps(metric)
                        writer.writerow([metric_name, timestamp, value, labels_str])
        
        logger.info(f"Dados salvos em CSV: {output_path}")


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='Coleta métricas do Prometheus')
    parser.add_argument('--scenario', required=True, help='ID do cenário (ex: C1_eMBB_5)')
    parser.add_argument('--prometheus-url', help='URL do Prometheus', default=None)
    parser.add_argument('--time-range', type=int, default=30, help='Janela de tempo em minutos')
    parser.add_argument('--format', choices=['json', 'csv', 'both'], default='both', help='Formato de saída')
    parser.add_argument('--output-dir', default='experiments/data/raw', help='Diretório de saída')
    
    args = parser.parse_args()
    
    # Métricas padrão (ajustar conforme métricas reais do TriSLA)
    default_metrics = [
        "trisla_decision_engine_decisions_total",
        "trisla_decision_engine_decision_duration_seconds",
        "trisla_ml_nsmf_predictions_total",
        "trisla_sem_csmf_intents_processed_total"
    ]
    
    # Criar coletor
    collector = PrometheusCollector(prometheus_url=args.prometheus_url)
    
    # Coletar métricas
    try:
        data = collector.collect_metrics(default_metrics, args.time_range)
        
        # Criar diretório de saída
        os.makedirs(args.output_dir, exist_ok=True)
        
        # Gerar nome de arquivo
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        base_name = f"metrics_{args.scenario}_{timestamp}"
        
        # Salvar
        if args.format in ['json', 'both']:
            json_path = os.path.join(args.output_dir, f"{base_name}.json")
            collector.save_json(data, json_path)
        
        if args.format in ['csv', 'both']:
            csv_path = os.path.join(args.output_dir, f"{base_name}.csv")
            collector.save_csv(data, csv_path)
        
        # Resumo
        total_series = sum(m['series_count'] for m in data['metrics'].values())
        print(f"\n=== RESUMO ===")
        print(f"Cenário: {args.scenario}")
        print(f"Métricas coletadas: {len(data['metrics'])}")
        print(f"Total de séries: {total_series}")
        print(f"Janela de tempo: {args.time_range} minutos")
        
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Erro na coleta: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

