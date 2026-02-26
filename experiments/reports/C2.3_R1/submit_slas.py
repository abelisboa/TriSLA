#!/usr/bin/env python3
"""
Script de Geração de Carga Experimental - TriSLA
Submete SLAs sintéticos conforme template YAML

USO:
    python3 submit_slas.py templates/C1_eMBB_5.yaml

NOTAS:
    - NÃO faz retries automáticos
    - NÃO paraleliza por padrão
    - Gera correlation_id único por SLA
    - Registra timestamps client-side
"""

import yaml
import json
import time
import uuid
import sys
import os
import argparse
from datetime import datetime, timezone
from typing import Dict, Any, List
import requests
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SLASubmitter:
    """Classe para submeter SLAs experimentais"""
    
    def __init__(self, api_url: str = None):
        """
        Inicializa o submissor de SLAs
        
        Args:
            api_url: URL base da API do TriSLA (padrão: http://192.168.10.16:32002)
        """
        self.api_url = api_url or os.getenv("TRISLA_API_URL", "http://192.168.10.16:32002")
        self.submissions = []  # Armazena resultados das submissões
    
    def load_template(self, template_path: str) -> Dict[str, Any]:
        """
        Carrega template YAML
        
        Args:
            template_path: Caminho para o arquivo YAML
            
        Returns:
            Dicionário com configuração do template
        """
        try:
            with open(template_path, 'r') as f:
                template = yaml.safe_load(f)
            logger.info(f"Template carregado: {template.get('scenario_id')}")
            return template
        except Exception as e:
            logger.error(f"Erro ao carregar template: {e}")
            raise
    
    def generate_sla_payload(self, template: Dict[str, Any], sla_index: int) -> Dict[str, Any]:
        """
        Gera payload de SLA sintético baseado no template
        
        Args:
            template: Configuração do template
            sla_index: Índice do SLA (para variação sintética)
            
        Returns:
            Payload JSON para submissão (formato: template_id + form_values)
        """
        sla_profile = template['sla_profile']
        qos = sla_profile['qos_requirements']
        
        # Gerar correlation_id único
        correlation_id = f"{template['scenario_id']}-{sla_index}-{uuid.uuid4().hex[:8]}"
        
        # Payload no formato esperado pela API /api/v1/sla/submit
        # Formato: {template_id, form_values, tenant_id}
        payload = {
            "template_id": f"template:{sla_profile['type']}",
            "form_values": {
                "service_type": sla_profile['type'],
                "latency_ms": float(str(qos['latency']).replace('ms', '').strip()),
                "throughput_mbps": float(str(qos['throughput']).replace('Mbps', '').replace('Gbps', '000').strip()),
                "reliability": float(qos['reliability']),
                "jitter_ms": float(str(qos.get('jitter', '10ms')).replace('ms', '').strip())
            },
            "tenant_id": f"experiment-{template['scenario_id']}"
        }
        
        return payload, correlation_id
    
    def submit_sla(self, payload: Dict[str, Any], correlation_id: str) -> Dict[str, Any]:
        """
        Submete um SLA via API HTTP
        
        Args:
            payload: Payload do SLA
            correlation_id: ID de correlação único
            
        Returns:
            Resultado da submissão com timestamps
        """
        submission_start = time.time()
        submission_timestamp = datetime.now(timezone.utc).isoformat()
        
        result = {
            "correlation_id": correlation_id,
            "submission_timestamp": submission_timestamp,
            "payload": payload,
            "success": False,
            "error": None,
            "response": None,
            "submission_time_ms": None
        }
        
        try:
            # Endpoint da API (ajustar conforme API real)
            endpoint = f"{self.api_url}/api/v1/sla/submit"
            
            logger.info(f"Submetendo SLA: {correlation_id}")
            response = requests.post(
                endpoint,
                json=payload,
                timeout=30,
                headers={"Content-Type": "application/json"}
            )
            
            submission_end = time.time()
            result["submission_time_ms"] = (submission_end - submission_start) * 1000
            
            if response.status_code == 200 or response.status_code == 201:
                result["success"] = True
                result["response"] = response.json()
                logger.info(f"SLA submetido com sucesso: {correlation_id}")
            else:
                result["error"] = f"HTTP {response.status_code}: {response.text}"
                logger.error(f"Erro ao submeter SLA {correlation_id}: {result['error']}")
                
        except requests.exceptions.RequestException as e:
            result["error"] = str(e)
            logger.error(f"Exceção ao submeter SLA {correlation_id}: {e}")
        
        return result
    
    def execute_scenario(self, template_path: str) -> List[Dict[str, Any]]:
        """
        Executa cenário completo conforme template
        
        Args:
            template_path: Caminho para o template YAML
            
        Returns:
            Lista com resultados de todas as submissões
        """
        template = self.load_template(template_path)
        execution = template['execution']
        quantity = execution['quantity']
        interval = execution.get('interval_seconds', 5)
        
        logger.info(f"Iniciando execução do cenário: {template['scenario_id']}")
        logger.info(f"Quantidade de SLAs: {quantity}, Intervalo: {interval}s")
        
        self.submissions = []
        
        for i in range(1, quantity + 1):
            # Gerar payload
            payload, correlation_id = self.generate_sla_payload(template, i)
            
            # Submeter
            result = self.submit_sla(payload, correlation_id)
            self.submissions.append(result)
            
            # Aguardar intervalo (exceto no último)
            if i < quantity:
                time.sleep(interval)
        
        logger.info(f"Execução concluída: {len(self.submissions)} SLAs submetidos")
        return self.submissions
    
    def save_results(self, output_path: str):
        """
        Salva resultados em arquivo JSON
        
        Args:
            output_path: Caminho para salvar resultados
        """
        output_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "submissions": self.submissions,
            "summary": {
                "total": len(self.submissions),
                "successful": sum(1 for s in self.submissions if s['success']),
                "failed": sum(1 for s in self.submissions if not s['success'])
            }
        }
        
        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        logger.info(f"Resultados salvos em: {output_path}")


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='Submete SLAs experimentais conforme template')
    parser.add_argument('template', help='Caminho para o template YAML')
    parser.add_argument('--api-url', help='URL da API do TriSLA', default=None)
    parser.add_argument('--output', help='Arquivo de saída JSON', default=None)
    
    args = parser.parse_args()
    
    # Criar submissor
    submitter = SLASubmitter(api_url=args.api_url)
    
    # Executar cenário
    try:
        submissions = submitter.execute_scenario(args.template)
        
        # Salvar resultados
        if args.output:
            output_path = args.output
        else:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            output_path = f"experiments/data/submissions_{timestamp}.json"
        
        submitter.save_results(output_path)
        
        # Resumo
        successful = sum(1 for s in submissions if s['success'])
        failed = len(submissions) - successful
        
        print(f"\n=== RESUMO ===")
        print(f"Total: {len(submissions)}")
        print(f"Sucesso: {successful}")
        print(f"Falhas: {failed}")
        print(f"Resultados salvos em: {output_path}")
        
        sys.exit(0 if failed == 0 else 1)
        
    except Exception as e:
        logger.error(f"Erro na execução: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    import os
    main()

