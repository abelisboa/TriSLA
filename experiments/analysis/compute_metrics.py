#!/usr/bin/env python3
"""
Análise de Métricas - TriSLA
Calcula métricas agregadas a partir de dados brutos

USO:
    python3 compute_metrics.py --scenario C1_eMBB_5

NOTAS:
    - Calcula tempo de decisão, tempo end-to-end, taxa de aceitação
    - Gera estatísticas simples (p50, p95, média)
    - NÃO faz inferência estatística avançada
    - NÃO descarta outliers
"""

import argparse
import json
import sys
import os
from datetime import datetime, timezone
from typing import Dict, Any, List
import statistics
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MetricsAnalyzer:
    """Analisador de métricas experimentais"""
    
    def __init__(self):
        """Inicializa o analisador"""
        self.analysis_results = {}
    
    def load_submissions(self, submissions_path: str) -> List[Dict[str, Any]]:
        """
        Carrega dados de submissões
        
        Args:
            submissions_path: Caminho para arquivo JSON de submissões
            
        Returns:
            Lista de submissões
        """
        try:
            with open(submissions_path, 'r') as f:
                data = json.load(f)
            return data.get('submissions', [])
        except Exception as e:
            logger.error(f"Erro ao carregar submissões: {e}")
            raise
    
    def load_prometheus_metrics(self, metrics_path: str) -> Dict[str, Any]:
        """
        Carrega métricas do Prometheus
        
        Args:
            metrics_path: Caminho para arquivo JSON de métricas
            
        Returns:
            Dados de métricas
        """
        try:
            with open(metrics_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar métricas: {e}")
            return {}
    
    def calculate_decision_time(self, submissions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calcula tempo de decisão
        
        Args:
            submissions: Lista de submissões
            
        Returns:
            Estatísticas de tempo de decisão
        """
        decision_times = []
        
        for submission in submissions:
            if submission.get('success') and submission.get('response'):
                response = submission['response']
                
                # Tentar extrair tempo de decisão da resposta
                # Ajustar conforme estrutura real da API
                decision_time = response.get('decision_time_ms') or response.get('processing_time_ms')
                
                if decision_time:
                    decision_times.append(float(decision_time))
        
        if not decision_times:
            return {"error": "Nenhum tempo de decisão encontrado"}
        
        return self._calculate_statistics(decision_times, "decision_time_ms")
    
    def calculate_end_to_end_time(self, submissions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calcula tempo end-to-end (submissão → decisão → registro)
        
        Args:
            submissions: Lista de submissões
            
        Returns:
            Estatísticas de tempo end-to-end
        """
        e2e_times = []
        
        for submission in submissions:
            if submission.get('success') and submission.get('response'):
                response = submission['response']
                
                # Tempo end-to-end pode estar na resposta ou ser calculado
                e2e_time = response.get('end_to_end_time_ms') or response.get('total_time_ms')
                
                if e2e_time:
                    e2e_times.append(float(e2e_time))
        
        if not e2e_times:
            return {"error": "Nenhum tempo end-to-end encontrado"}
        
        return self._calculate_statistics(e2e_times, "end_to_end_time_ms")
    
    def calculate_acceptance_rate(self, submissions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calcula taxa de aceitação/rejeição/renegociação
        
        Args:
            submissions: Lista de submissões
            
        Returns:
            Taxas de decisão
        """
        total = len(submissions)
        if total == 0:
            return {"error": "Nenhuma submissão encontrada"}
        
        successful = sum(1 for s in submissions if s.get('success'))
        failed = total - successful
        
        # Tentar extrair decisões das respostas
        accepted = 0
        rejected = 0
        renegotiated = 0
        
        for submission in submissions:
            if submission.get('success') and submission.get('response'):
                response = submission['response']
                action = response.get('action') or response.get('decision')
                
                if action in ['AC', 'ACCEPT', 'accept']:
                    accepted += 1
                elif action in ['REJ', 'REJECT', 'reject']:
                    rejected += 1
                elif action in ['RENEG', 'RENEGOTIATE', 'renegotiate']:
                    renegotiated += 1
        
        return {
            "total": total,
            "successful": successful,
            "failed": failed,
            "accepted": accepted,
            "rejected": rejected,
            "renegotiated": renegotiated,
            "acceptance_rate": (accepted / total * 100) if total > 0 else 0,
            "rejection_rate": (rejected / total * 100) if total > 0 else 0,
            "renegotiation_rate": (renegotiated / total * 100) if total > 0 else 0
        }
    
    def _calculate_statistics(self, values: List[float], metric_name: str) -> Dict[str, Any]:
        """
        Calcula estatísticas descritivas
        
        Args:
            values: Lista de valores
            metric_name: Nome da métrica
            
        Returns:
            Estatísticas (p50, p95, média, min, max)
        """
        if not values:
            return {"error": "Lista vazia"}
        
        sorted_values = sorted(values)
        n = len(sorted_values)
        
        # Percentis
        p50_idx = int(n * 0.50)
        p95_idx = int(n * 0.95)
        p99_idx = int(n * 0.99)
        
        stats = {
            "count": n,
            "min": min(values),
            "max": max(values),
            "mean": statistics.mean(values),
            "median": sorted_values[p50_idx] if p50_idx < n else sorted_values[-1],
            "p50": sorted_values[p50_idx] if p50_idx < n else sorted_values[-1],
            "p95": sorted_values[p95_idx] if p95_idx < n else sorted_values[-1],
            "p99": sorted_values[p99_idx] if p99_idx < n else sorted_values[-1],
            "std_dev": statistics.stdev(values) if n > 1 else 0
        }
        
        return stats
    
    def analyze(self, submissions_path: str, metrics_path: str = None) -> Dict[str, Any]:
        """
        Executa análise completa
        
        Args:
            submissions_path: Caminho para submissões
            metrics_path: Caminho opcional para métricas do Prometheus
            
        Returns:
            Resultados da análise
        """
        logger.info("Carregando dados de submissões")
        submissions = self.load_submissions(submissions_path)
        
        logger.info(f"Analisando {len(submissions)} submissões")
        
        analysis = {
            "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
            "submissions_count": len(submissions),
            "decision_time": self.calculate_decision_time(submissions),
            "end_to_end_time": self.calculate_end_to_end_time(submissions),
            "acceptance_rate": self.calculate_acceptance_rate(submissions)
        }
        
        # Adicionar métricas do Prometheus se disponível
        if metrics_path:
            logger.info("Carregando métricas do Prometheus")
            prometheus_data = self.load_prometheus_metrics(metrics_path)
            analysis["prometheus_metrics"] = prometheus_data
        
        return analysis
    
    def save_analysis(self, analysis: Dict[str, Any], output_path: str):
        """
        Salva resultados da análise
        
        Args:
            analysis: Resultados da análise
            output_path: Caminho de saída
        """
        with open(output_path, 'w') as f:
            json.dump(analysis, f, indent=2)
        logger.info(f"Análise salva em: {output_path}")


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='Analisa métricas experimentais')
    parser.add_argument('--scenario', required=True, help='ID do cenário (ex: C1_eMBB_5)')
    parser.add_argument('--submissions', help='Arquivo JSON de submissões', default=None)
    parser.add_argument('--metrics', help='Arquivo JSON de métricas Prometheus', default=None)
    parser.add_argument('--output-dir', default='experiments/data/analysis', help='Diretório de saída')
    
    args = parser.parse_args()
    
    # Criar analisador
    analyzer = MetricsAnalyzer()
    
    # Encontrar arquivos se não especificados
    if not args.submissions:
        # Procurar arquivo mais recente do cenário
        data_dir = "experiments/data/raw"
        import glob
        pattern = f"{data_dir}/submissions_{args.scenario}_*.json"
        files = glob.glob(pattern)
        if files:
            args.submissions = max(files, key=os.path.getctime)
        else:
            logger.error(f"Nenhum arquivo de submissões encontrado para {args.scenario}")
            sys.exit(1)
    
    # Executar análise
    try:
        analysis = analyzer.analyze(args.submissions, args.metrics)
        
        # Criar diretório de saída
        os.makedirs(args.output_dir, exist_ok=True)
        
        # Gerar nome de arquivo
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(args.output_dir, f"analysis_{args.scenario}_{timestamp}.json")
        
        # Salvar
        analyzer.save_analysis(analysis, output_path)
        
        # Resumo
        print(f"\n=== RESUMO DA ANÁLISE ===")
        print(f"Cenário: {args.scenario}")
        print(f"Submissões analisadas: {analysis['submissions_count']}")
        
        if 'error' not in analysis['decision_time']:
            dt = analysis['decision_time']
            print(f"\nTempo de Decisão (ms):")
            print(f"  Média: {dt['mean']:.2f}")
            print(f"  P50: {dt['p50']:.2f}")
            print(f"  P95: {dt['p95']:.2f}")
        
        if 'error' not in analysis['end_to_end_time']:
            e2e = analysis['end_to_end_time']
            print(f"\nTempo End-to-End (ms):")
            print(f"  Média: {e2e['mean']:.2f}")
            print(f"  P50: {e2e['p50']:.2f}")
            print(f"  P95: {e2e['p95']:.2f}")
        
        ar = analysis['acceptance_rate']
        print(f"\nTaxa de Aceitação:")
        print(f"  Aceitos: {ar.get('accepted', 0)} ({ar.get('acceptance_rate', 0):.1f}%)")
        print(f"  Rejeitados: {ar.get('rejected', 0)} ({ar.get('rejection_rate', 0):.1f}%)")
        print(f"  Renegociados: {ar.get('renegotiated', 0)} ({ar.get('renegotiation_rate', 0):.1f}%)")
        
        print(f"\nAnálise salva em: {output_path}")
        
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Erro na análise: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

