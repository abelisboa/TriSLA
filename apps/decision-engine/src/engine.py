"""
Engine de Decisão - Decision Engine
Motor principal que orquestra SEM-CSMF, ML-NSMF e BC-NSSMF para tomar decisões AC/RENEG/REJ
Alinhado com arquitetura TriSLA (Capítulos 4, 5, 6)
"""

import os
from typing import Optional
from datetime import datetime
from opentelemetry import trace

from models import (
    DecisionInput, DecisionResult, DecisionAction,
    SLARequirement, RiskLevel, SliceType
)
from sem_client import SEMClient
from ml_client import MLClient
from bc_client import BCClient
from resource_evaluator import ResourceEvaluator
from decision_snapshot import build_decision_snapshot
from system_xai import explain_decision
from decision_persistence import persist_decision_evidence
from decision_thresholds import thresholds_for_slice
import logging
import json

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)

# Fase 3/4: α configurável (limiares e classificador inalterados; calibrar via env no deploy).
PRB_RISK_ALPHA = float(os.getenv("PRB_RISK_ALPHA", "0.15"))

# Fase 5: precedência hard PRB → risco (limiares) → refinamento ML (reversível via env).
POLICY_GOVERNED_MODE = os.getenv("POLICY_GOVERNED_MODE", "true").lower() == "true"
ML_CAN_OVERRIDE_REJECT = os.getenv("ML_CAN_OVERRIDE_REJECT", "false").lower() == "true"
ML_REFINEMENT_CONFIDENCE = float(os.getenv("ML_REFINEMENT_CONFIDENCE", "0.6"))
HARD_PRB_REJECT_THRESHOLD = float(os.getenv("HARD_PRB_REJECT_THRESHOLD", "95"))
HARD_PRB_RENEGOTIATE_THRESHOLD = float(os.getenv("HARD_PRB_RENEGOTIATE_THRESHOLD", "85"))


def decision_exposure_from_xai_bundle(xai_bundle: Optional[dict]) -> dict:
    """
    Mapeia o bundle interno de _apply_decision_rules para campos de API estáveis.
    Não altera decisões — apenas normaliza rótulos (ex.: classification → classifier).
    """
    if not xai_bundle:
        return {}
    dm = xai_bundle.get("decision_mode")
    if dm == "classification":
        mode = "classifier"
    elif dm == "threshold_fallback":
        mode = "threshold"
    else:
        mode = dm
    fdc = xai_bundle.get("final_decision_confidence")
    try:
        conf = float(fdc) if fdc is not None else None
    except (TypeError, ValueError):
        conf = None
    return {
        "decision_mode": mode,
        "threshold_decision": xai_bundle.get("threshold_decision"),
        "final_decision": xai_bundle.get("final_decision"),
        "confidence_score": conf,
        "predicted_decision_class": xai_bundle.get("predicted_decision_class"),
    }


