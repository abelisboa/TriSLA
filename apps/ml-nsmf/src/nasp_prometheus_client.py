"""
Cliente Prometheus - ML-NSMF
Coleta métricas reais do NASP via Prometheus para predição de risco
FASE C2: Implementação com dados reais
"""

import httpx
from typing import Dict, Any, Optional, List
from opentelemetry import trace
import logging
from datetime import datetime, timedelta, timezone

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)


class PrometheusClient:
    """
    Cliente para coleta de métricas reais do Prometheus
    Coleta métricas do NASP em tempo real para predição de risco
    """
    
    def __init__(self, prometheus_url: Optional[str] = None):
        """
        Inicializa cliente Prometheus
        
        Args:
            prometheus_url: URL do Prometheus (padrão: PROMETHEUS_URL env ou http://prometheus:9090)
        """
        import os
        self.prometheus_url = prometheus_url or os.getenv("PROMETHEUS_URL", "http://prometheus:9090")
        self.http_client = httpx.AsyncClient(timeout=30.0)
        logger.info(f"PrometheusClient inicializado: {self.prometheus_url}")
    
    async def query(self, promql: str, time_range: Optional[timedelta] = None) -> Optional[Dict[str, Any]]:
        """
        Executa query PromQL no Prometheus
        
        Args:
            promql: Query PromQL
            time_range: Janela temporal (padrão: últimos 10 minutos)
        
        Returns:
            Resultado da query ou None em caso de erro
        """
        with tracer.start_as_current_span("prometheus_query") as span:
            span.set_attribute("prometheus.query", promql)
            
            try:
                # Determinar janela temporal
                if time_range is None:
                    time_range = timedelta(minutes=10)
                
                end_time = datetime.now(timezone.utc)
                start_time = end_time - time_range
                
                # Converter para timestamp Unix
                start_timestamp = int(start_time.timestamp())
                end_timestamp = int(end_time.timestamp())
                
                # Executar query range (para métricas ao longo do tempo)
                url = f"{self.prometheus_url}/api/v1/query_range"
                params = {
                    "query": promql,
                    "start": start_timestamp,
                    "end": end_timestamp,
                    "step": "30s"  # Resolução de 30 segundos
                }
                
                logger.debug(f"Executando query PromQL: {promql}")
                logger.debug(f"Janela temporal: {start_time.isoformat()} a {end_time.isoformat()}")
                
                response = await self.http_client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if data.get("status") != "success":
                    logger.error(f"Query PromQL falhou: {data.get('error', 'Unknown error')}")
                    span.set_attribute("prometheus.error", str(data.get("error")))
                    return None
                
                result = data.get("data", {}).get("result", [])
                span.set_attribute("prometheus.result_count", len(result))
                
                logger.debug(f"Query PromQL retornou {len(result)} séries temporais")
                
                return {
                    "result": result,
                    "start_time": start_timestamp,
                    "end_time": end_timestamp,
                    "query": promql
                }
                
            except httpx.HTTPError as e:
                logger.error(f"❌ Erro HTTP ao consultar Prometheus: {e}")
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                return None
            except Exception as e:
                logger.error(f"❌ Erro inesperado ao consultar Prometheus: {e}", exc_info=True)
                span.record_exception(e)
                return None
    
    async def get_latency_metrics(self, slice_id: Optional[str] = None, time_range: Optional[timedelta] = None) -> Optional[float]:
        """
        Obtém métricas de latência do NASP
        
        Args:
            slice_id: ID do slice (opcional, para filtrar por slice específico)
            time_range: Janela temporal (padrão: últimos 10 minutos)
        
        Returns:
            Latência média em ms ou None
        """
        with tracer.start_as_current_span("get_latency_metrics") as span:
            # Query PromQL para latência (exemplo: latência de RAN ou Core)
            # Ajustar conforme métricas reais do NASP
            if slice_id:
                promql = f'avg_over_time(ran_latency_ms{{slice_id="{slice_id}"}}[5m])'
            else:
                promql = 'avg_over_time(ran_latency_ms[5m])'
            
            # Fallback: usar métricas genéricas se específicas não existirem
            fallback_promql = 'avg_over_time(upstream_rtt_seconds[5m]) * 1000'  # Converter para ms
            
            result = await self.query(promql, time_range)
            
            if result and result.get("result"):
                # Extrair valor médio da série temporal
                values = []
                for series in result["result"]:
                    for value_pair in series.get("values", []):
                        if value_pair[1] != "NaN":
                            try:
                                values.append(float(value_pair[1]))
                            except (ValueError, TypeError):
                                pass
                
                if values:
                    avg_latency = sum(values) / len(values)
                    span.set_attribute("latency.avg_ms", avg_latency)
                    logger.info(f"Latência média coletada: {avg_latency:.2f} ms")
                    return avg_latency
            
            # Tentar fallback
            logger.debug("Tentando query fallback para latência")
            result = await self.query(fallback_promql, time_range)
            if result and result.get("result"):
                values = []
                for series in result["result"]:
                    for value_pair in series.get("values", []):
                        if value_pair[1] != "NaN":
                            try:
                                values.append(float(value_pair[1]))
                            except (ValueError, TypeError):
                                pass
                if values:
                    avg_latency = sum(values) / len(values)
                    return avg_latency
            
            logger.warning("Não foi possível coletar métricas de latência do Prometheus")
            return None
    
    async def get_packet_loss_metrics(self, slice_id: Optional[str] = None, time_range: Optional[timedelta] = None) -> Optional[float]:
        """
        Obtém métricas de perda de pacotes do NASP
        
        Args:
            slice_id: ID do slice (opcional)
            time_range: Janela temporal (padrão: últimos 10 minutos)
        
        Returns:
            Taxa de perda de pacotes (0-1) ou None
        """
        with tracer.start_as_current_span("get_packet_loss_metrics") as span:
            # Query PromQL para perda de pacotes
            if slice_id:
                promql = f'avg_over_time(packet_loss_rate{{slice_id="{slice_id}"}}[5m])'
            else:
                promql = 'avg_over_time(packet_loss_rate[5m])'
            
            # Fallback: calcular a partir de métricas disponíveis
            fallback_promql = '1 - (sum(rate(packets_received_total[5m])) / sum(rate(packets_sent_total[5m])))'
            
            result = await self.query(promql, time_range)
            
            if result and result.get("result"):
                values = []
                for series in result["result"]:
                    for value_pair in series.get("values", []):
                        if value_pair[1] != "NaN":
                            try:
                                values.append(float(value_pair[1]))
                            except (ValueError, TypeError):
                                pass
                
                if values:
                    avg_loss = sum(values) / len(values)
                    span.set_attribute("packet_loss.avg", avg_loss)
                    logger.info(f"Perda de pacotes média coletada: {avg_loss:.4f}")
                    return max(0.0, min(1.0, avg_loss))  # Garantir 0-1
            
            # Tentar fallback
            logger.debug("Tentando query fallback para perda de pacotes")
            result = await self.query(fallback_promql, time_range)
            if result and result.get("result"):
                values = []
                for series in result["result"]:
                    for value_pair in series.get("values", []):
                        if value_pair[1] != "NaN":
                            try:
                                values.append(float(value_pair[1]))
                            except (ValueError, TypeError):
                                pass
                if values:
                    avg_loss = sum(values) / len(values)
                    return max(0.0, min(1.0, avg_loss))
            
            logger.warning("Não foi possível coletar métricas de perda de pacotes do Prometheus")
            return None
    
    async def get_availability_metrics(self, slice_id: Optional[str] = None, time_range: Optional[timedelta] = None) -> Optional[float]:
        """
        Obtém métricas de disponibilidade do NASP
        
        Args:
            slice_id: ID do slice (opcional)
            time_range: Janela temporal (padrão: últimos 10 minutos)
        
        Returns:
            Disponibilidade (0-1) ou None
        """
        with tracer.start_as_current_span("get_availability_metrics") as span:
            # Query PromQL para disponibilidade
            if slice_id:
                promql = f'avg_over_time(slice_availability{{slice_id="{slice_id}"}}[5m])'
            else:
                promql = 'avg_over_time(slice_availability[5m])'
            
            # Fallback: usar métrica 'up' do Prometheus
            fallback_promql = 'avg_over_time(up[5m])'
            
            result = await self.query(promql, time_range)
            
            if result and result.get("result"):
                values = []
                for series in result["result"]:
                    for value_pair in series.get("values", []):
                        if value_pair[1] != "NaN":
                            try:
                                values.append(float(value_pair[1]))
                            except (ValueError, TypeError):
                                pass
                
                if values:
                    avg_availability = sum(values) / len(values)
                    span.set_attribute("availability.avg", avg_availability)
                    logger.info(f"Disponibilidade média coletada: {avg_availability:.4f}")
                    return max(0.0, min(1.0, avg_availability))
            
            # Tentar fallback
            logger.debug("Tentando query fallback para disponibilidade")
            result = await self.query(fallback_promql, time_range)
            if result and result.get("result"):
                values = []
                for series in result["result"]:
                    for value_pair in series.get("values", []):
                        if value_pair[1] != "NaN":
                            try:
                                values.append(float(value_pair[1]))
                            except (ValueError, TypeError):
                                pass
                if values:
                    avg_availability = sum(values) / len(values)
                    return max(0.0, min(1.0, avg_availability))
            
            logger.warning("Não foi possível coletar métricas de disponibilidade do Prometheus")
            return None
    
    async def get_load_metrics(self, slice_id: Optional[str] = None, time_range: Optional[timedelta] = None) -> Optional[float]:
        """
        Obtém métricas de carga do NASP
        
        Args:
            slice_id: ID do slice (opcional)
            time_range: Janela temporal (padrão: últimos 10 minutos)
        
        Returns:
            Carga média (0-1) ou None
        """
        with tracer.start_as_current_span("get_load_metrics") as span:
            # Query PromQL para carga (CPU, memória, ou throughput)
            if slice_id:
                promql = f'avg_over_time(slice_cpu_utilization{{slice_id="{slice_id}"}}[5m])'
            else:
                promql = 'avg_over_time(slice_cpu_utilization[5m])'
            
            # Fallback: usar métricas genéricas
            fallback_promql = 'avg_over_time(node_cpu_seconds_total[5m])'
            
            result = await self.query(promql, time_range)
            
            if result and result.get("result"):
                values = []
                for series in result["result"]:
                    for value_pair in series.get("values", []):
                        if value_pair[1] != "NaN":
                            try:
                                values.append(float(value_pair[1]))
                            except (ValueError, TypeError):
                                pass
                
                if values:
                    avg_load = sum(values) / len(values)
                    span.set_attribute("load.avg", avg_load)
                    logger.info(f"Carga média coletada: {avg_load:.4f}")
                    return max(0.0, min(1.0, avg_load))
            
            # Tentar fallback
            logger.debug("Tentando query fallback para carga")
            result = await self.query(fallback_promql, time_range)
            if result and result.get("result"):
                values = []
                for series in result["result"]:
                    for value_pair in series.get("values", []):
                        if value_pair[1] != "NaN":
                            try:
                                values.append(float(value_pair[1]))
                            except (ValueError, TypeError):
                                pass
                if values:
                    avg_load = sum(values) / len(values)
                    return max(0.0, min(1.0, avg_load))
            
            logger.warning("Não foi possível coletar métricas de carga do Prometheus")
            return None
    
    async def collect_all_metrics(self, slice_id: Optional[str] = None, time_range: Optional[timedelta] = None) -> Dict[str, Any]:
        """
        Coleta todas as métricas reais do NASP via Prometheus
        
        Args:
            slice_id: ID do slice (opcional)
            time_range: Janela temporal (padrão: últimos 10 minutos)
        
        Returns:
            Dicionário com métricas coletadas
        """
        with tracer.start_as_current_span("collect_all_metrics") as span:
            span.set_attribute("prometheus.slice_id", slice_id or "all")
            
            logger.info(f"🔍 Coletando métricas reais do Prometheus (slice_id={slice_id or 'all'})")
            
            # Coletar métricas em paralelo
            import asyncio
            latency, packet_loss, availability, load = await asyncio.gather(
                self.get_latency_metrics(slice_id, time_range),
                self.get_packet_loss_metrics(slice_id, time_range),
                self.get_availability_metrics(slice_id, time_range),
                self.get_load_metrics(slice_id, time_range),
                return_exceptions=True
            )
            
            # Construir dicionário de métricas
            metrics = {}
            
            if isinstance(latency, Exception):
                logger.warning(f"Erro ao coletar latência: {latency}")
            elif latency is not None:
                metrics["latency"] = latency
                span.set_attribute("metrics.latency_ms", latency)
            
            if isinstance(packet_loss, Exception):
                logger.warning(f"Erro ao coletar perda de pacotes: {packet_loss}")
            elif packet_loss is not None:
                metrics["packet_loss"] = packet_loss
                # Converter para reliability
                metrics["reliability"] = 1.0 - packet_loss
                span.set_attribute("metrics.packet_loss", packet_loss)
            
            if isinstance(availability, Exception):
                logger.warning(f"Erro ao coletar disponibilidade: {availability}")
            elif availability is not None:
                metrics["availability"] = availability
                span.set_attribute("metrics.availability", availability)
            
            if isinstance(load, Exception):
                logger.warning(f"Erro ao coletar carga: {load}")
            elif load is not None:
                metrics["cpu_utilization"] = load
                span.set_attribute("metrics.cpu_utilization", load)
            
            logger.info(f"✅ Métricas coletadas: {list(metrics.keys())}")
            span.set_attribute("metrics.count", len(metrics))
            
            return metrics
    
    async def close(self):
        """Fecha conexão HTTP"""
        await self.http_client.aclose()

