#!/usr/bin/env python3
"""
Detector de Anomalias - NWDAF
"""

import asyncio
import logging
import statistics
import math
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import uuid

from ..models.data_models import NetworkData, AnomalyDetection, PerformanceMetrics
from apps.common.telemetry import trace_function, measure_time

class AnomalyDetector:
    """Detector de anomalias em dados de rede"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Tipos de anomalias
        self.anomaly_types = {
            "performance_degradation": {
                "name": "Performance Degradation",
                "severity": "high",
                "thresholds": {"cpu_usage": 90, "memory_usage": 90, "latency": 100}
            },
            "traffic_spike": {
                "name": "Traffic Spike",
                "severity": "medium",
                "thresholds": {"throughput_factor": 3.0, "duration_min": 30}
            },
            "connection_failure": {
                "name": "Connection Failure",
                "severity": "high",
                "thresholds": {"failure_rate": 0.1, "duration_min": 60}
            },
            "resource_exhaustion": {
                "name": "Resource Exhaustion",
                "severity": "critical",
                "thresholds": {"cpu_usage": 95, "memory_usage": 95, "prb_utilization": 95}
            },
            "latency_anomaly": {
                "name": "Latency Anomaly",
                "severity": "medium",
                "thresholds": {"latency_factor": 2.0, "duration_min": 60}
            },
            "packet_loss_anomaly": {
                "name": "Packet Loss Anomaly",
                "severity": "high",
                "thresholds": {"packet_loss_rate": 0.01, "duration_min": 30}
            }
        }
        
        # Histórico de anomalias detectadas
        self.anomaly_history: List[AnomalyDetection] = []
        self.max_history_size = 1000
        
        # Dados históricos para detecção
        self.historical_data: List[Dict[str, Any]] = []
        self.history_size = 100
        
        # Status do detector
        self.running = False
        self.initialized = False
    
    async def initialize(self):
        """Inicializar detector"""
        try:
            self.logger.info("Inicializando Anomaly Detector")
            self.initialized = True
            self.logger.info("Anomaly Detector inicializado")
        except Exception as e:
            self.logger.error(f"Erro ao inicializar Anomaly Detector: {str(e)}")
            raise
    
    async def stop(self):
        """Parar detector"""
        try:
            self.running = False
            self.logger.info("Anomaly Detector parado")
        except Exception as e:
            self.logger.error(f"Erro ao parar Anomaly Detector: {str(e)}")
    
    @trace_function(operation_name="detect_anomalies")
    @measure_time
    async def detect_anomalies(self, network_data: NetworkData) -> Dict[str, Any]:
        """Detectar anomalias nos dados de rede"""
        try:
            self.logger.debug("Iniciando detecção de anomalias")
            
            # Extrair dados para análise
            analysis_data = await self._extract_analysis_data(network_data)
            
            # Adicionar ao histórico
            self.historical_data.append(analysis_data)
            if len(self.historical_data) > self.history_size:
                self.historical_data = self.historical_data[-self.history_size:]
            
            # Detectar diferentes tipos de anomalias
            anomalies = []
            
            # Detectar degradação de performance
            perf_anomalies = await self._detect_performance_degradation(analysis_data)
            anomalies.extend(perf_anomalies)
            
            # Detectar picos de tráfego
            traffic_anomalies = await self._detect_traffic_spikes(analysis_data)
            anomalies.extend(traffic_anomalies)
            
            # Detectar falhas de conexão
            connection_anomalies = await self._detect_connection_failures(analysis_data)
            anomalies.extend(connection_anomalies)
            
            # Detectar esgotamento de recursos
            resource_anomalies = await self._detect_resource_exhaustion(analysis_data)
            anomalies.extend(resource_anomalies)
            
            # Detectar anomalias de latência
            latency_anomalies = await self._detect_latency_anomalies(analysis_data)
            anomalies.extend(latency_anomalies)
            
            # Detectar anomalias de perda de pacotes
            packet_loss_anomalies = await self._detect_packet_loss_anomalies(analysis_data)
            anomalies.extend(packet_loss_anomalies)
            
            # Consolidar detecção
            anomaly_detection = {
                "analysis_type": "anomaly_detection",
                "timestamp": datetime.now().isoformat(),
                "anomalies": anomalies,
                "total_anomalies": len(anomalies),
                "critical_anomalies": len([a for a in anomalies if a.get("severity") == "critical"]),
                "high_anomalies": len([a for a in anomalies if a.get("severity") == "high"]),
                "medium_anomalies": len([a for a in anomalies if a.get("severity") == "medium"]),
                "low_anomalies": len([a for a in anomalies if a.get("severity") == "low"]),
                "recommendations": [],
                "alerts": []
            }
            
            # Gerar recomendações
            anomaly_detection["recommendations"] = await self._generate_anomaly_recommendations(anomalies)
            
            # Gerar alertas
            anomaly_detection["alerts"] = await self._generate_anomaly_alerts(anomalies)
            
            self.logger.info(f"Detecção de anomalias concluída - Total: {len(anomalies)}")
            return anomaly_detection
            
        except Exception as e:
            self.logger.error(f"Erro na detecção de anomalias: {str(e)}")
            raise
    
    async def _extract_analysis_data(self, network_data: NetworkData) -> Dict[str, Any]:
        """Extrair dados para análise de anomalias"""
        try:
            analysis_data = {
                "timestamp": datetime.now().isoformat(),
                "nwdaf_id": network_data.nwdaf_id,
                "metrics": {},
                "components": {}
            }
            
            # Extrair métricas do 5G Core
            if "core_data" in network_data.to_dict():
                core_data = network_data.core_data
                for component, data in core_data.items():
                    analysis_data["components"][component] = {
                        "cpu_usage": data.get("cpu_usage", 0),
                        "memory_usage": data.get("memory_usage", 0),
                        "success_rate": data.get("success_rate", 0)
                    }
            
            # Extrair métricas de RAN
            if "ran_data" in network_data.to_dict():
                ran_data = network_data.ran_data
                analysis_data["metrics"]["ran"] = {
                    "throughput_ul": ran_data.get("traffic_metrics", {}).get("ul_throughput", 0),
                    "throughput_dl": ran_data.get("traffic_metrics", {}).get("dl_throughput", 0),
                    "latency_ul": ran_data.get("traffic_metrics", {}).get("ul_latency", 0),
                    "latency_dl": ran_data.get("traffic_metrics", {}).get("dl_latency", 0),
                    "prb_utilization": ran_data.get("resource_utilization", {}).get("prb_utilization", 0),
                    "handover_success_rate": ran_data.get("handover_metrics", {}).get("handover_success_rate", 0)
                }
            
            # Extrair métricas de transporte
            if "transport_data" in network_data.to_dict():
                transport_data = network_data.transport_data
                analysis_data["metrics"]["transport"] = {
                    "bandwidth_utilization": transport_data.get("bandwidth_metrics", {}).get("utilization_percentage", 0),
                    "latency_avg": transport_data.get("latency_metrics", {}).get("avg_latency", 0),
                    "packet_loss_rate": transport_data.get("packet_metrics", {}).get("packet_loss_rate", 0),
                    "qos_compliance_rate": transport_data.get("qos_metrics", {}).get("qos_compliance_rate", 0)
                }
            
            # Extrair métricas de aplicação
            if "app_data" in network_data.to_dict():
                app_data = network_data.app_data
                analysis_data["metrics"]["application"] = {
                    "ue_connection_rate": app_data.get("user_equipment", {}).get("ue_connection_rate", 0),
                    "http_success_rate": app_data.get("application_metrics", {}).get("http_success_rate", 0),
                    "api_success_rate": app_data.get("application_metrics", {}).get("api_success_rate", 0),
                    "service_success_rate": app_data.get("service_metrics", {}).get("service_success_rate", 0)
                }
            
            return analysis_data
            
        except Exception as e:
            self.logger.error(f"Erro ao extrair dados de análise: {str(e)}")
            return {}
    
    async def _detect_performance_degradation(self, analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detectar degradação de performance"""
        try:
            anomalies = []
            
            # Verificar componentes do 5G Core
            if "components" in analysis_data:
                for component, data in analysis_data["components"].items():
                    # Verificar CPU
                    cpu_usage = data.get("cpu_usage", 0)
                    if cpu_usage > self.anomaly_types["performance_degradation"]["thresholds"]["cpu_usage"]:
                        anomaly = AnomalyDetection(
                            anomaly_id=str(uuid.uuid4()),
                            timestamp=datetime.now(),
                            anomaly_type="performance_degradation",
                            severity="high",
                            affected_components=[component],
                            description=f"Alta utilização de CPU em {component}: {cpu_usage:.1f}%",
                            confidence=min(1.0, cpu_usage / 100),
                            nwdaf_id=analysis_data.get("nwdaf_id", "nwdaf-001"),
                            metadata={"metric": "cpu_usage", "value": cpu_usage, "threshold": 90}
                        )
                        anomalies.append(anomaly.to_dict())
                        self.anomaly_history.append(anomaly)
                    
                    # Verificar memória
                    memory_usage = data.get("memory_usage", 0)
                    if memory_usage > self.anomaly_types["performance_degradation"]["thresholds"]["memory_usage"]:
                        anomaly = AnomalyDetection(
                            anomaly_id=str(uuid.uuid4()),
                            timestamp=datetime.now(),
                            anomaly_type="performance_degradation",
                            severity="high",
                            affected_components=[component],
                            description=f"Alta utilização de memória em {component}: {memory_usage:.1f}%",
                            confidence=min(1.0, memory_usage / 100),
                            nwdaf_id=analysis_data.get("nwdaf_id", "nwdaf-001"),
                            metadata={"metric": "memory_usage", "value": memory_usage, "threshold": 90}
                        )
                        anomalies.append(anomaly.to_dict())
                        self.anomaly_history.append(anomaly)
            
            # Verificar latência
            if "ran" in analysis_data.get("metrics", {}):
                ran_metrics = analysis_data["metrics"]["ran"]
                latency_ul = ran_metrics.get("latency_ul", 0)
                latency_dl = ran_metrics.get("latency_dl", 0)
                avg_latency = (latency_ul + latency_dl) / 2
                
                if avg_latency > self.anomaly_types["performance_degradation"]["thresholds"]["latency"]:
                    anomaly = AnomalyDetection(
                        anomaly_id=str(uuid.uuid4()),
                        timestamp=datetime.now(),
                        anomaly_type="performance_degradation",
                        severity="high",
                        affected_components=["RAN"],
                        description=f"Latência elevada no RAN: {avg_latency:.1f}ms",
                        confidence=min(1.0, avg_latency / 200),
                        nwdaf_id=analysis_data.get("nwdaf_id", "nwdaf-001"),
                        metadata={"metric": "latency", "value": avg_latency, "threshold": 100}
                    )
                    anomalies.append(anomaly.to_dict())
                    self.anomaly_history.append(anomaly)
            
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Erro na detecção de degradação de performance: {str(e)}")
            return []
    
    async def _detect_traffic_spikes(self, analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detectar picos de tráfego"""
        try:
            anomalies = []
            
            if len(self.historical_data) < 5:
                return anomalies
            
            # Verificar throughput
            if "ran" in analysis_data.get("metrics", {}):
                ran_metrics = analysis_data["metrics"]["ran"]
                current_throughput = ran_metrics.get("throughput_ul", 0) + ran_metrics.get("throughput_dl", 0)
                
                # Calcular throughput histórico
                historical_throughputs = []
                for data in self.historical_data[-10:]:  # Últimos 10 pontos
                    if "ran" in data.get("metrics", {}):
                        ran_data = data["metrics"]["ran"]
                        hist_throughput = ran_data.get("throughput_ul", 0) + ran_data.get("throughput_dl", 0)
                        historical_throughputs.append(hist_throughput)
                
                if historical_throughputs:
                    avg_throughput = statistics.mean(historical_throughputs)
                    std_throughput = statistics.stdev(historical_throughputs) if len(historical_throughputs) > 1 else 0
                    
                    # Verificar se é um pico
                    if avg_throughput > 0:
                        throughput_factor = current_throughput / avg_throughput
                        if throughput_factor > self.anomaly_types["traffic_spike"]["thresholds"]["throughput_factor"]:
                            anomaly = AnomalyDetection(
                                anomaly_id=str(uuid.uuid4()),
                                timestamp=datetime.now(),
                                anomaly_type="traffic_spike",
                                severity="medium",
                                affected_components=["RAN"],
                                description=f"Pico de tráfego detectado: {current_throughput:.1f}Mbps (fator: {throughput_factor:.2f})",
                                confidence=min(1.0, throughput_factor / 5.0),
                                nwdaf_id=analysis_data.get("nwdaf_id", "nwdaf-001"),
                                metadata={"metric": "throughput", "value": current_throughput, "factor": throughput_factor}
                            )
                            anomalies.append(anomaly.to_dict())
                            self.anomaly_history.append(anomaly)
            
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Erro na detecção de picos de tráfego: {str(e)}")
            return []
    
    async def _detect_connection_failures(self, analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detectar falhas de conexão"""
        try:
            anomalies = []
            
            # Verificar taxa de sucesso de handover
            if "ran" in analysis_data.get("metrics", {}):
                ran_metrics = analysis_data["metrics"]["ran"]
                handover_success_rate = ran_metrics.get("handover_success_rate", 0)
                
                if handover_success_rate < (1 - self.anomaly_types["connection_failure"]["thresholds"]["failure_rate"]) * 100:
                    anomaly = AnomalyDetection(
                        anomaly_id=str(uuid.uuid4()),
                        timestamp=datetime.now(),
                        anomaly_type="connection_failure",
                        severity="high",
                        affected_components=["RAN"],
                        description=f"Taxa de sucesso de handover baixa: {handover_success_rate:.1f}%",
                        confidence=min(1.0, (100 - handover_success_rate) / 100),
                        nwdaf_id=analysis_data.get("nwdaf_id", "nwdaf-001"),
                        metadata={"metric": "handover_success_rate", "value": handover_success_rate, "threshold": 90}
                    )
                    anomalies.append(anomaly.to_dict())
                    self.anomaly_history.append(anomaly)
            
            # Verificar taxa de sucesso de aplicação
            if "application" in analysis_data.get("metrics", {}):
                app_metrics = analysis_data["metrics"]["application"]
                ue_connection_rate = app_metrics.get("ue_connection_rate", 0)
                
                if ue_connection_rate < (1 - self.anomaly_types["connection_failure"]["thresholds"]["failure_rate"]) * 100:
                    anomaly = AnomalyDetection(
                        anomaly_id=str(uuid.uuid4()),
                        timestamp=datetime.now(),
                        anomaly_type="connection_failure",
                        severity="high",
                        affected_components=["Application"],
                        description=f"Taxa de conexão de UEs baixa: {ue_connection_rate:.1f}%",
                        confidence=min(1.0, (100 - ue_connection_rate) / 100),
                        nwdaf_id=analysis_data.get("nwdaf_id", "nwdaf-001"),
                        metadata={"metric": "ue_connection_rate", "value": ue_connection_rate, "threshold": 90}
                    )
                    anomalies.append(anomaly.to_dict())
                    self.anomaly_history.append(anomaly)
            
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Erro na detecção de falhas de conexão: {str(e)}")
            return []
    
    async def _detect_resource_exhaustion(self, analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detectar esgotamento de recursos"""
        try:
            anomalies = []
            
            # Verificar componentes do 5G Core
            if "components" in analysis_data:
                for component, data in analysis_data["components"].items():
                    cpu_usage = data.get("cpu_usage", 0)
                    memory_usage = data.get("memory_usage", 0)
                    
                    # Verificar esgotamento crítico
                    if cpu_usage > self.anomaly_types["resource_exhaustion"]["thresholds"]["cpu_usage"]:
                        anomaly = AnomalyDetection(
                            anomaly_id=str(uuid.uuid4()),
                            timestamp=datetime.now(),
                            anomaly_type="resource_exhaustion",
                            severity="critical",
                            affected_components=[component],
                            description=f"Esgotamento crítico de CPU em {component}: {cpu_usage:.1f}%",
                            confidence=min(1.0, cpu_usage / 100),
                            nwdaf_id=analysis_data.get("nwdaf_id", "nwdaf-001"),
                            metadata={"metric": "cpu_usage", "value": cpu_usage, "threshold": 95}
                        )
                        anomalies.append(anomaly.to_dict())
                        self.anomaly_history.append(anomaly)
                    
                    if memory_usage > self.anomaly_types["resource_exhaustion"]["thresholds"]["memory_usage"]:
                        anomaly = AnomalyDetection(
                            anomaly_id=str(uuid.uuid4()),
                            timestamp=datetime.now(),
                            anomaly_type="resource_exhaustion",
                            severity="critical",
                            affected_components=[component],
                            description=f"Esgotamento crítico de memória em {component}: {memory_usage:.1f}%",
                            confidence=min(1.0, memory_usage / 100),
                            nwdaf_id=analysis_data.get("nwdaf_id", "nwdaf-001"),
                            metadata={"metric": "memory_usage", "value": memory_usage, "threshold": 95}
                        )
                        anomalies.append(anomaly.to_dict())
                        self.anomaly_history.append(anomaly)
            
            # Verificar utilização de PRB
            if "ran" in analysis_data.get("metrics", {}):
                ran_metrics = analysis_data["metrics"]["ran"]
                prb_utilization = ran_metrics.get("prb_utilization", 0)
                
                if prb_utilization > self.anomaly_types["resource_exhaustion"]["thresholds"]["prb_utilization"]:
                    anomaly = AnomalyDetection(
                        anomaly_id=str(uuid.uuid4()),
                        timestamp=datetime.now(),
                        anomaly_type="resource_exhaustion",
                        severity="critical",
                        affected_components=["RAN"],
                        description=f"Esgotamento crítico de PRB no RAN: {prb_utilization:.1f}%",
                        confidence=min(1.0, prb_utilization / 100),
                        nwdaf_id=analysis_data.get("nwdaf_id", "nwdaf-001"),
                        metadata={"metric": "prb_utilization", "value": prb_utilization, "threshold": 95}
                    )
                    anomalies.append(anomaly.to_dict())
                    self.anomaly_history.append(anomaly)
            
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Erro na detecção de esgotamento de recursos: {str(e)}")
            return []
    
    async def _detect_latency_anomalies(self, analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detectar anomalias de latência"""
        try:
            anomalies = []
            
            if len(self.historical_data) < 5:
                return anomalies
            
            # Verificar latência do RAN
            if "ran" in analysis_data.get("metrics", {}):
                ran_metrics = analysis_data["metrics"]["ran"]
                current_latency = (ran_metrics.get("latency_ul", 0) + ran_metrics.get("latency_dl", 0)) / 2
                
                # Calcular latência histórica
                historical_latencies = []
                for data in self.historical_data[-10:]:
                    if "ran" in data.get("metrics", {}):
                        ran_data = data["metrics"]["ran"]
                        hist_latency = (ran_data.get("latency_ul", 0) + ran_data.get("latency_dl", 0)) / 2
                        historical_latencies.append(hist_latency)
                
                if historical_latencies:
                    avg_latency = statistics.mean(historical_latencies)
                    
                    if avg_latency > 0:
                        latency_factor = current_latency / avg_latency
                        if latency_factor > self.anomaly_types["latency_anomaly"]["thresholds"]["latency_factor"]:
                            anomaly = AnomalyDetection(
                                anomaly_id=str(uuid.uuid4()),
                                timestamp=datetime.now(),
                                anomaly_type="latency_anomaly",
                                severity="medium",
                                affected_components=["RAN"],
                                description=f"Anomalia de latência no RAN: {current_latency:.1f}ms (fator: {latency_factor:.2f})",
                                confidence=min(1.0, latency_factor / 3.0),
                                nwdaf_id=analysis_data.get("nwdaf_id", "nwdaf-001"),
                                metadata={"metric": "latency", "value": current_latency, "factor": latency_factor}
                            )
                            anomalies.append(anomaly.to_dict())
                            self.anomaly_history.append(anomaly)
            
            # Verificar latência de transporte
            if "transport" in analysis_data.get("metrics", {}):
                transport_metrics = analysis_data["metrics"]["transport"]
                current_latency = transport_metrics.get("latency_avg", 0)
                
                # Calcular latência histórica
                historical_latencies = []
                for data in self.historical_data[-10:]:
                    if "transport" in data.get("metrics", {}):
                        transport_data = data["metrics"]["transport"]
                        hist_latency = transport_data.get("latency_avg", 0)
                        historical_latencies.append(hist_latency)
                
                if historical_latencies:
                    avg_latency = statistics.mean(historical_latencies)
                    
                    if avg_latency > 0:
                        latency_factor = current_latency / avg_latency
                        if latency_factor > self.anomaly_types["latency_anomaly"]["thresholds"]["latency_factor"]:
                            anomaly = AnomalyDetection(
                                anomaly_id=str(uuid.uuid4()),
                                timestamp=datetime.now(),
                                anomaly_type="latency_anomaly",
                                severity="medium",
                                affected_components=["Transport"],
                                description=f"Anomalia de latência no transporte: {current_latency:.1f}ms (fator: {latency_factor:.2f})",
                                confidence=min(1.0, latency_factor / 3.0),
                                nwdaf_id=analysis_data.get("nwdaf_id", "nwdaf-001"),
                                metadata={"metric": "latency", "value": current_latency, "factor": latency_factor}
                            )
                            anomalies.append(anomaly.to_dict())
                            self.anomaly_history.append(anomaly)
            
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Erro na detecção de anomalias de latência: {str(e)}")
            return []
    
    async def _detect_packet_loss_anomalies(self, analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detectar anomalias de perda de pacotes"""
        try:
            anomalies = []
            
            # Verificar perda de pacotes de transporte
            if "transport" in analysis_data.get("metrics", {}):
                transport_metrics = analysis_data["metrics"]["transport"]
                packet_loss_rate = transport_metrics.get("packet_loss_rate", 0)
                
                if packet_loss_rate > self.anomaly_types["packet_loss_anomaly"]["thresholds"]["packet_loss_rate"]:
                    anomaly = AnomalyDetection(
                        anomaly_id=str(uuid.uuid4()),
                        timestamp=datetime.now(),
                        anomaly_type="packet_loss_anomaly",
                        severity="high",
                        affected_components=["Transport"],
                        description=f"Alta taxa de perda de pacotes: {packet_loss_rate:.4f}%",
                        confidence=min(1.0, packet_loss_rate / 0.1),
                        nwdaf_id=analysis_data.get("nwdaf_id", "nwdaf-001"),
                        metadata={"metric": "packet_loss_rate", "value": packet_loss_rate, "threshold": 0.01}
                    )
                    anomalies.append(anomaly.to_dict())
                    self.anomaly_history.append(anomaly)
            
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Erro na detecção de anomalias de perda de pacotes: {str(e)}")
            return []
    
    async def _generate_anomaly_recommendations(self, anomalies: List[Dict[str, Any]]) -> List[str]:
        """Gerar recomendações baseadas nas anomalias detectadas"""
        try:
            recommendations = []
            
            for anomaly in anomalies:
                anomaly_type = anomaly.get("anomaly_type", "")
                severity = anomaly.get("severity", "")
                
                if anomaly_type == "performance_degradation":
                    if severity == "high":
                        recommendations.append("Escalar recursos para componentes com alta utilização")
                        recommendations.append("Implementar balanceamento de carga")
                
                elif anomaly_type == "traffic_spike":
                    recommendations.append("Implementar escalonamento automático")
                    recommendations.append("Ativar políticas de QoS para picos de tráfego")
                
                elif anomaly_type == "connection_failure":
                    recommendations.append("Investigar falhas de conectividade")
                    recommendations.append("Revisar configurações de handover")
                
                elif anomaly_type == "resource_exhaustion":
                    if severity == "critical":
                        recommendations.append("AÇÃO IMEDIATA: Escalar recursos críticos")
                        recommendations.append("Implementar políticas de priorização")
                
                elif anomaly_type == "latency_anomaly":
                    recommendations.append("Otimizar roteamento de rede")
                    recommendations.append("Revisar configurações de QoS")
                
                elif anomaly_type == "packet_loss_anomaly":
                    recommendations.append("Investigar problemas de conectividade")
                    recommendations.append("Revisar configurações de buffer")
            
            return list(set(recommendations))  # Remover duplicatas
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar recomendações de anomalias: {str(e)}")
            return []
    
    async def _generate_anomaly_alerts(self, anomalies: List[Dict[str, Any]]) -> List[str]:
        """Gerar alertas baseados nas anomalias detectadas"""
        try:
            alerts = []
            
            for anomaly in anomalies:
                anomaly_type = anomaly.get("anomaly_type", "")
                severity = anomaly.get("severity", "")
                description = anomaly.get("description", "")
                confidence = anomaly.get("confidence", 0)
                
                if severity == "critical":
                    alerts.append(f"🚨 CRÍTICO: {description} (confiança: {confidence:.2f})")
                elif severity == "high":
                    alerts.append(f"⚠️ ALTO: {description} (confiança: {confidence:.2f})")
                elif severity == "medium":
                    alerts.append(f"⚡ MÉDIO: {description} (confiança: {confidence:.2f})")
                else:
                    alerts.append(f"ℹ️ BAIXO: {description} (confiança: {confidence:.2f})")
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar alertas de anomalias: {str(e)}")
            return []
    
    async def get_anomaly_history(self) -> List[AnomalyDetection]:
        """Obter histórico de anomalias"""
        return self.anomaly_history
    
    async def get_anomaly_statistics(self) -> Dict[str, Any]:
        """Obter estatísticas de anomalias"""
        try:
            if not self.anomaly_history:
                return {"status": "no_anomalies"}
            
            # Contar por tipo
            type_counts = {}
            severity_counts = {}
            
            for anomaly in self.anomaly_history:
                anomaly_type = anomaly.anomaly_type
                severity = anomaly.severity
                
                type_counts[anomaly_type] = type_counts.get(anomaly_type, 0) + 1
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            # Calcular confiança média
            confidences = [anomaly.confidence for anomaly in self.anomaly_history]
            avg_confidence = statistics.mean(confidences) if confidences else 0
            
            # Anomalias recentes (últimas 24 horas)
            recent_time = datetime.now() - timedelta(hours=24)
            recent_anomalies = [a for a in self.anomaly_history if a.timestamp > recent_time]
            
            return {
                "total_anomalies": len(self.anomaly_history),
                "recent_anomalies": len(recent_anomalies),
                "type_distribution": type_counts,
                "severity_distribution": severity_counts,
                "average_confidence": avg_confidence,
                "most_common_type": max(type_counts, key=type_counts.get) if type_counts else None,
                "most_common_severity": max(severity_counts, key=severity_counts.get) if severity_counts else None
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao obter estatísticas de anomalias: {str(e)}")
            return {"status": "error"}
    
    async def get_anomaly_trends(self) -> Dict[str, Any]:
        """Obter tendências de anomalias"""
        try:
            if len(self.anomaly_history) < 10:
                return {"status": "insufficient_data"}
            
            # Agrupar por hora
            hourly_counts = {}
            for anomaly in self.anomaly_history:
                hour_key = anomaly.timestamp.strftime("%Y-%m-%d %H:00")
                hourly_counts[hour_key] = hourly_counts.get(hour_key, 0) + 1
            
            # Calcular tendência
            counts = list(hourly_counts.values())
            if len(counts) > 1:
                # Regressão linear simples
                n = len(counts)
                x_values = list(range(n))
                sum_x = sum(x_values)
                sum_y = sum(counts)
                sum_xy = sum(x * y for x, y in zip(x_values, counts))
                sum_x2 = sum(x * x for x in x_values)
                
                denominator = n * sum_x2 - sum_x * sum_x
                if denominator != 0:
                    slope = (n * sum_xy - sum_x * sum_y) / denominator
                else:
                    slope = 0
                
                if abs(slope) < 0.1:
                    trend = "stable"
                elif slope > 0.1:
                    trend = "increasing"
                else:
                    trend = "decreasing"
            else:
                trend = "stable"
                slope = 0
            
            return {
                "trend": trend,
                "slope": slope,
                "hourly_counts": hourly_counts,
                "data_points": len(counts)
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao obter tendências de anomalias: {str(e)}")
            return {"status": "error"}




