#!/usr/bin/env python3
"""
TriSLA SLA Policies
Políticas SLA-aware para o Closed Loop Controller
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import json

# Configurar logging
logger = logging.getLogger(__name__)

class PolicyType(Enum):
    """Tipos de políticas SLA"""
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    AVAILABILITY = "availability"
    RELIABILITY = "reliability"
    BANDWIDTH = "bandwidth"
    CONNECTION_DENSITY = "connection_density"

class ViolationSeverity(Enum):
    """Severidade de violação"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ActionType(Enum):
    """Tipos de ações para violações"""
    WARN = "warn"
    ADJUST = "adjust"
    SCALE = "scale"
    FAILOVER = "failover"
    REJECT = "reject"

@dataclass
class SLAPolicy:
    """Política SLA individual"""
    policy_id: str
    name: str
    policy_type: PolicyType
    domain: str  # RAN, Transport, Core
    slice_type: str  # URLLC, eMBB, mMTC
    threshold: float
    operator: str  # "lt", "gt", "eq", "lte", "gte"
    severity: ViolationSeverity
    action_type: ActionType
    parameters: Dict[str, Any]
    enabled: bool = True
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

@dataclass
class PolicyEvaluation:
    """Resultado da avaliação de política"""
    policy_id: str
    evaluated_at: datetime
    metric_value: float
    threshold: float
    violated: bool
    severity: ViolationSeverity
    action_required: bool
    action_type: ActionType
    confidence: float
    context: Dict[str, Any]

