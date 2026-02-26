#!/usr/bin/env python3
from typing import Dict
"""
Coletor de Logs - TriSLA
Coleta logs via kubectl preservando timestamps

USO:
    python3 logs_collector.py --scenario C1_eMBB_5

NOTAS:
    - Preserva timestamps originais
    - Preserva pod name
    - Salva logs brutos em arquivos
"""

import argparse
import subprocess
import sys
import os
from datetime import datetime, timezone
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LogsCollector:
    """Coletor de logs do Kubernetes"""
    
    def __init__(self, namespace: str = "trisla-experiments"):
        """
        Inicializa o coletor
        
        Args:
            namespace: Namespace do Kubernetes
        """
        self.namespace = namespace
        self.components = [
            "decision-engine",
            "ml-nsmf",
            "sem-csmf",
            "bc-nssmf"
        ]
    
    def collect_component_logs(self, component: str, time_range_minutes: int = 30) -> str:
        """
        Coleta logs de um componente específico
        
        Args:
            component: Nome do componente
            time_range_minutes: Janela de tempo em minutos
            
        Returns:
            Logs brutos como string
        """
        # Construir comando kubectl
        # Buscar pods do componente
        pod_label = f"app=trisla-{component}"
        
        try:
            # Listar pods
            list_cmd = [
                "kubectl", "get", "pods",
                "-n", self.namespace,
                "-l", pod_label,
                "-o", "jsonpath={.items[*].metadata.name}"
            ]
            
            result = subprocess.run(
                list_cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                logger.warning(f"Erro ao listar pods de {component}: {result.stderr}")
                return ""
            
            pod_names = result.stdout.strip().split()
            
            if not pod_names:
                logger.warning(f"Nenhum pod encontrado para {component}")
                return ""
            
            # Coletar logs de cada pod
            all_logs = []
            
            for pod_name in pod_names:
                logger.info(f"Coletando logs do pod: {pod_name}")
                
                # Comando kubectl logs com timestamps
                logs_cmd = [
                    "kubectl", "logs",
                    "-n", self.namespace,
                    pod_name,
                    "--timestamps=true",
                    f"--since={time_range_minutes}m"
                ]
                
                result = subprocess.run(
                    logs_cmd,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0:
                    # Adicionar header com pod name
                    header = f"\n{'='*80}\n"
                    header += f"POD: {pod_name}\n"
                    header += f"COMPONENT: {component}\n"
                    header += f"{'='*80}\n\n"
                    all_logs.append(header + result.stdout)
                else:
                    logger.warning(f"Erro ao coletar logs de {pod_name}: {result.stderr}")
            
            return "\n".join(all_logs)
            
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout ao coletar logs de {component}")
            return ""
        except Exception as e:
            logger.error(f"Erro ao coletar logs de {component}: {e}")
            return ""
    
    def collect_all_logs(self, components: list = None, time_range_minutes: int = 30) -> Dict[str, str]:
        """
        Coleta logs de todos os componentes
        
        Args:
            components: Lista de componentes (padrão: todos)
            time_range_minutes: Janela de tempo
            
        Returns:
            Dicionário com logs de cada componente
        """
        if components is None:
            components = self.components
        
        logger.info(f"Coletando logs de {len(components)} componentes (janela: {time_range_minutes}min)")
        
        all_logs = {}
        
        for component in components:
            logger.info(f"Coletando logs de: {component}")
            logs = self.collect_component_logs(component, time_range_minutes)
            all_logs[component] = logs
        
        return all_logs
    
    def save_logs(self, logs: Dict[str, str], output_path: str):
        """
        Salva logs em arquivo
        
        Args:
            logs: Dicionário com logs por componente
            output_path: Caminho do arquivo de saída
        """
        with open(output_path, 'w') as f:
            # Header
            f.write(f"# Logs Coletados - {datetime.now(timezone.utc).isoformat()}\n")
            f.write(f"# Namespace: {self.namespace}\n")
            f.write(f"# Componentes: {', '.join(logs.keys())}\n")
            f.write(f"\n{'='*80}\n\n")
            
            # Logs de cada componente
            for component, log_content in logs.items():
                if log_content:
                    f.write(f"\n{'='*80}\n")
                    f.write(f"COMPONENTE: {component}\n")
                    f.write(f"{'='*80}\n\n")
                    f.write(log_content)
                    f.write(f"\n\n")
        
        logger.info(f"Logs salvos em: {output_path}")


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='Coleta logs do Kubernetes')
    parser.add_argument('--scenario', required=True, help='ID do cenário (ex: C1_eMBB_5)')
    parser.add_argument('--namespace', default='trisla-experiments', help='Namespace do Kubernetes')
    parser.add_argument('--time-range', type=int, default=30, help='Janela de tempo em minutos')
    parser.add_argument('--components', nargs='+', help='Componentes específicos (padrão: todos)')
    parser.add_argument('--output-dir', default='experiments/data/raw', help='Diretório de saída')
    
    args = parser.parse_args()
    
    # Criar coletor
    collector = LogsCollector(namespace=args.namespace)
    
    # Coletar logs
    try:
        components = args.components or collector.components
        logs = collector.collect_all_logs(components, args.time_range)
        
        # Criar diretório de saída
        os.makedirs(args.output_dir, exist_ok=True)
        
        # Gerar nome de arquivo
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(args.output_dir, f"logs_{args.scenario}_{timestamp}.txt")
        
        # Salvar
        collector.save_logs(logs, output_path)
        
        # Resumo
        total_size = sum(len(content) for content in logs.values())
        components_with_logs = sum(1 for content in logs.values() if content)
        
        print(f"\n=== RESUMO ===")
        print(f"Cenário: {args.scenario}")
        print(f"Componentes coletados: {components_with_logs}/{len(logs)}")
        print(f"Tamanho total: {total_size} caracteres")
        print(f"Logs salvos em: {output_path}")
        
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Erro na coleta: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

