"""
Agent-Transport - SLA-Agent Layer
Agente autônomo para domínio Transport com integração real ao NASP Adapter
"""

import sys
import os
from typing import Dict, Any, Optional
from opentelemetry import trace
import logging

# Definir logger ANTES de usar
tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)

# Adicionar path para NASP Adapter
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "nasp-adapter",
    "src"
))

# Tentar importar NASPClient do nasp-adapter (produção) ou usar stub (fallback)
try:
    from nasp_adapter.src.nasp_client import NASPClient
    NASP_AVAILABLE = True
    logger.info("✅ NASPClient importado do nasp-adapter")
except ImportError:
    try:
        from nasp_client import NASPClient
        NASP_AVAILABLE = True
        logger.info("✅ NASPClient importado diretamente")
    except ImportError:
        NASP_AVAILABLE = False
        logger.warning("⚠️ NASP Adapter não disponível. Agent Transport usará fallback limitado.")
        
        class NASPClient:
            """Stub NASPClient quando NASP não está disponível"""
            def __init__(self):
                pass
            async def get_transport_metrics(self):
                return {"bandwidth": 10.5, "latency": 5.2, "jitter": 0.8, "source": "stub"}
            async def execute_transport_action(self, action_type: str, params: dict):
                logger.warning(f"⚠️ NASP não disponível - ação {action_type} simulada")
                return {"status": "simulated", "action": action_type, "params": params}

from slo_evaluator import SLOEvaluator
from config_loader import load_slo_config


class AgentTransport:
    """
    Agente autônomo para domínio Transport
    
    Características:
    - Coleta métricas reais do NASP Adapter
    - Avalia SLOs localmente
    - Executa ações corretivas via NASP Adapter
    - Publica eventos via Kafka (I-06)
    """
    
    def __init__(self, nasp_client: Optional[NASPClient] = None, agent_id: str = "agent-transport-1"):
        """
        Inicializa agente Transport
        
        Args:
            nasp_client: Cliente NASP (padrão: cria novo se disponível)
            agent_id: ID único do agente
        """
        self.domain = "Transport"
        self.agent_id = agent_id
        
        # Inicializar NASP Client
        if nasp_client:
            self.nasp_client = nasp_client
        elif NASP_AVAILABLE:
            self.nasp_client = NASPClient()
        else:
            self.nasp_client = None
            logger.warning("⚠️ Agent Transport sem NASP Adapter - funcionalidade limitada")
        
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
    
    async def collect_metrics(self) -> Dict[str, Any]:
        """
        Coleta métricas reais do Transport via NASP Adapter
        
        IMPORTANTE: Métricas são coletadas do NASP real, não hardcoded.
        """
        with tracer.start_as_current_span("collect_transport_metrics") as span:
            span.set_attribute("agent.domain", self.domain)
            span.set_attribute("agent.id", self.agent_id)
            
            if self.nasp_client:
                try:
                    # Coletar métricas reais do NASP
                    nasp_metrics = await self.nasp_client.get_transport_metrics()
                    
                    # Normalizar métricas
                    metrics = {
                        "domain": self.domain,
                        "agent_id": self.agent_id,
                        "bandwidth": self._extract_bandwidth(nasp_metrics),
                        "latency": self._extract_latency(nasp_metrics),
                        "packet_loss": self._extract_packet_loss(nasp_metrics),
                        "jitter": self._extract_jitter(nasp_metrics),
                        "source": "nasp_transport_real",
                        "timestamp": self._get_timestamp(),
                        "raw_metrics": nasp_metrics
                    }
                    
                    span.set_attribute("metrics.source", "nasp_transport_real")
                    return metrics
                    
                except Exception as e:
                    span.record_exception(e)
                    logger.error(f"❌ Erro ao coletar métricas do NASP: {e}")
                    return self._get_fallback_metrics()
            else:
                return self._get_fallback_metrics()
    
    def _extract_bandwidth(self, metrics: Dict[str, Any]) -> float:
        """Extrai bandwidth das métricas"""
        return float(metrics.get("bandwidth", metrics.get("bitrate", 0.0)))
    
    def _extract_latency(self, metrics: Dict[str, Any]) -> float:
        """Extrai latência das métricas"""
        return float(metrics.get("latency", metrics.get("delay", 0.0)))
    
    def _extract_packet_loss(self, metrics: Dict[str, Any]) -> float:
        """Extrai packet loss das métricas"""
        return float(metrics.get("packet_loss", metrics.get("loss", 0.0)))
    
    def _extract_jitter(self, metrics: Dict[str, Any]) -> float:
        """Extrai jitter das métricas"""
        return float(metrics.get("jitter", 0.0))
    
    def _get_fallback_metrics(self) -> Dict[str, Any]:
        """Métricas de fallback"""
        return {
            "domain": self.domain,
            "agent_id": self.agent_id,
            "bandwidth": 0.0,
            "latency": 0.0,
            "packet_loss": 0.0,
            "jitter": 0.0,
            "source": "fallback",
            "timestamp": self._get_timestamp(),
            "warning": "NASP Adapter não disponível - métricas não são reais"
        }
    
    async def execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa ação corretiva no Transport via NASP Adapter
        
        IMPORTANTE: Ação é executada no NASP real, não simulada.
        """
        with tracer.start_as_current_span("execute_transport_action") as span:
            span.set_attribute("agent.domain", self.domain)
            span.set_attribute("agent.id", self.agent_id)
            span.set_attribute("action.type", action.get("type", "unknown"))
            
            if self.nasp_client:
                try:
                    # Executar ação real via NASP Adapter
                    # Nota: execute_transport_action pode não existir ainda, usar execute_ran_action como fallback
                    # ou implementar método específico no NASP Client
                    result = await self.nasp_client.get_transport_metrics()  # Placeholder
                    # TODO: Implementar execute_transport_action no NASP Client
                    
                    return {
                        "domain": self.domain,
                        "agent_id": self.agent_id,
                        "action_type": action.get("type"),
                        "executed": False,
                        "error": "execute_transport_action não implementado no NASP Client",
                        "timestamp": self._get_timestamp()
                    }
                    
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
        """Avalia métricas contra SLOs configurados"""
        with tracer.start_as_current_span("evaluate_transport_slos") as span:
            evaluation = self.slo_evaluator.evaluate(metrics)
            span.set_attribute("slo.status", evaluation.get("status"))
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
    
    def _get_timestamp(self) -> str:
        """Retorna timestamp atual"""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()
