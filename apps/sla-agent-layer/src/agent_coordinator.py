"""
Agent Coordinator - SLA-Agent Layer
Coordenação entre agentes federados (RAN, Transport, Core)
"""

from typing import Dict, Any, List, Optional
from opentelemetry import trace
import logging

# S29: Domain causal observability
try:
    from domain_snapshot import create_domain_snapshot
    from domain_compliance import compute_all_domains_compliance
    from system_xai import generate_causal_explanation
    S29_ENABLED = True
except ImportError:
    S29_ENABLED = False
    logger.warning("⚠️ Módulos S29 não disponíveis - observabilidade causal desabilitada")


tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)


class AgentCoordinator:
    """
    Coordenador de agentes federados
    
    Responsabilidades:
    - Coordenar ações entre múltiplos domínios
    - Implementar políticas federadas
    - Gerenciar colaboração entre agentes
    - Orquestrar ações multi-domínio
    """
    
    def __init__(self, agents: List):
        """
        Inicializa coordenador
        
        Args:
            agents: Lista de agentes (AgentRAN, AgentTransport, AgentCore)
        """
        self.agents = agents
        self.agent_map = {agent.domain.lower(): agent for agent in agents}
        logger.info(f"✅ AgentCoordinator inicializado com {len(agents)} agentes")
    
    async def coordinate_action(
        self,
        action: Dict[str, Any],
        target_domains: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Coordena ação entre múltiplos domínios
        
        Args:
            action: Ação a executar
            target_domains: Lista de domínios alvo (None = todos)
        
        Returns:
            Resultado da coordenação
        """
        with tracer.start_as_current_span("coordinate_action") as span:
            span.set_attribute("action.type", action.get("type", "unknown"))
            
            # Se não especificado, usar todos os domínios
            if target_domains is None:
                target_domains = [agent.domain for agent in self.agents]
            
            results = {}
            
            for domain in target_domains:
                domain_lower = domain.lower()
                agent = self.agent_map.get(domain_lower)
                
                if not agent:
                    logger.warning(f"⚠️ Agente não encontrado para domínio: {domain}")
                    results[domain] = {
                        "executed": False,
                        "error": f"Agent not found for domain: {domain}"
                    }
                    continue
                
                try:
                    # Executar ação no agente
                    result = await agent.execute_action(action)
                    results[domain] = result
                    
                    span.set_attribute(f"action.{domain_lower}.executed", result.get("executed", False))
                    
                except Exception as e:
                    logger.error(f"❌ Erro ao executar ação em {domain}: {e}")
                    results[domain] = {
                        "executed": False,
                        "error": str(e)
                    }
            
            # Determinar status geral
            executed_count = sum(1 for r in results.values() if r.get("executed", False))
            total_count = len(results)
            
            span.set_attribute("coordination.executed_count", executed_count)
            span.set_attribute("coordination.total_count", total_count)
            
            return {
                "action_type": action.get("type"),
                "target_domains": target_domains,
                "results": results,
                "executed_count": executed_count,
                "total_count": total_count,
                "success_rate": executed_count / total_count if total_count > 0 else 0.0,
                "timestamp": self._get_timestamp()
            }
    
    async def collect_all_metrics(self) -> Dict[str, Any]:
        """
        Coleta métricas de todos os agentes
        
        Returns:
            Métricas agregadas de todos os domínios
        """
        with tracer.start_as_current_span("collect_all_metrics") as span:
            all_metrics = {}
            
            for agent in self.agents:
                try:
                    metrics = await agent.collect_metrics()
                    all_metrics[agent.domain] = metrics
                    span.set_attribute(f"metrics.{agent.domain.lower()}.collected", True)
                except Exception as e:
                    logger.error(f"❌ Erro ao coletar métricas de {agent.domain}: {e}")
                    all_metrics[agent.domain] = {
                        "error": str(e),
                        "domain": agent.domain
                    }
            
            return {
                "domains": all_metrics,
                "total_domains": len(self.agents),
                "timestamp": self._get_timestamp()
            }
    
    async def evaluate_all_slos(self) -> Dict[str, Any]:
        """
        Avalia SLOs de todos os agentes
        
        Returns:
            Avaliação agregada de SLOs
        """
        with tracer.start_as_current_span("evaluate_all_slos") as span:
            all_evaluations = {}
            total_compliance = 0.0
            
            for agent in self.agents:
                try:
                    metrics = await agent.collect_metrics()
                    evaluation = await agent.evaluate_slos(metrics)
                    all_evaluations[agent.domain] = evaluation
                    
                    compliance_rate = evaluation.get("compliance_rate", 0.0)
                    total_compliance += compliance_rate
                    
                    span.set_attribute(f"slo.{agent.domain.lower()}.compliance", compliance_rate)
                except Exception as e:
                    logger.error(f"❌ Erro ao avaliar SLOs de {agent.domain}: {e}")
                    all_evaluations[agent.domain] = {
                        "error": str(e),
                        "domain": agent.domain
                    }
            
            overall_compliance = total_compliance / len(self.agents) if self.agents else 0.0
            
            span.set_attribute("slo.overall_compliance", overall_compliance)
            
            return {
                "evaluations": all_evaluations,
                "overall_compliance": overall_compliance,
                "total_domains": len(self.agents),
                "timestamp": self._get_timestamp()
            }
    
    async def apply_federated_policy(
        self,
        policy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Aplica política federada aos agentes
        
        Políticas federadas permitem:
        - Ações coordenadas entre domínios
        - Regras de prioridade
        - Dependências entre ações
        
        Args:
            policy: Política federada
                {
                    "name": "policy-name",
                    "priority": "high" | "medium" | "low",
                    "domains": ["RAN", "Transport", "Core"],
                    "actions": [
                        {
                            "domain": "RAN",
                            "action": {...},
                            "depends_on": ["Transport"]  # Opcional
                        }
                    ]
                }
        
        Returns:
            Resultado da aplicação da política
        """
        with tracer.start_as_current_span("apply_federated_policy") as span:
            policy_name = policy.get("name", "unknown")
            priority = policy.get("priority", "medium")
            actions = policy.get("actions", [])
            
            span.set_attribute("policy.name", policy_name)
            span.set_attribute("policy.priority", priority)
            span.set_attribute("policy.actions_count", len(actions))
            
            results = {}
            execution_order = self._determine_execution_order(actions)
            
            for action_item in execution_order:
                domain = action_item.get("domain")
                action = action_item.get("action", {})
                depends_on = action_item.get("depends_on", [])
                
                # Verificar dependências
                if depends_on:
                    all_deps_success = all(
                        results.get(dep, {}).get("executed", False)
                        for dep in depends_on
                    )
                    
                    if not all_deps_success:
                        logger.warning(
                            f"⚠️ Dependências não satisfeitas para {domain}. "
                            f"Dependências: {depends_on}"
                        )
                        results[domain] = {
                            "executed": False,
                            "error": "Dependencies not satisfied",
                            "depends_on": depends_on
                        }
                        continue
                
                # Executar ação
                agent = self.agent_map.get(domain.lower())
                if not agent:
                    results[domain] = {
                        "executed": False,
                        "error": f"Agent not found for domain: {domain}"
                    }
                    continue
                
                try:
                    result = await agent.execute_action(action)
                    results[domain] = result
                except Exception as e:
                    logger.error(f"❌ Erro ao executar ação em {domain}: {e}")
                    results[domain] = {
                        "executed": False,
                        "error": str(e)
                    }
            
            executed_count = sum(1 for r in results.values() if r.get("executed", False))
            
            return {
                "policy_name": policy_name,
                "priority": priority,
                "results": results,
                "executed_count": executed_count,
                "total_count": len(actions),
                "success_rate": executed_count / len(actions) if actions else 0.0,
                "timestamp": self._get_timestamp()
            }
    
    def _determine_execution_order(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Determina ordem de execução baseada em dependências
        
        Usa ordenação topológica simples
        """
        # Ordenação simples: ações sem dependências primeiro
        ordered = []
        remaining = actions.copy()
        
        while remaining:
            # Encontrar ações sem dependências não resolvidas
            for action_item in remaining[:]:
                depends_on = action_item.get("depends_on", [])
                
                if not depends_on:
                    # Sem dependências, pode executar
                    ordered.append(action_item)
                    remaining.remove(action_item)
                else:
                    # Verificar se dependências já foram resolvidas
                    resolved_deps = [
                        dep for dep in depends_on
                        if any(
                            a.get("domain") == dep
                            for a in ordered
                        )
                    ]
                    
                    if len(resolved_deps) == len(depends_on):
                        # Todas as dependências resolvidas
                        ordered.append(action_item)
                        remaining.remove(action_item)
            
            # Se não conseguiu adicionar nenhuma, pode haver ciclo
            if not ordered or (remaining and len(ordered) == len([a for a in actions if a not in remaining])):
                # Adicionar as restantes mesmo assim (pode haver erro de configuração)
                ordered.extend(remaining)
                break
        
        return ordered
    
    async def create_causal_snapshot_for_sla(
        self,
        sla_id: str,
        slice_type: str = "EMBB",
        sla_requirements: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Cria snapshot causal e explicação para um SLA (S29)
        """
        if not S29_ENABLED:
            logger.warning("⚠️ S29 desabilitado - snapshot causal não criado")
            return {}
        
        with tracer.start_as_current_span("create_causal_snapshot_s29") as span:
            span.set_attribute("sla.id", sla_id)
            span.set_attribute("slice.type", slice_type)
            
            try:
                all_metrics = await self.collect_all_metrics()
                metrics_ran = all_metrics.get("domains", {}).get("RAN", {})
                metrics_transport = all_metrics.get("domains", {}).get("Transport", {})
                metrics_core = all_metrics.get("domains", {}).get("Core", {})
                
                snapshot = create_domain_snapshot(
                    sla_id=sla_id,
                    metrics_ran=metrics_ran,
                    metrics_transport=metrics_transport,
                    metrics_core=metrics_core
                )
                
                from domain_compliance import compute_all_domains_compliance
                domain_compliance = compute_all_domains_compliance(
                    metrics_ran=metrics_ran,
                    metrics_transport=metrics_transport,
                    metrics_core=metrics_core,
                    slice_type=slice_type,
                    sla_requirements=sla_requirements
                )
                
                span.set_attribute("s29.snapshot.created", True)
                logger.info(f"✅ Snapshot causal S29 criado para SLA {sla_id}")
                
                return {
                    "snapshot": snapshot,
                    "domain_compliance": domain_compliance,
                    "timestamp": snapshot.get("timestamp")
                }
            except Exception as e:
                span.record_exception(e)
                logger.error(f"❌ Erro ao criar snapshot causal S29: {e}")
                return {}
    
    async def generate_causal_explanation_for_decision(
        self,
        sla_id: str,
        decision: str,
        slice_type: str = "EMBB",
        sla_requirements: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Gera explicação causal para uma decisão (S29)
        """
        if not S29_ENABLED:
            return {}
        
        with tracer.start_as_current_span("generate_causal_explanation_s29") as span:
            span.set_attribute("sla.id", sla_id)
            span.set_attribute("decision", decision)
            
            try:
                all_metrics = await self.collect_all_metrics()
                metrics_ran = all_metrics.get("domains", {}).get("RAN", {})
                metrics_transport = all_metrics.get("domains", {}).get("Transport", {})
                metrics_core = all_metrics.get("domains", {}).get("Core", {})
                
                from domain_compliance import compute_all_domains_compliance
                domain_compliance = compute_all_domains_compliance(
                    metrics_ran=metrics_ran,
                    metrics_transport=metrics_transport,
                    metrics_core=metrics_core,
                    slice_type=slice_type,
                    sla_requirements=sla_requirements
                )
                
                explanation = generate_causal_explanation(
                    sla_id=sla_id,
                    decision=decision,
                    domain_compliance=domain_compliance
                )
                
                logger.info(f"✅ Explicação causal S29 gerada para SLA {sla_id}: {decision}")
                return explanation
            except Exception as e:
                span.record_exception(e)
                logger.error(f"❌ Erro ao gerar explicação causal S29: {e}")
                return {}

    def _get_timestamp(self) -> str:
        """Retorna timestamp atual"""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()