class SLAPolicyManager:
    """Gerenciador de políticas SLA"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.policies: Dict[str, SLAPolicy] = {}
        self.evaluation_history: List[PolicyEvaluation] = []
        self.max_history_size = 1000
        
        # Carregar políticas padrão
        self._load_default_policies()
    
    def _load_default_policies(self):
        """Carregar políticas SLA padrão"""
        try:
            # Políticas URLLC
            self._add_policy(SLAPolicy(
                policy_id="urllc_latency_critical",
                name="URLLC Latency Critical",
                policy_type=PolicyType.LATENCY,
                domain="RAN",
                slice_type="URLLC",
                threshold=10.0,
                operator="lte",
                severity=ViolationSeverity.CRITICAL,
                action_type=ActionType.ADJUST,
                parameters={
                    "adjustment_factor": 0.8,
                    "max_adjustments": 3,
                    "cooldown_seconds": 30
                }
            ))
            
            self._add_policy(SLAPolicy(
                policy_id="urllc_reliability_critical",
                name="URLLC Reliability Critical",
                policy_type=PolicyType.RELIABILITY,
                domain="RAN",
                slice_type="URLLC",
                threshold=99.9,
                operator="gte",
                severity=ViolationSeverity.CRITICAL,
                action_type=ActionType.FAILOVER,
                parameters={
                    "backup_slices": 2,
                    "failover_timeout": 5.0
                }
            ))
            
            # Políticas eMBB
            self._add_policy(SLAPolicy(
                policy_id="embb_bandwidth_high",
                name="eMBB Bandwidth High",
                policy_type=PolicyType.BANDWIDTH,
                domain="Transport",
                slice_type="eMBB",
                threshold=1000.0,
                operator="gte",
                severity=ViolationSeverity.HIGH,
                action_type=ActionType.SCALE,
                parameters={
                    "scale_factor": 1.5,
                    "max_scale": 3.0,
                    "scale_timeout": 60.0
                }
            ))
            
            self._add_policy(SLAPolicy(
                policy_id="embb_latency_medium",
                name="eMBB Latency Medium",
                policy_type=PolicyType.LATENCY,
                domain="Transport",
                slice_type="eMBB",
                threshold=50.0,
                operator="lte",
                severity=ViolationSeverity.MEDIUM,
                action_type=ActionType.ADJUST,
                parameters={
                    "adjustment_factor": 0.9,
                    "max_adjustments": 5
                }
            ))
            
            # Políticas mMTC
            self._add_policy(SLAPolicy(
                policy_id="mmtc_connections_high",
                name="mMTC Connections High",
                policy_type=PolicyType.CONNECTION_DENSITY,
                domain="Core",
                slice_type="mMTC",
                threshold=10000.0,
                operator="gte",
                severity=ViolationSeverity.HIGH,
                action_type=ActionType.SCALE,
                parameters={
                    "scale_factor": 2.0,
                    "max_scale": 5.0,
                    "scale_timeout": 120.0
                }
            ))
            
            self._add_policy(SLAPolicy(
                policy_id="mmtc_latency_medium",
                name="mMTC Latency Medium",
                policy_type=PolicyType.LATENCY,
                domain="Core",
                slice_type="mMTC",
                threshold=100.0,
                operator="lte",
                severity=ViolationSeverity.MEDIUM,
                action_type=ActionType.ADJUST,
                parameters={
                    "adjustment_factor": 0.95,
                    "max_adjustments": 3
                }
            ))
            
            # Políticas de disponibilidade
            self._add_policy(SLAPolicy(
                policy_id="availability_critical",
                name="Availability Critical",
                policy_type=PolicyType.AVAILABILITY,
                domain="Core",
                slice_type="ALL",
                threshold=99.9,
                operator="gte",
                severity=ViolationSeverity.CRITICAL,
                action_type=ActionType.FAILOVER,
                parameters={
                    "backup_instances": 3,
                    "failover_timeout": 10.0
                }
            ))
            
            self.logger.info(f"Políticas padrão carregadas: {len(self.policies)} políticas")
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar políticas padrão: {str(e)}")
            raise
    
    def _add_policy(self, policy: SLAPolicy):
        """Adicionar política"""
        self.policies[policy.policy_id] = policy
        self.logger.debug(f"Política adicionada: {policy.name}")
    
    def add_policy(self, policy: SLAPolicy) -> bool:
        """Adicionar nova política"""
        try:
            policy.updated_at = datetime.now()
            self._add_policy(policy)
            self.logger.info(f"Política adicionada: {policy.name}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao adicionar política: {str(e)}")
            return False
    
    def update_policy(self, policy_id: str, updates: Dict[str, Any]) -> bool:
        """Atualizar política existente"""
        try:
            if policy_id not in self.policies:
                self.logger.warning(f"Política não encontrada: {policy_id}")
                return False
            
            policy = self.policies[policy_id]
            
            # Atualizar campos
            for key, value in updates.items():
                if hasattr(policy, key):
                    setattr(policy, key, value)
            
            policy.updated_at = datetime.now()
            
            self.logger.info(f"Política atualizada: {policy.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao atualizar política: {str(e)}")
            return False
    
    def remove_policy(self, policy_id: str) -> bool:
        """Remover política"""
        try:
            if policy_id not in self.policies:
                self.logger.warning(f"Política não encontrada: {policy_id}")
                return False
            
            policy = self.policies[policy_id]
            del self.policies[policy_id]
            
            self.logger.info(f"Política removida: {policy.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao remover política: {str(e)}")
            return False
    
    def get_policy(self, policy_id: str) -> Optional[SLAPolicy]:
        """Obter política por ID"""
        return self.policies.get(policy_id)
    
    def get_policies_by_domain(self, domain: str) -> List[SLAPolicy]:
        """Obter políticas por domínio"""
        return [policy for policy in self.policies.values() if policy.domain == domain]
    
    def get_policies_by_slice_type(self, slice_type: str) -> List[SLAPolicy]:
        """Obter políticas por tipo de slice"""
        return [policy for policy in self.policies.values() if policy.slice_type == slice_type]
    
    def get_enabled_policies(self) -> List[SLAPolicy]:
        """Obter políticas habilitadas"""
        return [policy for policy in self.policies.values() if policy.enabled]
    
    def evaluate_metrics(self, metrics: Dict[str, Any]) -> List[PolicyEvaluation]:
        """Avaliar métricas contra políticas"""
        try:
            evaluations = []
            
            for policy in self.get_enabled_policies():
                evaluation = self._evaluate_policy(policy, metrics)
                if evaluation:
                    evaluations.append(evaluation)
            
            # Adicionar ao histórico
            self.evaluation_history.extend(evaluations)
            
            # Limitar tamanho do histórico
            if len(self.evaluation_history) > self.max_history_size:
                self.evaluation_history = self.evaluation_history[-self.max_history_size:]
            
            self.logger.debug(f"Avaliações realizadas: {len(evaluations)}")
            return evaluations
            
        except Exception as e:
            self.logger.error(f"Erro ao avaliar métricas: {str(e)}")
            return []
    
    def _evaluate_policy(self, policy: SLAPolicy, metrics: Dict[str, Any]) -> Optional[PolicyEvaluation]:
        """Avaliar política específica contra métricas"""
        try:
            # Obter valor da métrica
            metric_value = self._get_metric_value(policy, metrics)
            if metric_value is None:
                return None
            
            # Avaliar violação
            violated = self._evaluate_violation(metric_value, policy)
            
            # Determinar severidade
            severity = self._determine_severity(metric_value, policy)
            
            # Determinar se ação é necessária
            action_required = violated and severity in [ViolationSeverity.HIGH, ViolationSeverity.CRITICAL]
            
            # Calcular confiança
            confidence = self._calculate_confidence(metric_value, policy)
            
            # Criar avaliação
            evaluation = PolicyEvaluation(
                policy_id=policy.policy_id,
                evaluated_at=datetime.now(),
                metric_value=metric_value,
                threshold=policy.threshold,
                violated=violated,
                severity=severity,
                action_required=action_required,
                action_type=policy.action_type,
                confidence=confidence,
                context={
                    "domain": policy.domain,
                    "slice_type": policy.slice_type,
                    "policy_name": policy.name
                }
            )
            
            return evaluation
            
        except Exception as e:
            self.logger.error(f"Erro ao avaliar política {policy.policy_id}: {str(e)}")
            return None
    
    def _get_metric_value(self, policy: SLAPolicy, metrics: Dict[str, Any]) -> Optional[float]:
        """Obter valor da métrica para política"""
        try:
            # Mapear tipo de política para chave de métrica
            metric_keys = {
                PolicyType.LATENCY: ["latency", "response_time", "processing_time"],
                PolicyType.THROUGHPUT: ["throughput", "requests_per_second", "tps"],
                PolicyType.AVAILABILITY: ["availability", "uptime", "service_availability"],
                PolicyType.RELIABILITY: ["reliability", "success_rate", "error_rate"],
                PolicyType.BANDWIDTH: ["bandwidth", "data_rate", "transfer_rate"],
                PolicyType.CONNECTION_DENSITY: ["connections", "active_connections", "connection_count"]
            }
            
            keys = metric_keys.get(policy.policy_type, [])
            
            # Procurar valor da métrica
            for key in keys:
                if key in metrics:
                    value = metrics[key]
                    if isinstance(value, (int, float)):
                        return float(value)
            
            # Procurar em sub-dicionários
            for key in keys:
                for domain_key, domain_metrics in metrics.items():
                    if isinstance(domain_metrics, dict) and key in domain_metrics:
                        value = domain_metrics[key]
                        if isinstance(value, (int, float)):
                            return float(value)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Erro ao obter valor da métrica: {str(e)}")
            return None
    
    def _evaluate_violation(self, metric_value: float, policy: SLAPolicy) -> bool:
        """Avaliar se há violação"""
        try:
            operator = policy.operator
            threshold = policy.threshold
            
            if operator == "lt":
                return metric_value < threshold
            elif operator == "gt":
                return metric_value > threshold
            elif operator == "eq":
                return abs(metric_value - threshold) < 0.001
            elif operator == "lte":
                return metric_value <= threshold
            elif operator == "gte":
                return metric_value >= threshold
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"Erro ao avaliar violação: {str(e)}")
            return False
    
    def _determine_severity(self, metric_value: float, policy: SLAPolicy) -> ViolationSeverity:
        """Determinar severidade da violação"""
        try:
            if not self._evaluate_violation(metric_value, policy):
                return ViolationSeverity.LOW
            
            # Calcular desvio percentual
            deviation = abs(metric_value - policy.threshold) / policy.threshold
            
            if deviation >= 0.5:  # 50% ou mais
                return ViolationSeverity.CRITICAL
            elif deviation >= 0.2:  # 20% ou mais
                return ViolationSeverity.HIGH
            elif deviation >= 0.1:  # 10% ou mais
                return ViolationSeverity.MEDIUM
            else:
                return ViolationSeverity.LOW
                
        except Exception as e:
            self.logger.error(f"Erro ao determinar severidade: {str(e)}")
            return ViolationSeverity.LOW
    
    def _calculate_confidence(self, metric_value: float, policy: SLAPolicy) -> float:
        """Calcular confiança da avaliação"""
        try:
            # Baseado na proximidade do valor ao threshold
            if policy.threshold == 0:
                return 1.0
            
            deviation = abs(metric_value - policy.threshold) / policy.threshold
            confidence = max(0.0, min(1.0, 1.0 - deviation))
            
            return confidence
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular confiança: {str(e)}")
            return 0.5
    
    def get_violations(self, severity: Optional[ViolationSeverity] = None) -> List[PolicyEvaluation]:
        """Obter violações do histórico"""
        try:
            violations = [eval for eval in self.evaluation_history if eval.violated]
            
            if severity:
                violations = [eval for eval in violations if eval.severity == severity]
            
            return violations
            
        except Exception as e:
            self.logger.error(f"Erro ao obter violações: {str(e)}")
            return []
    
    def get_recent_violations(self, hours: int = 24) -> List[PolicyEvaluation]:
        """Obter violações recentes"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_violations = [
                eval for eval in self.evaluation_history
                if eval.violated and eval.evaluated_at >= cutoff_time
            ]
            
            return recent_violations
            
        except Exception as e:
            self.logger.error(f"Erro ao obter violações recentes: {str(e)}")
            return []
    
    def get_policy_statistics(self) -> Dict[str, Any]:
        """Obter estatísticas das políticas"""
        try:
            total_policies = len(self.policies)
            enabled_policies = len(self.get_enabled_policies())
            
            # Contar por domínio
            domain_counts = {}
            for policy in self.policies.values():
                domain_counts[policy.domain] = domain_counts.get(policy.domain, 0) + 1
            
            # Contar por tipo de slice
            slice_type_counts = {}
            for policy in self.policies.values():
                slice_type_counts[policy.slice_type] = slice_type_counts.get(policy.slice_type, 0) + 1
            
            # Contar violações recentes
            recent_violations = self.get_recent_violations(24)
            violation_counts = {}
            for violation in recent_violations:
                severity = violation.severity.value
                violation_counts[severity] = violation_counts.get(severity, 0) + 1
            
            return {
                "total_policies": total_policies,
                "enabled_policies": enabled_policies,
                "disabled_policies": total_policies - enabled_policies,
                "domain_counts": domain_counts,
                "slice_type_counts": slice_type_counts,
                "recent_violations_24h": len(recent_violations),
                "violation_counts_by_severity": violation_counts,
                "evaluation_history_size": len(self.evaluation_history)
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao obter estatísticas: {str(e)}")
            return {}

# Função para criar gerenciador de políticas
def create_sla_policy_manager() -> SLAPolicyManager:
    """Criar gerenciador de políticas SLA"""
    return SLAPolicyManager()
