#!/usr/bin/env python3
"""
Preditor de QoS - NWDAF
"""

import asyncio
import logging
import statistics
import math
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import uuid

from ..models.data_models import NetworkData, PredictionResult, QoSProfile
from apps.common.telemetry import trace_function, measure_time

class QoSPredictor:
    """Preditor de qualidade de serviço"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Perfis de QoS padrão
        self.qos_profiles = {
            "urllc": QoSProfile(
                profile_id="urllc",
                name="Ultra-Reliable Low-Latency Communications",
                latency_requirement=1.0,  # 1ms
                reliability_requirement=99.999,  # 99.999%
                throughput_requirement=1.0,  # 1 Mbps
                jitter_requirement=0.1,  # 0.1ms
                packet_loss_requirement=0.00001  # 0.001%
            ),
            "embb": QoSProfile(
                profile_id="embb",
                name="Enhanced Mobile Broadband",
                latency_requirement=10.0,  # 10ms
                reliability_requirement=99.9,  # 99.9%
                throughput_requirement=1000.0,  # 1000 Mbps
                jitter_requirement=1.0,  # 1ms
                packet_loss_requirement=0.001  # 0.1%
            ),
            "mmtc": QoSProfile(
                profile_id="mmtc",
                name="Massive Machine Type Communications",
                latency_requirement=100.0,  # 100ms
                reliability_requirement=99.0,  # 99%
                throughput_requirement=1.0,  # 1 Mbps
                jitter_requirement=10.0,  # 10ms
                packet_loss_requirement=0.01  # 1%
            )
        }
        
        # Histórico de predições
        self.prediction_history: List[PredictionResult] = []
        self.max_history_size = 1000
        
        # Modelos de predição (simulados)
        self.prediction_models = {
            "latency": self._predict_latency,
            "throughput": self._predict_throughput,
            "reliability": self._predict_reliability,
            "jitter": self._predict_jitter,
            "packet_loss": self._predict_packet_loss
        }
        
        # Status do preditor
        self.running = False
        self.initialized = False
    
    async def initialize(self):
        """Inicializar preditor"""
        try:
            self.logger.info("Inicializando QoS Predictor")
            self.initialized = True
            self.logger.info("QoS Predictor inicializado")
        except Exception as e:
            self.logger.error(f"Erro ao inicializar QoS Predictor: {str(e)}")
            raise
    
    async def stop(self):
        """Parar preditor"""
        try:
            self.running = False
            self.logger.info("QoS Predictor parado")
        except Exception as e:
            self.logger.error(f"Erro ao parar QoS Predictor: {str(e)}")
    
    @trace_function(operation_name="predict_qos")
    @measure_time
    async def predict_qos(self, network_data: NetworkData) -> Dict[str, Any]:
        """Predizer QoS baseado nos dados de rede"""
        try:
            self.logger.debug("Iniciando predição de QoS")
            
            # Predizer métricas para cada perfil de QoS
            predictions = {}
            
            for profile_id, profile in self.qos_profiles.items():
                profile_predictions = await self._predict_qos_for_profile(network_data, profile)
                predictions[profile_id] = profile_predictions
            
            # Consolidar predições
            qos_prediction = {
                "analysis_type": "qos_prediction",
                "timestamp": datetime.now().isoformat(),
                "predictions": predictions,
                "overall_qos_score": 0.0,
                "recommendations": [],
                "alerts": []
            }
            
            # Calcular score geral de QoS
            qos_scores = []
            for profile_id, profile_preds in predictions.items():
                if "qos_score" in profile_preds:
                    qos_scores.append(profile_preds["qos_score"])
            
            if qos_scores:
                qos_prediction["overall_qos_score"] = statistics.mean(qos_scores)
            
            # Gerar recomendações
            qos_prediction["recommendations"] = await self._generate_qos_recommendations(predictions)
            
            # Gerar alertas
            qos_prediction["alerts"] = await self._generate_qos_alerts(predictions)
            
            self.logger.info(f"Predição de QoS concluída - Score: {qos_prediction['overall_qos_score']:.2f}")
            return qos_prediction
            
        except Exception as e:
            self.logger.error(f"Erro na predição de QoS: {str(e)}")
            raise
    
    async def _predict_qos_for_profile(self, network_data: NetworkData, profile: QoSProfile) -> Dict[str, Any]:
        """Predizer QoS para um perfil específico"""
        try:
            predictions = {
                "profile_id": profile.profile_id,
                "profile_name": profile.name,
                "predicted_metrics": {},
                "qos_score": 0.0,
                "compliance": True,
                "violations": []
            }
            
            # Predizer latência
            latency_pred = await self._predict_latency(network_data, profile)
            predictions["predicted_metrics"]["latency"] = latency_pred
            
            # Predizer throughput
            throughput_pred = await self._predict_throughput(network_data, profile)
            predictions["predicted_metrics"]["throughput"] = throughput_pred
            
            # Predizer confiabilidade
            reliability_pred = await self._predict_reliability(network_data, profile)
            predictions["predicted_metrics"]["reliability"] = reliability_pred
            
            # Predizer jitter
            jitter_pred = await self._predict_jitter(network_data, profile)
            predictions["predicted_metrics"]["jitter"] = jitter_pred
            
            # Predizer perda de pacotes
            packet_loss_pred = await self._predict_packet_loss(network_data, profile)
            predictions["predicted_metrics"]["packet_loss"] = packet_loss_pred
            
            # Calcular score de QoS
            qos_score = await self._calculate_qos_score(predictions["predicted_metrics"], profile)
            predictions["qos_score"] = qos_score
            
            # Verificar conformidade
            compliance, violations = await self._check_qos_compliance(predictions["predicted_metrics"], profile)
            predictions["compliance"] = compliance
            predictions["violations"] = violations
            
            # Criar resultado de predição
            prediction_result = PredictionResult(
                prediction_id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                prediction_type=f"qos_{profile.profile_id}",
                predicted_value=qos_score,
                confidence=0.85,  # Simulado
                metadata={
                    "profile_id": profile.profile_id,
                    "predicted_metrics": predictions["predicted_metrics"]
                }
            )
            
            # Armazenar no histórico
            self.prediction_history.append(prediction_result)
            if len(self.prediction_history) > self.max_history_size:
                self.prediction_history = self.prediction_history[-self.max_history_size:]
            
            return predictions
            
        except Exception as e:
            self.logger.error(f"Erro na predição de QoS para perfil {profile.profile_id}: {str(e)}")
            return {
                "profile_id": profile.profile_id,
                "profile_name": profile.name,
                "predicted_metrics": {},
                "qos_score": 0.0,
                "compliance": False,
                "violations": ["Erro na predição"]
            }
    
    async def _predict_latency(self, network_data: NetworkData, profile: QoSProfile) -> Dict[str, Any]:
        """Predizer latência"""
        try:
            # Simular predição de latência baseada nos dados de rede
            base_latency = 5.0  # Latência base em ms
            
            # Ajustar baseado na utilização de CPU
            if "core_data" in network_data.to_dict():
                core_data = network_data.core_data
                if "upf" in core_data and "cpu_usage" in core_data["upf"]:
                    cpu_usage = core_data["upf"]["cpu_usage"]
                    base_latency += (cpu_usage - 50) * 0.1
            
            # Ajustar baseado na utilização de RAN
            if "ran_data" in network_data.to_dict():
                ran_data = network_data.ran_data
                if "resource_utilization" in ran_data and "prb_utilization" in ran_data["resource_utilization"]:
                    prb_util = ran_data["resource_utilization"]["prb_utilization"]
                    base_latency += (prb_util - 50) * 0.05
            
            # Ajustar baseado na latência de transporte
            if "transport_data" in network_data.to_dict():
                transport_data = network_data.transport_data
                if "latency_metrics" in transport_data and "avg_latency" in transport_data["latency_metrics"]:
                    transport_latency = transport_data["latency_metrics"]["avg_latency"]
                    base_latency += transport_latency * 0.3
            
            # Ajustar baseado no tipo de perfil
            if profile.profile_id == "urllc":
                base_latency *= 0.8  # URLLC tem latência menor
            elif profile.profile_id == "mmtc":
                base_latency *= 1.2  # mMTC pode ter latência maior
            
            # Adicionar ruído aleatório
            import random
            noise = random.uniform(-0.5, 0.5)
            predicted_latency = max(0.1, base_latency + noise)
            
            return {
                "predicted_value": predicted_latency,
                "confidence": 0.85,
                "trend": "stable",
                "factors": ["cpu_usage", "prb_utilization", "transport_latency"]
            }
            
        except Exception as e:
            self.logger.error(f"Erro na predição de latência: {str(e)}")
            return {
                "predicted_value": profile.latency_requirement * 2,
                "confidence": 0.0,
                "trend": "unknown",
                "factors": []
            }
    
    async def _predict_throughput(self, network_data: NetworkData, profile: QoSProfile) -> Dict[str, Any]:
        """Predizer throughput"""
        try:
            # Simular predição de throughput baseada nos dados de rede
            base_throughput = 100.0  # Throughput base em Mbps
            
            # Ajustar baseado na utilização de largura de banda
            if "transport_data" in network_data.to_dict():
                transport_data = network_data.transport_data
                if "bandwidth_metrics" in transport_data and "utilization_percentage" in transport_data["bandwidth_metrics"]:
                    bandwidth_util = transport_data["bandwidth_metrics"]["utilization_percentage"]
                    base_throughput *= (100 - bandwidth_util) / 100
            
            # Ajustar baseado na utilização de RAN
            if "ran_data" in network_data.to_dict():
                ran_data = network_data.ran_data
                if "resource_utilization" in ran_data and "prb_utilization" in ran_data["resource_utilization"]:
                    prb_util = ran_data["resource_utilization"]["prb_utilization"]
                    base_throughput *= (100 - prb_util) / 100
            
            # Ajustar baseado no tipo de perfil
            if profile.profile_id == "urllc":
                base_throughput *= 0.1  # URLLC tem throughput menor
            elif profile.profile_id == "embb":
                base_throughput *= 10.0  # eMBB tem throughput maior
            elif profile.profile_id == "mmtc":
                base_throughput *= 0.01  # mMTC tem throughput muito menor
            
            # Adicionar ruído aleatório
            import random
            noise = random.uniform(0.8, 1.2)
            predicted_throughput = max(0.1, base_throughput * noise)
            
            return {
                "predicted_value": predicted_throughput,
                "confidence": 0.80,
                "trend": "stable",
                "factors": ["bandwidth_utilization", "prb_utilization", "profile_type"]
            }
            
        except Exception as e:
            self.logger.error(f"Erro na predição de throughput: {str(e)}")
            return {
                "predicted_value": profile.throughput_requirement * 0.5,
                "confidence": 0.0,
                "trend": "unknown",
                "factors": []
            }
    
    async def _predict_reliability(self, network_data: NetworkData, profile: QoSProfile) -> Dict[str, Any]:
        """Predizer confiabilidade"""
        try:
            # Simular predição de confiabilidade baseada nos dados de rede
            base_reliability = 99.5  # Confiabilidade base em %
            
            # Ajustar baseado na taxa de sucesso de handover
            if "ran_data" in network_data.to_dict():
                ran_data = network_data.ran_data
                if "handover_metrics" in ran_data and "handover_success_rate" in ran_data["handover_metrics"]:
                    handover_success = ran_data["handover_metrics"]["handover_success_rate"]
                    base_reliability = min(99.9, base_reliability * (handover_success / 100))
            
            # Ajustar baseado na taxa de sucesso de sessão
            if "core_data" in network_data.to_dict():
                core_data = network_data.core_data
                if "smf" in core_data and "session_establishment_success_rate" in core_data["smf"]:
                    session_success = core_data["smf"]["session_establishment_success_rate"]
                    base_reliability = min(99.9, base_reliability * (session_success / 100))
            
            # Ajustar baseado no tipo de perfil
            if profile.profile_id == "urllc":
                base_reliability = min(99.999, base_reliability + 0.3)  # URLLC tem maior confiabilidade
            elif profile.profile_id == "mmtc":
                base_reliability = max(95.0, base_reliability - 2.0)  # mMTC pode ter menor confiabilidade
            
            # Adicionar ruído aleatório
            import random
            noise = random.uniform(-0.1, 0.1)
            predicted_reliability = max(90.0, min(99.999, base_reliability + noise))
            
            return {
                "predicted_value": predicted_reliability,
                "confidence": 0.90,
                "trend": "stable",
                "factors": ["handover_success", "session_success", "profile_type"]
            }
            
        except Exception as e:
            self.logger.error(f"Erro na predição de confiabilidade: {str(e)}")
            return {
                "predicted_value": profile.reliability_requirement * 0.9,
                "confidence": 0.0,
                "trend": "unknown",
                "factors": []
            }
    
    async def _predict_jitter(self, network_data: NetworkData, profile: QoSProfile) -> Dict[str, Any]:
        """Predizer jitter"""
        try:
            # Simular predição de jitter baseada nos dados de rede
            base_jitter = 1.0  # Jitter base em ms
            
            # Ajustar baseado na variância de latência
            if "transport_data" in network_data.to_dict():
                transport_data = network_data.transport_data
                if "latency_metrics" in transport_data and "latency_variance" in transport_data["latency_metrics"]:
                    latency_variance = transport_data["latency_metrics"]["latency_variance"]
                    base_jitter += latency_variance * 0.5
            
            # Ajustar baseado na utilização de recursos
            if "ran_data" in network_data.to_dict():
                ran_data = network_data.ran_data
                if "resource_utilization" in ran_data and "cpu_usage" in ran_data["resource_utilization"]:
                    cpu_usage = ran_data["resource_utilization"]["cpu_usage"]
                    base_jitter += (cpu_usage - 50) * 0.02
            
            # Ajustar baseado no tipo de perfil
            if profile.profile_id == "urllc":
                base_jitter *= 0.1  # URLLC tem jitter menor
            elif profile.profile_id == "mmtc":
                base_jitter *= 2.0  # mMTC pode ter jitter maior
            
            # Adicionar ruído aleatório
            import random
            noise = random.uniform(-0.2, 0.2)
            predicted_jitter = max(0.01, base_jitter + noise)
            
            return {
                "predicted_value": predicted_jitter,
                "confidence": 0.75,
                "trend": "stable",
                "factors": ["latency_variance", "cpu_usage", "profile_type"]
            }
            
        except Exception as e:
            self.logger.error(f"Erro na predição de jitter: {str(e)}")
            return {
                "predicted_value": profile.jitter_requirement * 2,
                "confidence": 0.0,
                "trend": "unknown",
                "factors": []
            }
    
    async def _predict_packet_loss(self, network_data: NetworkData, profile: QoSProfile) -> Dict[str, Any]:
        """Predizer perda de pacotes"""
        try:
            # Simular predição de perda de pacotes baseada nos dados de rede
            base_packet_loss = 0.001  # Perda base em %
            
            # Ajustar baseado na perda de pacotes de transporte
            if "transport_data" in network_data.to_dict():
                transport_data = network_data.transport_data
                if "packet_metrics" in transport_data and "packet_loss_rate" in transport_data["packet_metrics"]:
                    transport_loss = transport_data["packet_metrics"]["packet_loss_rate"]
                    base_packet_loss = max(base_packet_loss, transport_loss)
            
            # Ajustar baseado na qualidade do sinal
            if "ran_data" in network_data.to_dict():
                ran_data = network_data.ran_data
                if "radio_metrics" in ran_data and "sinr_avg" in ran_data["radio_metrics"]:
                    sinr = ran_data["radio_metrics"]["sinr_avg"]
                    if sinr < 10:  # SINR baixo
                        base_packet_loss *= 10
                    elif sinr < 15:
                        base_packet_loss *= 2
            
            # Ajustar baseado no tipo de perfil
            if profile.profile_id == "urllc":
                base_packet_loss *= 0.1  # URLLC tem menor perda
            elif profile.profile_id == "mmtc":
                base_packet_loss *= 5.0  # mMTC pode ter maior perda
            
            # Adicionar ruído aleatório
            import random
            noise = random.uniform(0.5, 1.5)
            predicted_packet_loss = max(0.0001, base_packet_loss * noise)
            
            return {
                "predicted_value": predicted_packet_loss,
                "confidence": 0.70,
                "trend": "stable",
                "factors": ["transport_loss", "sinr", "profile_type"]
            }
            
        except Exception as e:
            self.logger.error(f"Erro na predição de perda de pacotes: {str(e)}")
            return {
                "predicted_value": profile.packet_loss_requirement * 10,
                "confidence": 0.0,
                "trend": "unknown",
                "factors": []
            }
    
    async def _calculate_qos_score(self, predicted_metrics: Dict[str, Any], profile: QoSProfile) -> float:
        """Calcular score de QoS baseado nas métricas preditas"""
        try:
            scores = []
            
            # Score de latência
            if "latency" in predicted_metrics:
                latency_pred = predicted_metrics["latency"]["predicted_value"]
                latency_score = max(0, 100 - (latency_pred / profile.latency_requirement) * 100)
                scores.append(latency_score)
            
            # Score de throughput
            if "throughput" in predicted_metrics:
                throughput_pred = predicted_metrics["throughput"]["predicted_value"]
                throughput_score = min(100, (throughput_pred / profile.throughput_requirement) * 100)
                scores.append(throughput_score)
            
            # Score de confiabilidade
            if "reliability" in predicted_metrics:
                reliability_pred = predicted_metrics["reliability"]["predicted_value"]
                reliability_score = min(100, (reliability_pred / profile.reliability_requirement) * 100)
                scores.append(reliability_score)
            
            # Score de jitter
            if "jitter" in predicted_metrics:
                jitter_pred = predicted_metrics["jitter"]["predicted_value"]
                jitter_score = max(0, 100 - (jitter_pred / profile.jitter_requirement) * 100)
                scores.append(jitter_score)
            
            # Score de perda de pacotes
            if "packet_loss" in predicted_metrics:
                packet_loss_pred = predicted_metrics["packet_loss"]["predicted_value"]
                packet_loss_score = max(0, 100 - (packet_loss_pred / profile.packet_loss_requirement) * 100)
                scores.append(packet_loss_score)
            
            # Calcular score médio
            if scores:
                return statistics.mean(scores)
            else:
                return 0.0
                
        except Exception as e:
            self.logger.error(f"Erro no cálculo do score de QoS: {str(e)}")
            return 0.0
    
    async def _check_qos_compliance(self, predicted_metrics: Dict[str, Any], profile: QoSProfile) -> Tuple[bool, List[str]]:
        """Verificar conformidade com os requisitos de QoS"""
        try:
            compliance = True
            violations = []
            
            # Verificar latência
            if "latency" in predicted_metrics:
                latency_pred = predicted_metrics["latency"]["predicted_value"]
                if latency_pred > profile.latency_requirement:
                    compliance = False
                    violations.append(f"Latência predita ({latency_pred:.2f}ms) excede requisito ({profile.latency_requirement}ms)")
            
            # Verificar throughput
            if "throughput" in predicted_metrics:
                throughput_pred = predicted_metrics["throughput"]["predicted_value"]
                if throughput_pred < profile.throughput_requirement:
                    compliance = False
                    violations.append(f"Throughput predito ({throughput_pred:.2f}Mbps) abaixo do requisito ({profile.throughput_requirement}Mbps)")
            
            # Verificar confiabilidade
            if "reliability" in predicted_metrics:
                reliability_pred = predicted_metrics["reliability"]["predicted_value"]
                if reliability_pred < profile.reliability_requirement:
                    compliance = False
                    violations.append(f"Confiabilidade predita ({reliability_pred:.3f}%) abaixo do requisito ({profile.reliability_requirement}%)")
            
            # Verificar jitter
            if "jitter" in predicted_metrics:
                jitter_pred = predicted_metrics["jitter"]["predicted_value"]
                if jitter_pred > profile.jitter_requirement:
                    compliance = False
                    violations.append(f"Jitter predito ({jitter_pred:.2f}ms) excede requisito ({profile.jitter_requirement}ms)")
            
            # Verificar perda de pacotes
            if "packet_loss" in predicted_metrics:
                packet_loss_pred = predicted_metrics["packet_loss"]["predicted_value"]
                if packet_loss_pred > profile.packet_loss_requirement:
                    compliance = False
                    violations.append(f"Perda de pacotes predita ({packet_loss_pred:.6f}%) excede requisito ({profile.packet_loss_requirement:.6f}%)")
            
            return compliance, violations
            
        except Exception as e:
            self.logger.error(f"Erro na verificação de conformidade: {str(e)}")
            return False, ["Erro na verificação de conformidade"]
    
    async def _generate_qos_recommendations(self, predictions: Dict[str, Any]) -> List[str]:
        """Gerar recomendações baseadas nas predições de QoS"""
        try:
            recommendations = []
            
            for profile_id, profile_preds in predictions.items():
                if not profile_preds.get("compliance", True):
                    violations = profile_preds.get("violations", [])
                    if violations:
                        recommendations.append(f"Revisar configuração para {profile_id}: {', '.join(violations[:2])}")
                
                qos_score = profile_preds.get("qos_score", 0)
                if qos_score < 70:
                    recommendations.append(f"Otimizar QoS para {profile_id} (score: {qos_score:.1f})")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar recomendações de QoS: {str(e)}")
            return []
    
    async def _generate_qos_alerts(self, predictions: Dict[str, Any]) -> List[str]:
        """Gerar alertas baseados nas predições de QoS"""
        try:
            alerts = []
            
            for profile_id, profile_preds in predictions.items():
                qos_score = profile_preds.get("qos_score", 0)
                if qos_score < 50:
                    alerts.append(f"ALERTA CRÍTICO: QoS {profile_id} com score {qos_score:.1f}")
                elif qos_score < 70:
                    alerts.append(f"ALERTA: QoS {profile_id} com score {qos_score:.1f}")
                
                if not profile_preds.get("compliance", True):
                    alerts.append(f"VIOLAÇÃO: {profile_id} não atende requisitos de QoS")
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar alertas de QoS: {str(e)}")
            return []
    
    async def get_prediction_history(self) -> List[PredictionResult]:
        """Obter histórico de predições"""
        return self.prediction_history
    
    async def get_qos_profiles(self) -> Dict[str, QoSProfile]:
        """Obter perfis de QoS"""
        return self.qos_profiles
    
    async def add_qos_profile(self, profile: QoSProfile):
        """Adicionar novo perfil de QoS"""
        try:
            self.qos_profiles[profile.profile_id] = profile
            self.logger.info(f"Perfil de QoS {profile.profile_id} adicionado")
        except Exception as e:
            self.logger.error(f"Erro ao adicionar perfil de QoS: {str(e)}")
            raise
    
    async def remove_qos_profile(self, profile_id: str):
        """Remover perfil de QoS"""
        try:
            if profile_id in self.qos_profiles:
                del self.qos_profiles[profile_id]
                self.logger.info(f"Perfil de QoS {profile_id} removido")
            else:
                self.logger.warning(f"Perfil de QoS {profile_id} não encontrado")
        except Exception as e:
            self.logger.error(f"Erro ao remover perfil de QoS: {str(e)}")
            raise




