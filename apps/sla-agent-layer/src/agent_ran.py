"""
Agent-RAN - SLA-Agent Layer
Agente autônomo para domínio RAN com integração real ao NASP Adapter

Conforme dissertação TriSLA:
- Coleta métricas reais do NASP
- Avalia SLOs localmente
- Executa ações corretivas via NASP Adapter
- Publica eventos de violação/risco via Kafka (I-06)
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
    print("⚠️ NASP Adapter não disponível. Agent RAN usará fallback limitado.")

from slo_evaluator import SLOEvaluator, SLOStatus
from config_loader import load_slo_config
from kafka_producer import EventProducer

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)


class AgentRAN:
    """
    Agente autônomo para domínio RAN
    
    Características:
    - Coleta métricas reais do NASP Adapter
    - Avalia SLOs localmente
    - Executa ações corretivas via NASP Adapter
    - Publica eventos via Kafka (I-06)
    """
    
    def __init__(
        self,
        nasp_client: Optional[NASPClient] = None,
        agent_id: str = "agent-ran-1",
        event_producer: Optional[EventProducer] = None
    ):
        """
        Inicializa agente RAN
        
        Args:
            nasp_client: Cliente NASP (padrão: cria novo se disponível)
            agent_id: ID único do agente
            event_producer: Producer Kafka para eventos I-06 e I-07
        """
        self.domain = "RAN"
        self.agent_id = agent_id
        
        # Inicializar NASP Client
        if nasp_client:
            self.nasp_client = nasp_client
        elif NASP_AVAILABLE:
            self.nasp_client = NASPClient()
        else:
            self.nasp_client = None
            logger.warning("⚠️ Agent RAN sem NASP Adapter - funcionalidade limitada")
        
        # Inicializar Event Producer
        self.event_producer = event_producer or EventProducer()
        
        # Carregar configuração de SLOs
        try:
            slo_config = load_slo_config(self.domain)
            self.slo_evaluator = SLOEvaluator(slo_config)
            logger.info(f"✅ SLOs carregados para domínio {self.domain}")
        except Exception as e:
            logger.error(f"❌ Erro ao carregar SLOs: {e}")
            # Fallback para SLOs padrão
            self.slo_evaluator = SLOEvaluator({
                "domain": self.domain,
                "slos": []
            })
        
        # Estado interno para loop autônomo
        self.running = False
        self.poll_interval = float(os.getenv("AGENT_POLL_INTERVAL_SECONDS", "10.0"))
    
    async def collect_metrics(self) -> Dict[str, Any]:
        """
        Coleta métricas reais do RAN via NASP Adapter
        
        IMPORTANTE: Métricas são coletadas do NASP real, não hardcoded.
        
        Returns:
            Dicionário com métricas coletadas
        """
        with tracer.start_as_current_span("collect_ran_metrics") as span:
            span.set_attribute("agent.domain", self.domain)
            span.set_attribute("agent.id", self.agent_id)
            
            if self.nasp_client:
                try:
                    # Coletar métricas reais do NASP
                    nasp_metrics = await self.nasp_client.get_ran_metrics()
                    
                    # Normalizar métricas para formato padrão
                    metrics = {
                        "domain": self.domain,
                        "agent_id": self.agent_id,
                        "prb_allocation": self._extract_prb_allocation(nasp_metrics),
                        "latency": self._extract_latency(nasp_metrics),
                        "throughput": self._extract_throughput(nasp_metrics),
                        "packet_loss": self._extract_packet_loss(nasp_metrics),
                        "jitter": self._extract_jitter(nasp_metrics),
                        "source": "nasp_ran_real",
                        "timestamp": self._get_timestamp(),
                        "raw_metrics": nasp_metrics  # Manter métricas brutas para debug
                    }
                    
                    span.set_attribute("metrics.source", "nasp_ran_real")
                    span.set_attribute("metrics.latency", metrics.get("latency"))
                    span.set_attribute("metrics.throughput", metrics.get("throughput"))
                    
                    return metrics
                    
                except Exception as e:
                    span.record_exception(e)
                    logger.error(f"❌ Erro ao coletar métricas do NASP: {e}")
                    # Retornar métricas vazias em caso de erro
                    return self._get_fallback_metrics()
            else:
                logger.warning("⚠️ NASP Adapter não disponível, retornando métricas de fallback")
                return self._get_fallback_metrics()
    
    def _extract_prb_allocation(self, metrics: Dict[str, Any]) -> float:
        """Extrai alocação de PRB das métricas"""
        return float(metrics.get("prb_allocation", metrics.get("prb_utilization", 0.0)))
    
    def _extract_latency(self, metrics: Dict[str, Any]) -> float:
        """Extrai latência das métricas"""
        return float(metrics.get("latency", metrics.get("delay", 0.0)))
    
    def _extract_throughput(self, metrics: Dict[str, Any]) -> float:
        """Extrai throughput das métricas"""
        return float(metrics.get("throughput", metrics.get("bitrate", 0.0)))
    
    def _extract_packet_loss(self, metrics: Dict[str, Any]) -> float:
        """Extrai packet loss das métricas"""
        return float(metrics.get("packet_loss", metrics.get("loss", 0.0)))
    
    def _extract_jitter(self, metrics: Dict[str, Any]) -> float:
        """Extrai jitter das métricas"""
        return float(metrics.get("jitter", 0.0))
    
    def _get_fallback_metrics(self) -> Dict[str, Any]:
        """Métricas de fallback (apenas se NASP não disponível)"""
        return {
            "domain": self.domain,
            "agent_id": self.agent_id,
            "prb_allocation": 0.0,
            "latency": 0.0,
            "throughput": 0.0,
            "packet_loss": 0.0,
            "jitter": 0.0,
            "source": "fallback",
            "timestamp": self._get_timestamp(),
            "warning": "NASP Adapter não disponível - métricas não são reais"
        }
    
    async def execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa ação corretiva no RAN via NASP Adapter
        
        IMPORTANTE: Ação é executada no NASP real, não simulada.
        
        Args:
            action: Dicionário com ação a executar
                {
                    "type": "ADJUST_PRB" | "MODIFY_QOS" | ...,
                    "parameters": {...}
                }
        
        Returns:
            Resultado da execução da ação
        """
        with tracer.start_as_current_span("execute_ran_action") as span:
            span.set_attribute("agent.domain", self.domain)
            span.set_attribute("agent.id", self.agent_id)
            span.set_attribute("action.type", action.get("type", "unknown"))
            
            if self.nasp_client:
                try:
                    # Executar ação real via NASP Adapter
                    result = await self.nasp_client.execute_ran_action(action)
                    
                    executed = result.get("success", result.get("executed", False))
                    
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
                logger.warning("⚠️ NASP Adapter não disponível, ação não executada")
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
        
        Args:
            metrics: Métricas coletadas
        
        Returns:
            Resultado da avaliação de SLOs
        """
        with tracer.start_as_current_span("evaluate_ran_slos") as span:
            evaluation = self.slo_evaluator.evaluate(metrics)
            
            span.set_attribute("slo.status", evaluation.get("status"))
            span.set_attribute("slo.compliance_rate", evaluation.get("compliance_rate"))
            span.set_attribute("slo.violations_count", len(evaluation.get("violations", [])))
            
            # Publicar eventos I-06 para violações e riscos
            status = evaluation.get("status")
            if status in [SLOStatus.RISK, SLOStatus.VIOLATED]:
                # Publicar evento para cada SLO com problema
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
        """
        Retorna SLOs configurados para o domínio RAN
        
        Returns:
            Dicionário com SLOs e status atual (após coleta de métricas)
        """
        # Coletar métricas atuais
        metrics = await self.collect_metrics()
        
        # Avaliar SLOs
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
        """
        Loop autônomo de coleta de métricas, avaliação de SLOs e publicação de eventos
        
        Executa continuamente:
        1. Coleta métricas do NASP
        2. Avalia SLOs
        3. Publica eventos I-06 se houver violações/riscos
        """
        self.running = True
        logger.info(f"🔄 Iniciando loop autônomo do Agent RAN (intervalo: {self.poll_interval}s)")
        
        import asyncio
        
        while self.running:
            try:
                # 1. Coletar métricas
                metrics = await self.collect_metrics()
                
                # 2. Avaliar SLOs (já publica eventos I-06 internamente)
                evaluation = await self.evaluate_slos(metrics)
                
                # Log resumo
                status = evaluation.get("status")
                if status != SLOStatus.OK:
                    logger.warning(
                        f"⚠️ SLOs em {status}: domain={self.domain}, "
                        f"violations={len(evaluation.get('violations', []))}, "
                        f"risks={len(evaluation.get('risks', []))}"
                    )
                
                # Aguardar próximo ciclo
                await asyncio.sleep(self.poll_interval)
                
            except Exception as e:
                logger.error(f"❌ Erro no loop autônomo: {e}", exc_info=True)
                await asyncio.sleep(self.poll_interval)
    
    def stop_autonomous_loop(self):
        """Para o loop autônomo"""
        self.running = False
        logger.info("🛑 Parando loop autônomo do Agent RAN")
    
    def _get_timestamp(self) -> str:
        """Retorna timestamp atual"""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()