class DecisionEngine:
    """
    Motor de Decisão Principal
    Orquestra o fluxo: SEM-CSMF → ML-NSMF → Regras → BC-NSSMF
    """
    
    def __init__(self):
        self.sem_client = SEMClient()
        self.ml_client = MLClient()
        self.bc_client = BCClient()
        self.resource_evaluator = ResourceEvaluator()
    
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
            
            # 3.5. Avaliar recursos disponíveis
            resources = await self.resource_evaluator.evaluate_resources()
            span.set_attribute("resources.cpu_score", resources.get("cpu_score", 0.5))
            span.set_attribute("resources.memory_score", resources.get("memory_score", 0.5))
            span.set_attribute("resources.disk_score", resources.get("disk_score", 0.5))
            span.set_attribute("resources.network_score", resources.get("network_score", 0.5))
            
            # 4. Aplicar regras de decisão
            action, reasoning, slos, domains, xai_bundle = self._apply_decision_rules(
                intent, nest, ml_prediction, context
            )
            
            span.set_attribute("decision.action", action.value)
            
            # FASE 4 (C4): Capturar timestamp de decisão
            t_decision = datetime.utcnow().isoformat() + 'Z'
            
            # 5. Construir resultado da decisão
            _fdc = (xai_bundle or {}).get("final_decision_confidence")
            _conf = float(_fdc) if _fdc is not None else float(ml_prediction.confidence)

            _exp = decision_exposure_from_xai_bundle(xai_bundle)
            _meta = {
                "ml_explanation": ml_prediction.explanation,
                "ml_features_importance": ml_prediction.features_importance,
                "t_decision": t_decision,
                **(xai_bundle or {}),
            }
            _meta.update(_exp)

            decision_result = DecisionResult(
                decision_id=decision_id,
                intent_id=intent_id,
                nest_id=nest.nest_id if nest else None,
                action=action,
                reasoning=reasoning,
                confidence=_conf,
                ml_risk_score=ml_prediction.risk_score,
                ml_risk_level=ml_prediction.risk_level,
                slos=slos,
                domains=domains,
                metadata=_meta,
                decision_mode=_exp.get("decision_mode"),
                threshold_decision=_exp.get("threshold_decision"),
                final_decision=_exp.get("final_decision"),
                confidence_score=_exp.get("confidence_score"),
                predicted_decision_class=_exp.get("predicted_decision_class"),
            )
            
            # 6. Registrar no blockchain se aceito (Interface I-06)
            blockchain_tx_hash = None
            if action == DecisionAction.ACCEPT:
                pass  # TODO: Implement blockchain registration
                pass  # TODO: Implement blockchain registration
            if blockchain_tx_hash:
                decision_result.metadata["blockchain_tx_hash"] = blockchain_tx_hash
                span.set_attribute("bc.tx_hash", blockchain_tx_hash)
            
            # PROMPT_S30 - FASE 1, 2, 3, 4: Snapshot, XAI, Persistência e Kafka
            decision_context = {
                'intent': intent,
                'nest': nest,
                'ml_prediction': ml_prediction,
                'resources': resources
            }
            try:
                snapshot = build_decision_snapshot(decision_context, decision_result)
                explanation = explain_decision(snapshot, decision_result)
                persist_decision_evidence(intent_id, snapshot, explanation)
                try:
                    from kafka_producer import DecisionProducer
                    kafka_producer = DecisionProducer()
                    kafka_event = {
                        "sla_id": intent_id,
                        "decision": decision_result.action.value,
                        "snapshot": snapshot,
                        "explanation": explanation,
                        "timestamp": snapshot.get("timestamp_utc"),
                        "decision_id": decision_result.decision_id
                    }
                    if kafka_producer.producer is not None:
                        kafka_producer.producer.send('trisla-decision-events', value=kafka_event)
                        kafka_producer.producer.flush()
                except Exception as kafka_error:
                    logger.warning(f"Kafka error for {intent_id}: {kafka_error}")
                decision_result.metadata["decision_snapshot"] = snapshot
                decision_result.metadata["system_xai_explanation"] = explanation
            except Exception as e:
                logger.error(f"PROMPT_S30 error for {intent_id}: {e}", exc_info=True)
            
            return decision_result
    
    def _apply_decision_rules(
        self,
        intent,
        nest,
        ml_prediction,
        context: Optional[dict]
    ) -> tuple:
        """
        Aplica regras de decisão baseadas em:
        - Tipo de slice (URLLC/eMBB/mMTC)
        - Previsão do ML (risk_score, risk_level)
        - Thresholds de SLOs
        - Domínios afetados (RAN/Transporte/Core)
        
        Returns:
            (action, reasoning, slos, domains)
        """
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
            reliability_raw = sla_reqs.get("reliability", 0.99)
            try:
                reliability_value = float(reliability_raw) if reliability_raw is not None else 0.99
            except (ValueError, TypeError):
                reliability_value = 0.99
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
            domains = ["RAN", "Transporte", "Core"]  # URLLC requer todos os domínios
        elif service_type == SliceType.EMBB:
            domains = ["RAN", "Transporte"]  # eMBB foca em RAN e transporte
        elif service_type == SliceType.MMTC:
            domains = ["RAN", "Core"]  # mMTC foca em RAN e core
        
        raw_risk_score = float(
            ml_prediction.raw_risk_score
            if ml_prediction.raw_risk_score is not None
            else ml_prediction.risk_score
        )
        slice_adjusted = float(
            ml_prediction.slice_adjusted_risk_score
            if ml_prediction.slice_adjusted_risk_score is not None
            else raw_risk_score
        )
        slice_label = service_type.value
        t_accept, t_reneg, thresholds_used = thresholds_for_slice(slice_label)

        ran_prb_raw = None
        transport_latency_input = None
        core_cpu_input = None
        core_memory_input = None
        if context and isinstance(context, dict):
            _ts = context.get("telemetry_snapshot") or {}
            ran_prb_raw = (_ts.get("ran") or {}).get("prb_utilization")
            _tr = _ts.get("transport") or {}
            _cr = _ts.get("core") or {}
            transport_latency_input = _tr.get("latency_ms")
            if transport_latency_input is None:
                transport_latency_input = _tr.get("rtt")
            core_cpu_input = _cr.get("cpu_utilization")
            core_memory_input = _cr.get("memory_utilization")

        ml_risk_for_prb = float(slice_adjusted)
        final_risk = ml_risk_for_prb
        if ran_prb_raw is not None:
            try:
                prb_norm = max(0.0, min(float(ran_prb_raw) / 100.0, 1.0))
                final_risk = min(1.0, ml_risk_for_prb + PRB_RISK_ALPHA * prb_norm)
            except (TypeError, ValueError):
                final_risk = ml_risk_for_prb

        print(
            f"[RAN AWARE] ml={ml_risk_for_prb:.4f} prb={ran_prb_raw} "
            f"alpha={PRB_RISK_ALPHA} final={final_risk:.4f}"
        )
        logger.info(
            "[RAN AWARE] ml=%.4f prb=%s alpha=%s final=%.4f",
            ml_risk_for_prb,
            ran_prb_raw,
            PRB_RISK_ALPHA,
            final_risk,
        )

        risk_for_decision = final_risk

        top_factors = ml_prediction.top_factors or []
        dom = ml_prediction.dominant_domain or "unknown"

        def _factor_names() -> str:
            if not top_factors:
                return "indisponível"
            out = []
            for item in top_factors[:3]:
                if isinstance(item, dict) and item.get("factor"):
                    out.append(str(item["factor"]))
            return ", ".join(out) if out else "indisponível"

        def _action_to_label(a: DecisionAction) -> str:
            return {"AC": "ACCEPT", "RENEG": "RENEGOTIATE", "REJ": "REJECT"}[a.value]

        def _label_to_action(label: str) -> DecisionAction:
            u = (label or "").strip().upper()
            if u == "ACCEPT":
                return DecisionAction.ACCEPT
            if u == "RENEGOTIATE":
                return DecisionAction.RENEGOTIATE
            if u == "REJECT":
                return DecisionAction.REJECT
            return DecisionAction.RENEGOTIATE

        if risk_for_decision < t_accept:
            threshold_action = DecisionAction.ACCEPT
        elif risk_for_decision < t_reneg:
            threshold_action = DecisionAction.RENEGOTIATE
        else:
            threshold_action = DecisionAction.REJECT

        threshold_decision_str = _action_to_label(threshold_action)
        cls_str = ml_prediction.predicted_decision_class
        cls_conf = (
            float(ml_prediction.classifier_confidence)
            if ml_prediction.classifier_confidence is not None
            else 0.0
        )

        if os.getenv("DECISION_SCORE_MODE", "false").lower() == "true":
            from decision_score_mode import score_mode_decide

            return score_mode_decide(
                intent=intent,
                nest=nest,
                ml_prediction=ml_prediction,
                context=context,
                slos=slos,
                domains=domains,
                raw_risk_score=raw_risk_score,
                slice_adjusted=slice_adjusted,
                final_risk=final_risk,
                ran_prb_raw=ran_prb_raw,
                slice_label=slice_label,
                transport_latency_input=transport_latency_input,
                core_cpu_input=core_cpu_input,
                core_memory_input=core_memory_input,
                prb_risk_alpha=PRB_RISK_ALPHA,
                top_factors=top_factors,
                dom=dom,
                cls_str=cls_str,
                cls_conf=cls_conf,
                hard_prb_reject=HARD_PRB_REJECT_THRESHOLD,
                hard_prb_reneg=HARD_PRB_RENEGOTIATE_THRESHOLD,
            )

        decision_source = "unknown"
        decision: DecisionAction
        final_decision_confidence: float
        decision_mode: str
        use_classifier: bool

        if POLICY_GOVERNED_MODE:
            policy_decision: Optional[DecisionAction] = None

            if ran_prb_raw is not None:
                try:
                    prb_value = float(ran_prb_raw)
                    if prb_value >= HARD_PRB_REJECT_THRESHOLD:
                        policy_decision = DecisionAction.REJECT
                        decision_source = "policy_hard_reject"
                    elif prb_value >= HARD_PRB_RENEGOTIATE_THRESHOLD:
                        policy_decision = DecisionAction.RENEGOTIATE
                        decision_source = "policy_hard_renegotiate"
                except Exception:
                    policy_decision = None

            if policy_decision is None:
                if final_risk >= t_reneg:
                    policy_decision = DecisionAction.REJECT
                    decision_source = "policy_risk"
                elif final_risk >= t_accept:
                    policy_decision = DecisionAction.RENEGOTIATE
                    decision_source = "policy_risk"

            if policy_decision is not None:
                decision = policy_decision
                final_decision_confidence = float(ml_prediction.confidence)
                decision_mode = "policy_governed"
                use_classifier = False
                logger.info(
                    "[ENGINE] policy_governed source=%s decision=%s",
                    decision_source,
                    _action_to_label(decision),
                )
            else:
                if cls_conf >= ML_REFINEMENT_CONFIDENCE and cls_str and str(cls_str).strip():
                    cls_label = str(cls_str).strip().upper()
                    if not ML_CAN_OVERRIDE_REJECT and cls_label == "REJECT":
                        decision = DecisionAction.RENEGOTIATE
                        decision_source = "ml_refinement_safe"
                    else:
                        decision = _label_to_action(cls_label)
                        decision_source = "ml_refinement"
                    final_decision_confidence = cls_conf
                    decision_mode = "policy_governed"
                    use_classifier = True
                    logger.info(
                        "[ENGINE] policy_governed ml_refinement source=%s decision=%s conf=%.3f",
                        decision_source,
                        _action_to_label(decision),
                        cls_conf,
                    )
                else:
                    decision = DecisionAction.ACCEPT
                    decision_source = "fallback_accept"
                    final_decision_confidence = float(ml_prediction.confidence)
                    decision_mode = "policy_governed"
                    use_classifier = False
                    logger.info(
                        "[ENGINE] policy_governed fallback_accept conf=%.3f",
                        cls_conf,
                    )
        else:
            use_classifier = (
                bool(cls_str and str(cls_str).strip())
                and cls_conf >= ML_REFINEMENT_CONFIDENCE
            )
            if use_classifier:
                decision = _label_to_action(str(cls_str))
                final_decision_confidence = cls_conf
                decision_mode = "classification"
                decision_source = "legacy_classification"
                logger.info(
                    "[ENGINE] mode=classifier confidence=%.3f decision=%s",
                    cls_conf,
                    _action_to_label(decision),
                )
            else:
                decision = threshold_action
                final_decision_confidence = float(ml_prediction.confidence)
                decision_mode = "threshold_fallback"
                decision_source = "legacy_threshold_fallback"
                logger.info(
                    "[ENGINE] mode=threshold decision=%s",
                    threshold_decision_str,
                )

        action_plain = {"AC": "ACCEPT", "RENEG": "RENEGOTIATE", "REJ": "REJECT"}.get(
            decision.value, decision.value
        )
        final_label = _action_to_label(decision)
        divergence = bool(cls_str) and str(cls_str).strip().upper() != threshold_decision_str

        print(
            f"[HYBRID DECISION] prb={ran_prb_raw} ml={ml_risk_for_prb:.4f} "
            f"final={final_risk:.4f} conf={cls_conf:.3f} "
            f"decision={final_label} source={decision_source}"
        )
        logger.info(
            "[HYBRID DECISION] prb=%s ml=%.4f final=%.4f conf=%.3f decision=%s source=%s",
            ran_prb_raw,
            ml_risk_for_prb,
            final_risk,
            cls_conf,
            final_label,
            decision_source,
        )

        decision_explanation_technical = (
            f"source={decision_source} policy_governed={POLICY_GOVERNED_MODE} "
            f"confidence {final_decision_confidence:.3f}, adjusted risk {slice_adjusted:.3f}, "
            f"ran_aware_risk {final_risk:.3f}, dominant domain {dom}; "
            f"predicted_decision_class={cls_str} threshold_decision={threshold_decision_str} "
            f"final_decision={final_label} divergence={divergence}"
        )
        if POLICY_GOVERNED_MODE:
            if decision_source.startswith("policy_hard"):
                decision_explanation_plain = (
                    f"A decisão foi {action_plain} por política de PRB (prb={ran_prb_raw}); "
                    f"risco pós-PRB {final_risk:.2f}; domínio {dom}."
                )
            elif decision_source == "policy_risk":
                decision_explanation_plain = (
                    f"A decisão foi {action_plain} por limiar de risco (pós-PRB {final_risk:.2f} "
                    f"vs accept={t_accept:.2f} renegotiate={t_reneg:.2f}); domínio {dom}."
                )
            elif use_classifier:
                decision_explanation_plain = (
                    f"A decisão foi {action_plain} por refinamento ML (fonte={decision_source}) "
                    f"com confiança {cls_conf:.2f}; risco pós-PRB {final_risk:.2f}; "
                    f"domínio {dom} (fatores: {_factor_names()})."
                )
            else:
                decision_explanation_plain = (
                    f"A decisão foi {action_plain} (confiança ML {cls_conf:.2f} abaixo do limiar "
                    f"ou classe indisponível); risco pós-PRB {final_risk:.2f}; domínio {dom}."
                )
        elif use_classifier:
            decision_explanation_plain = (
                f"A decisão foi {action_plain} porque o modelo de classificação SLA-aware "
                f"indicou confiança {cls_conf:.2f}, risco ajustado (ML) {slice_adjusted:.2f}, "
                f"risco pós-PRB {final_risk:.2f} e domínio dominante {dom} (fatores: {_factor_names()})."
            )
        else:
            decision_explanation_plain = (
                f"A decisão foi {action_plain} (fallback por limiar) porque a confiança do classificador "
                f"foi {cls_conf:.2f} ou classe indisponível; risco pós-PRB {final_risk:.2f} "
                f"(ML ajustado {slice_adjusted:.2f}, bruto {raw_risk_score:.2f}) vs limiares "
                f"accept={t_accept:.2f} renegotiate={t_reneg:.2f}; domínio {dom}; fatores: {_factor_names()}."
            )
        reasoning = (
            f"{decision_explanation_plain} Domínios considerados: {', '.join(domains)}. "
            f"{ml_prediction.explanation or ''}"
        )

        xai_bundle = {
            "raw_risk_score": raw_risk_score,
            "slice_adjusted_risk_score": slice_adjusted,
            "ran_prb_utilization_input": ran_prb_raw,
            "transport_latency_input": transport_latency_input,
            "transport_latency_ms_input": transport_latency_input,
            "core_cpu_input": core_cpu_input,
            "core_cpu_percent_input": core_cpu_input,
            "core_memory_input": core_memory_input,
            "ran_aware_final_risk": final_risk,
            "prb_risk_alpha": PRB_RISK_ALPHA,
            "predicted_decision_class": cls_str,
            "confidence_score": cls_conf,
            "threshold_decision": threshold_decision_str,
            "final_decision": final_label,
            "decision_divergence": divergence,
            "decision_mode": decision_mode,
            "thresholds_used": thresholds_used,
            "top_factors": top_factors,
            "dominant_domain": dom,
            "decision_explanation": decision_explanation_technical,
            "decision_explanation_plain": decision_explanation_plain,
            "final_decision_confidence": final_decision_confidence,
            "decision_source": decision_source,
            "policy_governed": POLICY_GOVERNED_MODE,
            "hard_prb_thresholds": {
                "reject": HARD_PRB_REJECT_THRESHOLD,
                "renegotiate": HARD_PRB_RENEGOTIATE_THRESHOLD,
            },
        }

        logger.info(
            "[DECISION] slice=%s mode=%s raw=%.3f adj=%.3f ran_risk=%.3f cls=%s thr=%s final=%s",
            slice_label,
            decision_mode,
            raw_risk_score,
            slice_adjusted,
            final_risk,
            cls_str,
            threshold_decision_str,
            final_label,
        )
        return (decision, reasoning, slos, domains, xai_bundle)
    
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

