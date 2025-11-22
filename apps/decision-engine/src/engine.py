"""
Engine de Decisão - Decision Engine
Motor principal que orquestra SEM-CSMF, ML-NSMF e BC-NSSMF para tomar decisões AC/RENEG/REJ
Alinhado com arquitetura TriSLA (Capítulos 4, 5, 6)
"""

from typing import Optional
from opentelemetry import trace

from models import (
    DecisionInput, DecisionResult, DecisionAction,
    SLARequirement, RiskLevel, SliceType
)
from sem_client import SEMClient
from ml_client import MLClient
from bc_client import BCClient

tracer = trace.get_tracer(__name__)


class DecisionEngine:
    """
    Motor de Decisão Principal
    Orquestra o fluxo: SEM-CSMF → ML-NSMF → Regras → BC-NSSMF
    """
    
    def __init__(self):
        self.sem_client = SEMClient()
        self.ml_client = MLClient()
        self.bc_client = BCClient()
    
    async def decide(
        self,
        intent_id: str,
        nest_id: Optional[str] = None,
        context: Optional[dict] = None
    ) -> DecisionResult:
        """
        Fluxo principal de decisão:
        1. Busca intent/NEST do SEM-CSMF
        2. Obtém previsão de risco do ML-NSMF
        3. Aplica regras de decisão (thresholds, domínios, tipos de slice)
        4. Registra no BC-NSSMF se aceito
        5. Retorna decisão final
        
        Args:
            intent_id: ID do intent
            nest_id: ID do NEST (opcional)
            context: Contexto adicional (opcional)
        
        Returns:
            DecisionResult com ação e justificativa
        """
        with tracer.start_as_current_span("decision_engine_decide") as span:
            span.set_attribute("intent.id", intent_id)
            
            decision_id = f"dec-{intent_id}"
            
            # 1. Buscar intent e NEST do SEM-CSMF
            intent = await self.sem_client.fetch_semantic_sla(intent_id)
            if not intent:
                # Se não encontrar, criar intent básico
                from models import SliceType
                intent = await self._create_fallback_intent(intent_id, context)
            
            nest = None
            if nest_id:
                nest = await self.sem_client.fetch_nest_by_intent_id(nest_id)
            elif intent.nest_id:
                nest = await self.sem_client.fetch_nest_by_intent_id(intent.nest_id)
            
            # 2. Agregar dados para o ML
            decision_input = DecisionInput(
                intent=intent,
                nest=nest,
                context=context or {}
            )
            
            # 3. Obter previsão do ML-NSMF (Interface I-05)
            ml_prediction = await self.ml_client.predict_viability(decision_input)
            decision_input.ml_prediction = ml_prediction
            
            span.set_attribute("ml.risk_score", ml_prediction.risk_score)
            span.set_attribute("ml.risk_level", ml_prediction.risk_level.value)
            
            # 4. Aplicar regras de decisão
            action, reasoning, slos, domains = self._apply_decision_rules(
                intent, nest, ml_prediction, context
            )
            
            span.set_attribute("decision.action", action.value)
            
            # 5. Construir resultado da decisão
            decision_result = DecisionResult(
                decision_id=decision_id,
                intent_id=intent_id,
                nest_id=nest.nest_id if nest else None,
                action=action,
                reasoning=reasoning,
                confidence=ml_prediction.confidence,
                ml_risk_score=ml_prediction.risk_score,
                ml_risk_level=ml_prediction.risk_level,
                slos=slos,
                domains=domains,
                metadata={
                    "ml_explanation": ml_prediction.explanation,
                    "ml_features_importance": ml_prediction.features_importance
                }
            )
            
            # 6. Registrar no blockchain se aceito (Interface I-06)
            blockchain_tx_hash = None
            if action == DecisionAction.ACCEPT:
                blockchain_tx_hash = await self.bc_client.register_sla_on_chain(decision_result)
                if blockchain_tx_hash:
                    decision_result.metadata["blockchain_tx_hash"] = blockchain_tx_hash
                    span.set_attribute("bc.tx_hash", blockchain_tx_hash)
            
            return decision_result
    
    def _apply_decision_rules(
        self,
        intent,
        nest,
        ml_prediction,
        context: Optional[dict]
    ) -> tuple:
        """
        Aplica regras de decisão usando RuleEngine (YAML-based, sem hardcoded)
        
        Returns:
            (action, reasoning, slos, domains)
        """
        from rule_engine import RuleEngine
        
        # Extrair SLOs do intent
        slos = []
        sla_reqs = intent.sla_requirements
        
        # Latência
        if "latency" in sla_reqs:
            latency_str = str(sla_reqs["latency"]).replace("ms", "").strip()
            try:
                latency_value = float(latency_str)
                slos.append(SLARequirement(
                    name="latency",
                    value=latency_value,
                    threshold=latency_value,
                    unit="ms"
                ))
            except (ValueError, TypeError):
                pass
        
        # Reliability
        if "reliability" in sla_reqs:
            reliability_value = float(sla_reqs.get("reliability", 0.99))
            slos.append(SLARequirement(
                name="reliability",
                value=reliability_value,
                threshold=reliability_value,
                unit="ratio"
            ))
        
        # Throughput
        if "throughput" in sla_reqs:
            throughput_str = str(sla_reqs["throughput"]).replace("Mbps", "").replace("Gbps", "000").strip()
            try:
                throughput_value = float(throughput_str)
                slos.append(SLARequirement(
                    name="throughput",
                    value=throughput_value,
                    threshold=throughput_value,
                    unit="Mbps"
                ))
            except (ValueError, TypeError):
                pass
        
        # Determinar domínios afetados
        domains = []
        service_type = intent.service_type
        
        if service_type == SliceType.URLLC:
            domains = ["RAN", "Transporte", "Core"]
        elif service_type == SliceType.EMBB:
            domains = ["RAN", "Transporte"]
        elif service_type == SliceType.MMTC:
            domains = ["RAN", "Core"]
        
        # Calcular SLA compliance (simplificado - pode ser melhorado)
        sla_compliance = 0.95  # Padrão
        if slos:
            # Calcular compliance baseado em quantos SLOs são viáveis
            # (Em produção, isso seria mais complexo)
            sla_compliance = min(1.0, 0.95 + (len(slos) * 0.01))
        
        # Construir contexto para RuleEngine
        rule_context = {
            "risk_level": ml_prediction.risk_level.value,
            "risk_score": ml_prediction.risk_score,
            "service_type": service_type.value,
            "sla_compliance": sla_compliance,
            "latency": slos[0].value if slos and slos[0].name == "latency" else 0.0,
            "throughput": next((slo.value for slo in slos if slo.name == "throughput"), 0.0),
            "reliability": next((slo.value for slo in slos if slo.name == "reliability"), 0.99),
            "confidence": ml_prediction.confidence,
            "domains": domains,
            "explanation": ml_prediction.explanation or ""
        }
        
        # Usar RuleEngine para avaliar regras (YAML-based, sem hardcoded)
        rule_engine = RuleEngine()
        import asyncio
        rules_result = asyncio.run(rule_engine.evaluate(rule_context))
        
        # Converter ação string para enum
        action_str = rules_result.get("action", "ACCEPT")
        if action_str == "REJECT":
            action = DecisionAction.REJECT
        elif action_str == "NEGOTIATE" or action_str == "RENEGOTIATE":
            action = DecisionAction.RENEGOTIATE
        else:
            action = DecisionAction.ACCEPT
        
        reasoning = rules_result.get("reasoning", "Decisão baseada em regras")
        
        return (action, reasoning, slos, domains)
    
    async def _create_fallback_intent(self, intent_id: str, context: Optional[dict]) -> 'SLAIntent':
        """Cria intent de fallback se não encontrar no SEM-CSMF"""
        from models import SliceType, SLAIntent
        
        return SLAIntent(
            intent_id=intent_id,
            tenant_id=context.get("tenant_id") if context else None,
            service_type=SliceType(context.get("service_type", "eMBB")) if context else SliceType.EMBB,
            sla_requirements=context.get("sla_requirements", {}) if context else {},
            metadata=context
        )
    
    async def close(self):
        """Fecha conexões com clientes"""
        await self.sem_client.close()
        await self.ml_client.close()

