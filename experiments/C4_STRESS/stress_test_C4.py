#!/usr/bin/env python3
"""
TriSLA — Cenário C4: Stress Test
Pasta de execução: /home/porvir5g/gtp5g/trisla/experiments/C4_STRESS

Este script DEVE ser executado a partir da pasta acima.
NÃO modifica código produtivo.
Avalia comportamento sob carga extrema (100, 200, 500 SLAs simultâneos).
"""

import os
import sys
import csv
import time
import uuid
import json
import argparse
import requests
import logging
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, List

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API endpoint (ajustar conforme necessário)
DEFAULT_API_URL = os.getenv('TRISLA_API_URL', 'http://192.168.10.16:32002')


class StressTestC4:
    """Classe para execução de stress test C4"""
    
    def __init__(self, api_url: str = None, max_workers: int = 50):
        """
        Inicializa o stress test
        
        Args:
            api_url: URL da API do TriSLA
            max_workers: Número máximo de threads paralelas
        """
        self.api_url = api_url or DEFAULT_API_URL
        self.max_workers = max_workers
        self.results = []
    
    def generate_sla_payload(self, scenario_id: str, sla_index: int) -> tuple:
        """
        Gera payload de SLA sintético para stress test
        
        Args:
            scenario_id: ID do cenário (C4_100, C4_200, C4_500)
            sla_index: Índice do SLA
            
        Returns:
            Tupla (payload, correlation_id)
        """
        correlation_id = f"{scenario_id}-{sla_index}-{uuid.uuid4().hex[:8]}"
        
        # Payload baseado na API do TriSLA (formato C1/C2)
        payload = {
            "template_id": "template:eMBB",
            "form_values": {
                "service_type": "eMBB",
                "latency_ms": 50.0,
                "throughput_mbps": 100.0,
                "reliability": 0.99,
                "jitter_ms": 10.0
            },
            "tenant_id": f"stress-test-{scenario_id}"
        }
        
        return payload, correlation_id
    
    def submit_single_sla(self, scenario_id: str, sla_index: int) -> Dict[str, Any]:
        """
        Submete um único SLA e retorna métricas
        
        Args:
            scenario_id: ID do cenário
            sla_index: Índice do SLA
            
        Returns:
            Dicionário com métricas da submissão
        """
        payload, correlation_id = self.generate_sla_payload(scenario_id, sla_index)
        
        result = {
            "correlation_id": correlation_id,
            "scenario_id": scenario_id,
            "sla_index": sla_index,
            "start_timestamp": datetime.now(timezone.utc).isoformat(),
            "start_ts_ms": int(time.time() * 1000),
            "success": False,
            "http_code": None,
            "error": None,
            "end_timestamp": None,
            "end_ts_ms": None,
            "duration_ms": None,
            "response": None
        }
        
        try:
            endpoint = f"{self.api_url}/api/v1/sla/submit"
            
            response = requests.post(
                endpoint,
                json=payload,
                timeout=60,
                headers={"Content-Type": "application/json"}
            )
            
            result["end_timestamp"] = datetime.now(timezone.utc).isoformat()
            result["end_ts_ms"] = int(time.time() * 1000)
            result["duration_ms"] = result["end_ts_ms"] - result["start_ts_ms"]
            result["http_code"] = response.status_code
            
            if response.status_code in [200, 201, 202]:
                result["success"] = True
                try:
                    result["response"] = response.json()
                except:
                    result["response"] = response.text
            else:
                result["error"] = f"HTTP {response.status_code}: {response.text[:200]}"
                
        except requests.exceptions.Timeout:
            result["error"] = "Timeout"
            result["end_timestamp"] = datetime.now(timezone.utc).isoformat()
            result["end_ts_ms"] = int(time.time() * 1000)
            result["duration_ms"] = result["end_ts_ms"] - result["start_ts_ms"]
        except Exception as e:
            result["error"] = str(e)
            result["end_timestamp"] = datetime.now(timezone.utc).isoformat()
            result["end_ts_ms"] = int(time.time() * 1000)
            if result["start_ts_ms"]:
                result["duration_ms"] = result["end_ts_ms"] - result["start_ts_ms"]
        
        return result
    
    def run_stress_test(self, total_slas: int, scenario_id: str = None) -> List[Dict[str, Any]]:
        """
        Executa stress test com paralelismo controlado
        
        Args:
            total_slas: Número total de SLAs a submeter
            scenario_id: ID do cenário (padrão: C4_{total_slas})
            
        Returns:
            Lista com resultados de todas as submissões
        """
        if scenario_id is None:
            scenario_id = f"C4_{total_slas}"
        
        logger.info(f"Iniciando stress test: {scenario_id} ({total_slas} SLAs simultâneos)")
        logger.info(f"Paralelismo: {self.max_workers} threads")
        
        start_time = time.time()
        results = []
        
        # Executar submissões em paralelo
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self.submit_single_sla, scenario_id, i+1): i+1
                for i in range(total_slas)
            }
            
            completed = 0
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                    completed += 1
                    if completed % 10 == 0:
                        logger.info(f"Progresso: {completed}/{total_slas} SLAs submetidos")
                except Exception as e:
                    logger.error(f"Erro ao processar submissão: {e}")
                    results.append({
                        "correlation_id": f"{scenario_id}-{futures[future]}-error",
                        "scenario_id": scenario_id,
                        "sla_index": futures[future],
                        "success": False,
                        "error": str(e)
                    })
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        logger.info(f"Stress test concluído: {scenario_id}")
        logger.info(f"Duração total: {total_duration:.2f}s")
        logger.info(f"SLAs processados: {len(results)}")
        
        return results
    
    def save_results_csv(self, results: List[Dict[str, Any]], output_file: str):
        """
        Salva resultados em CSV
        
        Args:
            results: Lista de resultados
            output_file: Caminho do arquivo CSV
        """
        if not results:
            logger.warning("Nenhum resultado para salvar")
            return
        
        fieldnames = [
            "correlation_id", "scenario_id", "sla_index",
            "start_timestamp", "start_ts_ms",
            "end_timestamp", "end_ts_ms", "duration_ms",
            "success", "http_code", "error"
        ]
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for result in results:
                row = {field: result.get(field, '') for field in fieldnames}
                writer.writerow(row)
        
        logger.info(f"Resultados CSV salvos em: {output_file}")
    
    def save_results_json(self, results: List[Dict[str, Any]], output_file: str):
        """
        Salva resultados em JSON com estatísticas
        
        Args:
            results: Lista de resultados
            output_file: Caminho do arquivo JSON
        """
        successful = [r for r in results if r.get('success', False)]
        failed = [r for r in results if not r.get('success', False)]
        
        durations = [r.get('duration_ms', 0) for r in results if r.get('duration_ms')]
        
        stats = {
            "total": len(results),
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": len(successful) / len(results) * 100 if results else 0,
            "failure_rate": len(failed) / len(results) * 100 if results else 0,
            "duration_stats": {
                "min": min(durations) if durations else 0,
                "max": max(durations) if durations else 0,
                "avg": sum(durations) / len(durations) if durations else 0
            }
        }
        
        output_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "scenario_id": results[0].get('scenario_id') if results else 'unknown',
            "statistics": stats,
            "results": results
        }
        
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        logger.info(f"Resultados JSON salvos em: {output_file}")
        logger.info(f"Estatísticas: {stats['successful']}/{stats['total']} sucessos ({stats['success_rate']:.1f}%)")


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='Stress Test C4 - TriSLA')
    parser.add_argument('--scenario', choices=['100', '200', '500', 'all'], 
                       default='all', help='Cenário a executar')
    parser.add_argument('--api-url', help='URL da API do TriSLA', default=None)
    parser.add_argument('--max-workers', type=int, default=50, 
                       help='Número máximo de threads paralelas')
    parser.add_argument('--output-dir', default='.', 
                       help='Diretório para salvar resultados')
    
    args = parser.parse_args()
    
    # Verificar se estamos no diretório correto
    current_dir = os.getcwd()
    if not current_dir.endswith('C4_STRESS'):
        logger.warning(f"Atenção: Executando fora de C4_STRESS. Diretório atual: {current_dir}")
    
    # Criar instância do stress test
    stress_test = StressTestC4(api_url=args.api_url, max_workers=args.max_workers)
    
    scenarios = []
    if args.scenario == 'all':
        scenarios = [100, 200, 500]
    else:
        scenarios = [int(args.scenario)]
    
    for total_slas in scenarios:
        scenario_id = f"C4_{total_slas}"
        logger.info(f"\n{'='*60}")
        logger.info(f"Executando: {scenario_id}")
        logger.info(f"{'='*60}")
        
        # Executar stress test
        results = stress_test.run_stress_test(total_slas, scenario_id)
        
        # Salvar resultados
        csv_file = os.path.join(args.output_dir, f"results_C4_{total_slas}.csv")
        json_file = os.path.join(args.output_dir, f"results_C4_{total_slas}.json")
        
        stress_test.save_results_csv(results, csv_file)
        stress_test.save_results_json(results, json_file)
        
        logger.info(f"\nCenário {scenario_id} concluído\n")


if __name__ == '__main__':
    main()
