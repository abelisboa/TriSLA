#!/usr/bin/env python3
"""
TriSLA Adaptive Policies
Políticas adaptativas que se ajustam automaticamente baseadas no comportamento do sistema
"""

import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import statistics
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

# Configurar logging
logger = logging.getLogger(__name__)

@dataclass
class AdaptivePolicy:
    """Política adaptativa"""
    policy_id: str
    base_policy_id: str
    name: str
    adaptation_type: str  # "threshold", "parameters", "action"
    learning_rate: float
    adaptation_window: int  # número de observações
    min_confidence: float
    enabled: bool = True
    created_at: datetime = None
    last_adapted: datetime = None
    adaptation_count: int = 0
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_adapted is None:
            self.last_adapted = datetime.now()

@dataclass
class AdaptationResult:
    """Resultado da adaptação"""
    policy_id: str
    adapted_at: datetime
    adaptation_type: str
    old_value: Any
    new_value: Any
    confidence: float
    reason: str
    success: bool

class AdaptivePolicyManager:
    """Gerenciador de políticas adaptativas"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.adaptive_policies: Dict[str, AdaptivePolicy] = {}
        self.adaptation_history: List[AdaptationResult] = []
        self.learning_data: Dict[str, List[Dict[str, Any]]] = {}
        self.max_history_size = 1000
        self.max_learning_data = 10000
        
        # Modelos de ML para adaptação
        self.models: Dict[str, Any] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        
        # Carregar políticas adaptativas padrão
        self._load_default_adaptive_policies()
    
    def _load_default_adaptive_policies(self):
        """Carregar políticas adaptativas padrão"""
        try:
            # Política adaptativa para latência URLLC
            self._add_adaptive_policy(AdaptivePolicy(
                policy_id="adaptive_urllc_latency",
                base_policy_id="urllc_latency_critical",
                name="Adaptive URLLC Latency",
                adaptation_type="threshold",
                learning_rate=0.1,
                adaptation_window=50,
                min_confidence=0.8
            ))
            
            # Política adaptativa para throughput eMBB
            self._add_adaptive_policy(AdaptivePolicy(
                policy_id="adaptive_embb_throughput",
                base_policy_id="embb_bandwidth_high",
                name="Adaptive eMBB Throughput",
                adaptation_type="parameters",
                learning_rate=0.05,
                adaptation_window=100,
                min_confidence=0.75
            ))
            
            # Política adaptativa para conexões mMTC
            self._add_adaptive_policy(AdaptivePolicy(
                policy_id="adaptive_mmtc_connections",
                base_policy_id="mmtc_connections_high",
                name="Adaptive mMTC Connections",
                adaptation_type="threshold",
                learning_rate=0.15,
                adaptation_window=75,
                min_confidence=0.7
            ))
            
            self.logger.info(f"Políticas adaptativas padrão carregadas: {len(self.adaptive_policies)} políticas")
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar políticas adaptativas padrão: {str(e)}")
            raise
    
    def _add_adaptive_policy(self, policy: AdaptivePolicy):
        """Adicionar política adaptativa"""
        self.adaptive_policies[policy.policy_id] = policy
        self.learning_data[policy.policy_id] = []
        self.logger.debug(f"Política adaptativa adicionada: {policy.name}")
    
    def add_adaptive_policy(self, policy: AdaptivePolicy) -> bool:
        """Adicionar nova política adaptativa"""
        try:
            self._add_adaptive_policy(policy)
            self.logger.info(f"Política adaptativa adicionada: {policy.name}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao adicionar política adaptativa: {str(e)}")
            return False
    
    def add_learning_data(self, policy_id: str, data: Dict[str, Any]) -> bool:
        """Adicionar dados de aprendizado"""
        try:
            if policy_id not in self.learning_data:
                self.logger.warning(f"Política adaptativa não encontrada: {policy_id}")
                return False
            
            # Adicionar timestamp
            data["timestamp"] = datetime.now()
            
            # Adicionar aos dados de aprendizado
            self.learning_data[policy_id].append(data)
            
            # Limitar tamanho dos dados
            if len(self.learning_data[policy_id]) > self.max_learning_data:
                self.learning_data[policy_id] = self.learning_data[policy_id][-self.max_learning_data:]
            
            self.logger.debug(f"Dados de aprendizado adicionados para {policy_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao adicionar dados de aprendizado: {str(e)}")
            return False
    
    def should_adapt(self, policy_id: str) -> bool:
        """Verificar se política deve ser adaptada"""
        try:
            if policy_id not in self.adaptive_policies:
                return False
            
            policy = self.adaptive_policies[policy_id]
            if not policy.enabled:
                return False
            
            # Verificar se há dados suficientes
            data_count = len(self.learning_data[policy_id])
            if data_count < policy.adaptation_window:
                return False
            
            # Verificar se passou tempo suficiente desde última adaptação
            time_since_last = datetime.now() - policy.last_adapted
            if time_since_last.total_seconds() < 300:  # 5 minutos
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao verificar se deve adaptar: {str(e)}")
            return False
    
    def adapt_policy(self, policy_id: str, base_policy: Dict[str, Any]) -> Optional[AdaptationResult]:
        """Adaptar política baseada nos dados de aprendizado"""
        try:
            if not self.should_adapt(policy_id):
                return None
            
            policy = self.adaptive_policies[policy_id]
            learning_data = self.learning_data[policy_id]
            
            # Obter dados recentes
            recent_data = learning_data[-policy.adaptation_window:]
            
            # Adaptar baseado no tipo
            if policy.adaptation_type == "threshold":
                result = self._adapt_threshold(policy, recent_data, base_policy)
            elif policy.adaptation_type == "parameters":
                result = self._adapt_parameters(policy, recent_data, base_policy)
            elif policy.adaptation_type == "action":
                result = self._adapt_action(policy, recent_data, base_policy)
            else:
                self.logger.warning(f"Tipo de adaptação não suportado: {policy.adaptation_type}")
                return None
            
            if result and result.success:
                # Atualizar política
                policy.last_adapted = datetime.now()
                policy.adaptation_count += 1
                
                # Adicionar ao histórico
                self.adaptation_history.append(result)
                
                # Limitar histórico
                if len(self.adaptation_history) > self.max_history_size:
                    self.adaptation_history = self.adaptation_history[-self.max_history_size:]
                
                self.logger.info(f"Política {policy.name} adaptada com sucesso")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erro ao adaptar política {policy_id}: {str(e)}")
            return None
    
    def _adapt_threshold(self, policy: AdaptivePolicy, data: List[Dict[str, Any]], base_policy: Dict[str, Any]) -> Optional[AdaptationResult]:
        """Adaptar threshold da política"""
        try:
            # Extrair métricas relevantes
            metric_values = []
            violation_counts = []
            
            for entry in data:
                if "metric_value" in entry and "violated" in entry:
                    metric_values.append(entry["metric_value"])
                    violation_counts.append(1 if entry["violated"] else 0)
            
            if len(metric_values) < 10:  # Mínimo de dados
                return None
            
            # Calcular novo threshold baseado na distribuição
            current_threshold = base_policy.get("threshold", 0)
            
            # Usar percentil para ajustar threshold
            percentile = 95 if policy.learning_rate > 0.1 else 90
            new_threshold = np.percentile(metric_values, percentile)
            
            # Aplicar learning rate
            adapted_threshold = current_threshold + policy.learning_rate * (new_threshold - current_threshold)
            
            # Calcular confiança baseada na consistência dos dados
            confidence = self._calculate_adaptation_confidence(metric_values, violation_counts)
            
            if confidence < policy.min_confidence:
                return None
            
            return AdaptationResult(
                policy_id=policy.policy_id,
                adapted_at=datetime.now(),
                adaptation_type="threshold",
                old_value=current_threshold,
                new_value=adapted_threshold,
                confidence=confidence,
                reason=f"Threshold adaptado baseado em {len(data)} observações",
                success=True
            )
            
        except Exception as e:
            self.logger.error(f"Erro ao adaptar threshold: {str(e)}")
            return None
    
    def _adapt_parameters(self, policy: AdaptivePolicy, data: List[Dict[str, Any]], base_policy: Dict[str, Any]) -> Optional[AdaptationResult]:
        """Adaptar parâmetros da política"""
        try:
            # Extrair features e targets
            features = []
            targets = []
            
            for entry in data:
                if "context" in entry and "performance" in entry:
                    feature_vector = self._extract_features(entry["context"])
                    if feature_vector:
                        features.append(feature_vector)
                        targets.append(entry["performance"])
            
            if len(features) < 20:  # Mínimo de dados
                return None
            
            # Treinar modelo de regressão
            X = np.array(features)
            y = np.array(targets)
            
            # Normalizar features
            if policy.policy_id not in self.scalers:
                self.scalers[policy.policy_id] = StandardScaler()
            
            X_scaled = self.scalers[policy.policy_id].fit_transform(X)
            
            # Treinar modelo
            if policy.policy_id not in self.models:
                self.models[policy.policy_id] = LinearRegression()
            
            model = self.models[policy.policy_id]
            model.fit(X_scaled, y)
            
            # Calcular novos parâmetros baseados no modelo
            current_parameters = base_policy.get("parameters", {})
            new_parameters = self._calculate_new_parameters(current_parameters, model, policy.learning_rate)
            
            # Calcular confiança
            confidence = model.score(X_scaled, y)
            
            if confidence < policy.min_confidence:
                return None
            
            return AdaptationResult(
                policy_id=policy.policy_id,
                adapted_at=datetime.now(),
                adaptation_type="parameters",
                old_value=current_parameters,
                new_value=new_parameters,
                confidence=confidence,
                reason=f"Parâmetros adaptados usando modelo ML com {len(data)} observações",
                success=True
            )
            
        except Exception as e:
            self.logger.error(f"Erro ao adaptar parâmetros: {str(e)}")
            return None
    
    def _adapt_action(self, policy: AdaptivePolicy, data: List[Dict[str, Any]], base_policy: Dict[str, Any]) -> Optional[AdaptationResult]:
        """Adaptar ação da política"""
        try:
            # Analisar efetividade das ações
            action_effectiveness = {}
            
            for entry in data:
                if "action_taken" in entry and "outcome" in entry:
                    action = entry["action_taken"]
                    outcome = entry["outcome"]
                    
                    if action not in action_effectiveness:
                        action_effectiveness[action] = {"success": 0, "total": 0}
                    
                    action_effectiveness[action]["total"] += 1
                    if outcome == "success":
                        action_effectiveness[action]["success"] += 1
            
            # Calcular taxa de sucesso
            success_rates = {}
            for action, stats in action_effectiveness.items():
                if stats["total"] > 0:
                    success_rates[action] = stats["success"] / stats["total"]
            
            if not success_rates:
                return None
            
            # Encontrar melhor ação
            best_action = max(success_rates, key=success_rates.get)
            best_rate = success_rates[best_action]
            
            # Calcular confiança
            confidence = best_rate
            
            if confidence < policy.min_confidence:
                return None
            
            # Atualizar ação na política
            current_action = base_policy.get("action_type", "adjust")
            new_action = best_action
            
            return AdaptationResult(
                policy_id=policy.policy_id,
                adapted_at=datetime.now(),
                adaptation_type="action",
                old_value=current_action,
                new_value=new_action,
                confidence=confidence,
                reason=f"Ação adaptada para {best_action} com {best_rate:.2%} de sucesso",
                success=True
            )
            
        except Exception as e:
            self.logger.error(f"Erro ao adaptar ação: {str(e)}")
            return None
    
    def _extract_features(self, context: Dict[str, Any]) -> Optional[List[float]]:
        """Extrair features do contexto"""
        try:
            features = []
            
            # Features numéricas
            numeric_keys = ["cpu_usage", "memory_usage", "latency", "throughput", "connections"]
            for key in numeric_keys:
                if key in context:
                    features.append(float(context[key]))
                else:
                    features.append(0.0)
            
            # Features categóricas (one-hot encoding)
            categorical_keys = ["domain", "slice_type", "severity"]
            for key in categorical_keys:
                if key in context:
                    value = context[key]
                    if value == "RAN":
                        features.extend([1, 0, 0])
                    elif value == "Transport":
                        features.extend([0, 1, 0])
                    elif value == "Core":
                        features.extend([0, 0, 1])
                    else:
                        features.extend([0, 0, 0])
                else:
                    features.extend([0, 0, 0])
            
            return features
            
        except Exception as e:
            self.logger.error(f"Erro ao extrair features: {str(e)}")
            return None
    
    def _calculate_new_parameters(self, current_parameters: Dict[str, Any], model: Any, learning_rate: float) -> Dict[str, Any]:
        """Calcular novos parâmetros baseados no modelo"""
        try:
            new_parameters = current_parameters.copy()
            
            # Ajustar parâmetros baseados nos coeficientes do modelo
            coefficients = model.coef_
            
            # Ajustar scale_factor se existir
            if "scale_factor" in new_parameters:
                current_scale = new_parameters["scale_factor"]
                # Usar o primeiro coeficiente para ajustar scale_factor
                adjustment = coefficients[0] * learning_rate
                new_parameters["scale_factor"] = max(0.1, min(5.0, current_scale + adjustment))
            
            # Ajustar adjustment_factor se existir
            if "adjustment_factor" in new_parameters:
                current_adjustment = new_parameters["adjustment_factor"]
                # Usar o segundo coeficiente para ajustar adjustment_factor
                if len(coefficients) > 1:
                    adjustment = coefficients[1] * learning_rate
                    new_parameters["adjustment_factor"] = max(0.1, min(1.0, current_adjustment + adjustment))
            
            return new_parameters
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular novos parâmetros: {str(e)}")
            return current_parameters
    
    def _calculate_adaptation_confidence(self, metric_values: List[float], violation_counts: List[int]) -> float:
        """Calcular confiança da adaptação"""
        try:
            if len(metric_values) < 5:
                return 0.0
            
            # Confiança baseada na consistência dos dados
            std_dev = statistics.stdev(metric_values)
            mean_value = statistics.mean(metric_values)
            coefficient_of_variation = std_dev / mean_value if mean_value != 0 else 1.0
            
            # Confiança inversamente proporcional à variação
            consistency_confidence = max(0.0, 1.0 - coefficient_of_variation)
            
            # Confiança baseada na taxa de violações
            violation_rate = sum(violation_counts) / len(violation_counts)
            violation_confidence = 1.0 - violation_rate
            
            # Confiança combinada
            combined_confidence = (consistency_confidence + violation_confidence) / 2.0
            
            return max(0.0, min(1.0, combined_confidence))
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular confiança: {str(e)}")
            return 0.5
    
    def get_adaptation_statistics(self) -> Dict[str, Any]:
        """Obter estatísticas das adaptações"""
        try:
            total_adaptations = len(self.adaptation_history)
            successful_adaptations = len([r for r in self.adaptation_history if r.success])
            
            # Contar por tipo de adaptação
            adaptation_types = {}
            for result in self.adaptation_history:
                adaptation_type = result.adaptation_type
                adaptation_types[adaptation_type] = adaptation_types.get(adaptation_type, 0) + 1
            
            # Calcular confiança média
            confidences = [r.confidence for r in self.adaptation_history if r.success]
            avg_confidence = statistics.mean(confidences) if confidences else 0.0
            
            # Contar adaptações por política
            policy_adaptations = {}
            for result in self.adaptation_history:
                policy_id = result.policy_id
                policy_adaptations[policy_id] = policy_adaptations.get(policy_id, 0) + 1
            
            return {
                "total_adaptations": total_adaptations,
                "successful_adaptations": successful_adaptations,
                "success_rate": successful_adaptations / total_adaptations if total_adaptations > 0 else 0.0,
                "adaptation_types": adaptation_types,
                "average_confidence": avg_confidence,
                "policy_adaptations": policy_adaptations,
                "active_adaptive_policies": len([p for p in self.adaptive_policies.values() if p.enabled])
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao obter estatísticas: {str(e)}")
            return {}

# Função para criar gerenciador de políticas adaptativas
def create_adaptive_policy_manager() -> AdaptivePolicyManager:
    """Criar gerenciador de políticas adaptativas"""
    return AdaptivePolicyManager()
