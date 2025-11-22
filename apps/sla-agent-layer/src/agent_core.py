"""
Agent-Core - SLA-Agent Layer
Agente autônomo para domínio Core com integração real ao NASP Adapter
"""

import sys
import os
from typing import Dict, Any, Optional
from opentelemetry import trace
import logging

# Adicionar path para NASP Adapter
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "nasp-adapter",
    "src"
))

try:
    from nasp_client import NASPClient
    NASP_AVAILABLE = True
except ImportError:
    NASP_AVAILABLE = False
    print("⚠️ NASP Adapter não disponível. Agent Core usará fallback limitado.")

from slo_evaluator import SLOEvaluator, SLOStatus
from config_loader import load_slo_config
from kafka_producer import EventProducer

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)


class AgentCore:
    """
    Agente autônomo para domínio Core
    
    Características:
    - Coleta métricas reais do NASP Adapter
    - Avalia SLOs localmente
    - Executa ações corretivas via NASP Adapter
    - Publica eventos via Kafka (I-06)
    """
    
    def __init__(
        self,
        nasp_client: Optional[NASPClient] = None,
        agent_id: str = "agent-core-1",
        event_producer: Optional[EventProducer] = None
    ):
        """
        Inicializa agente Core
        
        Args:
            nasp_client: Cliente NASP (padrão: cria novo se disponível)
            agent_id: ID único do agente
            event_producer: Producer Kafka para eventos I-06 e I-07
        """
        self.domain = "Core"
        self.agent_id = agent_id
        
        # Inicializar NASP Client
        if nasp_client:
            self.nasp_client = nasp_client
        elif NASP_AVAILABLE:
            self.nasp_client = NASPClient()
        else:
            self.nasp_client = None
            logger.warning("⚠️ Agent Core sem NASP Adapter - funcionalidade limitada")
        
        # Inicializar Event Producer
        self.event_producer = event_producer or EventProducer()
        
        # Carregar configuração de SLOs
        try:
            slo_config = load_slo_config(self.domain)
            self.slo_evaluator = SLOEvaluator(slo_config)
            logger.info(f"✅ SLOs carregados para domínio {self.domain}")
        except Exception as e:
            logger.error(f"❌ Erro ao carregar SLOs: {e}")
            self.slo_evaluator = SLOEvaluator({
                "domain": self.domain,
                "slos": []
            })
        
        # Estado interno para loop autônomo
        self.running = False
        self.poll_interval = float(os.getenv("AGENT_POLL_INTERVAL_SECONDS", "10.0"))
    
    async def collect_metrics(self) -> Dict[str, Any]:
        """
        Coleta métricas reais do Core via NASP Adapter
        
        IMPORTANTE: Métricas são coletadas do NASP real, não hardcoded.
        """
        with tracer.start_as_current_span("collect_core_metrics") as span:
            span.set_attribute("agent.domain", self.domain)
            span.set_attribute("agent.id", self.agent_id)
            
            if self.nasp_client:
                try:
                    # Coletar métricas reais do NASP
                    nasp_metrics = await self.nasp_client.get_core_metrics()
                    
                    # Normalizar métricas
                    metrics = {
                        "domain": self.domain,
                        "agent_id": self.agent_id,
                        "cpu_utilization": self._extract_cpu_utilization(nasp_metrics),
                        "memory_utilization": self._extract_memory_utilization(nasp_metrics),
                        "request_latency": self._extract_request_latency(nasp_metrics),
                        "throughput": self._extract_throughput(nasp_metrics),
                        "source": "nasp_core_real",
                        "timestamp": self._get_timestamp(),
                        "raw_metrics": nasp_metrics
                    }
                    
                    span.set_attribute("metrics.source", "nasp_core_real")
                    return metrics
                    
                except Exception as e:
                    span.record_exception(e)
                    logger.error(f"❌ Erro ao coletar métricas do NASP: {e}")
                    return self._get_fallback_metrics()
            else:
                return self._get_fallback_metrics()
    
    def _extract_cpu_utilization(self, metrics: Dict[str, Any]) -> float:
        """Extrai utilização de CPU das métricas"""
        return float(metrics.get("cpu_utilization", metrics.get("cpu_usage", 0.0))) * 100
    
    def _extract_memory_utilization(self, metrics: Dict[str, Any]) -> float:
        """Extrai utilização de memória das métricas"""
        return float(metrics.get("memory_utilization", metrics.get("memory_usage", 0.0))) * 100
    
    def _extract_request_latency(self, metrics: Dict[str, Any]) -> float:
        """Extrai latência de requisições das métricas"""
        return float(metrics.get("request_latency", metrics.get("latency", 0.0)))
    
    def _extract_throughput(self, metrics: Dict[str, Any]) -> float:
        """Extrai throughput das métricas"""
        return float(metrics.get("throughput", metrics.get("req_per_sec", 0.0)))
    
    def _get_fallback_metrics(self) -> Dict[str, Any]:
        """Métricas de fallback"""
        return {
            "domain": self.domain,
            "agent_id": self.agent_id,
            "cpu_utilization": 0.0,
            "memory_utilization": 0.0,
            "request_latency": 0.0,
            "throughput": 0.0,
            "source": "fallback",
            "timestamp": self._get_timestamp(),
            "warning": "NASP Adapter não disponível - métricas não são reais"
        }
    
    async def execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa ação corretiva no Core via NASP Adapter
        
        IMPORTANTE: Ação é executada no NASP real, não simulada.
        """
        with tracer.start_as_current_span("execute_core_action") as span:
            span.set_attribute("agent.domain", self.domain)
            span.set_attribute("agent.id", self.agent_id)
            span.set_attribute("action.type", action.get("type", "unknown"))
            
            if self.nasp_client:
                try:
                    # Executar ação real via NASP Adapter
                    sys.path.insert(0, os.path.join(
                        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                        "nasp-adapter",
                        "src"
                    ))
                    from action_executor import ActionExecutor
                    action_executor = ActionExecutor(self.nasp_client)
                    
                    # Configurar domínio na ação
                    action_with_domain = {**action, "domain": "core"}
                    result = await action_executor.execute(action_with_domain)
                    
                    executed = result.get("executed", result.get("success", False))
                    
                    span.set_attribute("action.executed", executed)
                    span.set_attribute("action.result", str(result))
                    
                    action_result = {
                        "domain": self.domain,
                        "agent_id": self.agent_id,
                        "action_type": action.get("type"),
                        "executed": executed,
                        "result": result,
                        "timestamp": self._get_timestamp()
                    }
                    
                    # Publicar evento I-07 (resultado de ação)
                    await self.event_producer.send_i07_action_result(
                        domain=self.domain,
                        agent_id=self.agent_id,
                        action=action,
                        result=action_result
                    )
                    logger.info(
                        f"📢 Evento I-07 publicado: domain={self.domain}, "
                        f"action={action.get('type')}, executed={executed}"
                    )
                    
                    return action_result
                    
                except Exception as e:
                    span.record_exception(e)
                    logger.error(f"❌ Erro ao executar ação no NASP: {e}")
                    return {
                        "domain": self.domain,
                        "agent_id": self.agent_id,
                        "action_type": action.get("type"),
                        "executed": False,
                        "error": str(e),
                        "timestamp": self._get_timestamp()
                    }
            else:
                return {
                    "domain": self.domain,
                    "agent_id": self.agent_id,
                    "action_type": action.get("type"),
                    "executed": False,
                    "error": "NASP Adapter não disponível",
                    "timestamp": self._get_timestamp()
                }
    
    async def evaluate_slos(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Avalia métricas contra SLOs configurados e publica eventos I-06 se necessário
        """
        with tracer.start_as_current_span("evaluate_core_slos") as span:
            evaluation = self.slo_evaluator.evaluate(metrics)
            span.set_attribute("slo.status", evaluation.get("status"))
            span.set_attribute("slo.compliance_rate", evaluation.get("compliance_rate"))
            span.set_attribute("slo.violations_count", len(evaluation.get("violations", [])))
            
            # Publicar eventos I-06 para violações e riscos
            status = evaluation.get("status")
            if status in [SLOStatus.RISK, SLOStatus.VIOLATED]:
                for slo in evaluation.get("slos", []):
                    if slo.get("status") in [SLOStatus.RISK, SLOStatus.VIOLATED]:
                        await self.event_producer.send_i06_event(
                            domain=self.domain,
                            agent_id=self.agent_id,
                            status=slo.get("status"),
                            slo={
                                "name": slo.get("name"),
                                "target": slo.get("target"),
                                "current": slo.get("current"),
                                "unit": slo.get("unit")
                            },
                            slice_id=metrics.get("slice_id"),
                            sla_id=metrics.get("sla_id")
                        )
                        logger.info(
                            f"📢 Evento I-06 publicado: domain={self.domain}, "
                            f"slo={slo.get('name')}, status={slo.get('status')}"
                        )
            
            return evaluation
    
    def is_healthy(self) -> bool:
        """Verifica saúde do agente"""
        return self.nasp_client is not None
    
    async def get_slos(self) -> Dict[str, Any]:
        """Retorna SLOs configurados e status atual"""
        metrics = await self.collect_metrics()
        evaluation = await self.evaluate_slos(metrics)
        
        return {
            "domain": self.domain,
            "agent_id": self.agent_id,
            "slos": evaluation.get("slos", []),
            "compliance_rate": evaluation.get("compliance_rate", 0.0),
            "status": evaluation.get("status", "UNKNOWN"),
            "violations": evaluation.get("violations", []),
            "risks": evaluation.get("risks", []),
            "timestamp": self._get_timestamp()
        }
    
    async def run_autonomous_loop(self):
        """Loop autônomo de coleta de métricas, avaliação de SLOs e publicação de eventos"""
        self.running = True
        logger.info(f"🔄 Iniciando loop autônomo do Agent Core (intervalo: {self.poll_interval}s)")
        
        import asyncio
        
        while self.running:
            try:
                metrics = await self.collect_metrics()
                evaluation = await self.evaluate_slos(metrics)
                
                status = evaluation.get("status")
                if status != SLOStatus.OK:
                    logger.warning(
                        f"⚠️ SLOs em {status}: domain={self.domain}, "
                        f"violations={len(evaluation.get('violations', []))}, "
                        f"risks={len(evaluation.get('risks', []))}"
                    )
                
                await asyncio.sleep(self.poll_interval)
            except Exception as e:
                logger.error(f"❌ Erro no loop autônomo: {e}", exc_info=True)
                await asyncio.sleep(self.poll_interval)
    
    def stop_autonomous_loop(self):
        """Para o loop autônomo"""
        self.running = False
        logger.info("🛑 Parando loop autônomo do Agent Core")
    
    def _get_timestamp(self) -> str:
        """Retorna timestamp atual"""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()
