"""
Resource Evaluator - Decision Engine
Avalia recursos disponíveis usando queries Prometheus finais (sem rate())
Aplicação das queries finais de decisão conforme PROMPT_S3.30
"""

import httpx
import logging
from typing import Dict, Optional
from opentelemetry import trace

from config import config

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)

# Referência para normalização de rede (10GB em bytes)
NET_REF_BYTES = 10 * 1024 * 1024 * 1024  # 10 GB


class ResourceEvaluator:
    """
    Avaliador de recursos usando queries Prometheus finais
    Queries sem rate() para decisão estável e imediata
    """
    
    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=10.0)
        self.prometheus_url = config.prometheus_url
    
    async def evaluate_resources(self) -> Dict[str, float]:
        """
        Avalia recursos disponíveis nos domínios:
        - Computação (CPU)
        - Memória
        - Armazenamento (Disco)
        - Rede
        
        Returns:
            Dict com scores normalizados [0,1] para cada domínio
        """
        with tracer.start_as_current_span("evaluate_resources") as span:
            try:
                # Obter métricas de cada domínio
                cpu_used_fraction = await self._query_cpu()
                mem_available_fraction = await self._query_memory()
                disk_available_fraction = await self._query_disk()
                net_increase_bytes = await self._query_network()
                
                # Normalização conforme FASE 3
                cpu_score = 1 - cpu_used_fraction
                mem_score = mem_available_fraction
                disk_score = disk_available_fraction
                net_score = min(1.0, net_increase_bytes / NET_REF_BYTES)
                
                # Garantir scores ∈ [0,1]
                cpu_score = max(0.0, min(1.0, cpu_score))
                mem_score = max(0.0, min(1.0, mem_score))
                disk_score = max(0.0, min(1.0, disk_score))
                net_score = max(0.0, min(1.0, net_score))
                
                result = {
                    "cpu_score": cpu_score,
                    "memory_score": mem_score,
                    "disk_score": disk_score,
                    "network_score": net_score,
                    "cpu_used_fraction": cpu_used_fraction,
                    "mem_available_fraction": mem_available_fraction,
                    "disk_available_fraction": disk_available_fraction,
                    "net_increase_bytes": net_increase_bytes
                }
                
                span.set_attribute("resources.cpu_score", cpu_score)
                span.set_attribute("resources.memory_score", mem_score)
                span.set_attribute("resources.disk_score", disk_score)
                span.set_attribute("resources.network_score", net_score)
                
                logger.info(
                    f"Recursos avaliados - CPU: {cpu_score:.3f}, "
                    f"Mem: {mem_score:.3f}, Disk: {disk_score:.3f}, "
                    f"Net: {net_score:.3f}"
                )
                
                return result
                
            except Exception as e:
                logger.error(f"Erro ao avaliar recursos: {e}", exc_info=True)
                span.record_exception(e)
                # Retornar scores padrão (assumindo recursos disponíveis)
                return {
                    "cpu_score": 0.5,
                    "memory_score": 0.5,
                    "disk_score": 0.5,
                    "network_score": 0.5,
                    "error": str(e)
                }
    
    async def _query_cpu(self) -> float:
        """
        Query FINAL para CPU (sem rate())
        1 - avg(node_cpu_seconds_total{mode="idle"}) / avg(node_cpu_seconds_total)
        """
        query = "1 - avg(node_cpu_seconds_total{mode=\"idle\"}) / avg(node_cpu_seconds_total)"
        result = await self._execute_query(query)
        return float(result) if result is not None else 0.5
    
    async def _query_memory(self) -> float:
        """
        Query FINAL para Memória (sem rate())
        avg(node_memory_MemAvailable_bytes) / avg(node_memory_MemTotal_bytes)
        """
        query = "avg(node_memory_MemAvailable_bytes) / avg(node_memory_MemTotal_bytes)"
        result = await self._execute_query(query)
        return float(result) if result is not None else 0.5
    
    async def _query_disk(self) -> float:
        """
        Query FINAL para Disco (sem rate())
        avg(node_filesystem_avail_bytes{fstype!~\"tmpfs|overlay\"}) / avg(node_filesystem_size_bytes{fstype!~\"tmpfs|overlay\"})
        """
        query = "avg(node_filesystem_avail_bytes{fstype!~\"tmpfs|overlay\"}) / avg(node_filesystem_size_bytes{fstype!~\"tmpfs|overlay\"})"
        result = await self._execute_query(query)
        return float(result) if result is not None else 0.5
    
    async def _query_network(self) -> float:
        """
        Query FINAL para Rede (sem rate())
        increase(node_network_transmit_bytes_total[10m])
        """
        query = "increase(node_network_transmit_bytes_total[10m])"
        result = await self._execute_query(query)
        return float(result) if result is not None else 0.0
    
    async def _execute_query(self, query: str) -> Optional[float]:
        """
        Executa query Prometheus e retorna valor escalar
        """
        try:
            url = f"{self.prometheus_url}/api/v1/query"
            params = {"query": query}
            
            response = await self.http_client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data.get("status") == "success":
                result = data.get("data", {}).get("result", [])
                if result and len(result) > 0:
                    # Extrair valor escalar
                    value = result[0].get("value", [None, None])[1]
                    if value:
                        return float(value)
            
            logger.warning(f"Query retornou resultado vazio: {query}")
            return None
            
        except Exception as e:
            logger.error(f"Erro ao executar query Prometheus: {query} - {e}")
            return None
    
    async def close(self):
        """Fecha conexão HTTP"""
        await self.http_client.aclose()
