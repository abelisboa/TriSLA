#!/usr/bin/env python3
"""
Analisador de Performance de Rede - NWDAF
"""

import asyncio
import logging
import statistics
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import uuid

from ..models.data_models import NetworkData, PerformanceMetrics, NetworkHealth
from apps.common.telemetry import trace_function, measure_time

class NetworkAnalyzer:
    """Analisador de performance de rede"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.thresholds = {
            "cpu_usage": 80.0,
            "memory_usage": 85.0,
            "latency": 50.0,
            "packet_loss": 0.01,
            "throughput": 0.8,  # 80% da capacidade
            "availability": 99.0
        }
        
        # Histórico de métricas
        self.metrics_history: List[PerformanceMetrics] = []
        self.max_history_size = 1000
        
        # Status do analisador
        self.running = False
        self.initialized = False
    
    async def initialize(self):
        """Inicializar analisador"""
        try:
            self.logger.info("Inicializando Network Analyzer")
            self.initialized = True
            self.logger.info("Network Analyzer inicializado")
        except Exception as e:
            self.logger.error(f"Erro ao inicializar Network Analyzer: {str(e)}")
            raise
    
    async def stop(self):
        """Parar analisador"""
        try:
            self.running = False
            self.logger.info("Network Analyzer parado")
        except Exception as e:
            self.logger.error(f"Erro ao parar Network Analyzer: {str(e)}")
    
    @trace_function(operation_name="analyze_performance")
    @measure_time
    async def analyze_performance(self, network_data: NetworkData) -> Dict[str, Any]:
        """Analisar performance de rede"""
        try:
            self.logger.debug("Iniciando análise de performance de rede")
            
            # Analisar componentes do 5G Core
            core_analysis = await self._analyze_core_performance(network_data.core_data)
            
            # Analisar RAN
            ran_analysis = await self._analyze_ran_performance(network_data.ran_data)
            
            # Analisar transporte
            transport_analysis = await self._analyze_transport_performance(network_data.transport_data)
            
            # Analisar aplicações
            app_analysis = await self._analyze_app_performance(network_data.app_data)
            
            # Consolidar análise
            performance_analysis = {
                "analysis_type": "network_performance",
                "timestamp": datetime.now().isoformat(),
                "overall_score": 0.0,
                "components": {
                    "core": core_analysis,
                    "ran": ran_analysis,
                    "transport": transport_analysis,
                    "application": app_analysis
                },
                "health_status": "healthy",
                "issues": [],
                "recommendations": []
            }
            
            # Calcular score geral
            scores = []
            if core_analysis.get("score"):
                scores.append(core_analysis["score"])
            if ran_analysis.get("score"):
                scores.append(ran_analysis["score"])
            if transport_analysis.get("score"):
                scores.append(transport_analysis["score"])
            if app_analysis.get("score"):
                scores.append(app_analysis["score"])
            
            if scores:
                performance_analysis["overall_score"] = statistics.mean(scores)
            
            # Determinar status de saúde
            if performance_analysis["overall_score"] >= 90:
                performance_analysis["health_status"] = "healthy"
            elif performance_analysis["overall_score"] >= 70:
                performance_analysis["health_status"] = "warning"
            else:
                performance_analysis["health_status"] = "critical"
            
            # Gerar recomendações
            performance_analysis["recommendations"] = await self._generate_recommendations(performance_analysis)
            
            # Criar métricas de performance
            metrics = PerformanceMetrics(
                metrics_id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                component="network",
                metrics={
                    "overall_score": performance_analysis["overall_score"],
                    "core_score": core_analysis.get("score", 0),
                    "ran_score": ran_analysis.get("score", 0),
                    "transport_score": transport_analysis.get("score", 0),
                    "app_score": app_analysis.get("score", 0)
                },
                thresholds=self.thresholds,
                violations=performance_analysis["issues"],
                nwdaf_id=network_data.nwdaf_id
            )
            
            # Armazenar no histórico
            self.metrics_history.append(metrics)
            if len(self.metrics_history) > self.max_history_size:
                self.metrics_history = self.metrics_history[-self.max_history_size:]
            
            self.logger.info(f"Análise de performance concluída - Score: {performance_analysis['overall_score']:.2f}")
            return performance_analysis
            
        except Exception as e:
            self.logger.error(f"Erro na análise de performance: {str(e)}")
            raise
    
    async def _analyze_core_performance(self, core_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analisar performance do 5G Core"""
        try:
            analysis = {
                "component": "5g_core",
                "score": 0.0,
                "metrics": {},
                "issues": [],
                "recommendations": []
            }
            
            scores = []
            
            # Analisar AMF
            if "amf" in core_data:
                amf_score = await self._analyze_component_performance(core_data["amf"], "AMF")
                scores.append(amf_score)
                analysis["metrics"]["amf_score"] = amf_score
            
            # Analisar SMF
            if "smf" in core_data:
                smf_score = await self._analyze_component_performance(core_data["smf"], "SMF")
                scores.append(smf_score)
                analysis["metrics"]["smf_score"] = smf_score
            
            # Analisar UPF
            if "upf" in core_data:
                upf_score = await self._analyze_component_performance(core_data["upf"], "UPF")
                scores.append(upf_score)
                analysis["metrics"]["upf_score"] = upf_score
            
            # Analisar PCF
            if "pcf" in core_data:
                pcf_score = await self._analyze_component_performance(core_data["pcf"], "PCF")
                scores.append(pcf_score)
                analysis["metrics"]["pcf_score"] = pcf_score
            
            # Analisar UDM
            if "udm" in core_data:
                udm_score = await self._analyze_component_performance(core_data["udm"], "UDM")
                scores.append(udm_score)
                analysis["metrics"]["udm_score"] = udm_score
            
            # Analisar AUSF
            if "ausf" in core_data:
                ausf_score = await self._analyze_component_performance(core_data["ausf"], "AUSF")
                scores.append(ausf_score)
                analysis["metrics"]["ausf_score"] = ausf_score
            
            # Analisar NRF
            if "nrf" in core_data:
                nrf_score = await self._analyze_component_performance(core_data["nrf"], "NRF")
                scores.append(nrf_score)
                analysis["metrics"]["nrf_score"] = nrf_score
            
            # Analisar NSSF
            if "nssf" in core_data:
                nssf_score = await self._analyze_component_performance(core_data["nssf"], "NSSF")
                scores.append(nssf_score)
                analysis["metrics"]["nssf_score"] = nssf_score
            
            # Calcular score geral
            if scores:
                analysis["score"] = statistics.mean(scores)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Erro na análise do 5G Core: {str(e)}")
            return {"component": "5g_core", "score": 0.0, "metrics": {}, "issues": [], "recommendations": []}
    
    async def _analyze_ran_performance(self, ran_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analisar performance do RAN"""
        try:
            analysis = {
                "component": "ran",
                "score": 0.0,
                "metrics": {},
                "issues": [],
                "recommendations": []
            }
            
            scores = []
            
            # Analisar células
            if "cells" in ran_data:
                cell_score = await self._analyze_cell_performance(ran_data["cells"])
                scores.append(cell_score)
                analysis["metrics"]["cell_score"] = cell_score
            
            # Analisar métricas de rádio
            if "radio_metrics" in ran_data:
                radio_score = await self._analyze_radio_performance(ran_data["radio_metrics"])
                scores.append(radio_score)
                analysis["metrics"]["radio_score"] = radio_score
            
            # Analisar métricas de tráfego
            if "traffic_metrics" in ran_data:
                traffic_score = await self._analyze_traffic_performance(ran_data["traffic_metrics"])
                scores.append(traffic_score)
                analysis["metrics"]["traffic_score"] = traffic_score
            
            # Analisar handover
            if "handover_metrics" in ran_data:
                handover_score = await self._analyze_handover_performance(ran_data["handover_metrics"])
                scores.append(handover_score)
                analysis["metrics"]["handover_score"] = handover_score
            
            # Analisar utilização de recursos
            if "resource_utilization" in ran_data:
                resource_score = await self._analyze_resource_performance(ran_data["resource_utilization"])
                scores.append(resource_score)
                analysis["metrics"]["resource_score"] = resource_score
            
            # Calcular score geral
            if scores:
                analysis["score"] = statistics.mean(scores)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Erro na análise do RAN: {str(e)}")
            return {"component": "ran", "score": 0.0, "metrics": {}, "issues": [], "recommendations": []}
    
    async def _analyze_transport_performance(self, transport_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analisar performance de transporte"""
        try:
            analysis = {
                "component": "transport",
                "score": 0.0,
                "metrics": {},
                "issues": [],
                "recommendations": []
            }
            
            scores = []
            
            # Analisar links de rede
            if "network_links" in transport_data:
                link_score = await self._analyze_link_performance(transport_data["network_links"])
                scores.append(link_score)
                analysis["metrics"]["link_score"] = link_score
            
            # Analisar largura de banda
            if "bandwidth_metrics" in transport_data:
                bandwidth_score = await self._analyze_bandwidth_performance(transport_data["bandwidth_metrics"])
                scores.append(bandwidth_score)
                analysis["metrics"]["bandwidth_score"] = bandwidth_score
            
            # Analisar latência
            if "latency_metrics" in transport_data:
                latency_score = await self._analyze_latency_performance(transport_data["latency_metrics"])
                scores.append(latency_score)
                analysis["metrics"]["latency_score"] = latency_score
            
            # Analisar pacotes
            if "packet_metrics" in transport_data:
                packet_score = await self._analyze_packet_performance(transport_data["packet_metrics"])
                scores.append(packet_score)
                analysis["metrics"]["packet_score"] = packet_score
            
            # Analisar QoS
            if "qos_metrics" in transport_data:
                qos_score = await self._analyze_qos_performance(transport_data["qos_metrics"])
                scores.append(qos_score)
                analysis["metrics"]["qos_score"] = qos_score
            
            # Calcular score geral
            if scores:
                analysis["score"] = statistics.mean(scores)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Erro na análise de transporte: {str(e)}")
            return {"component": "transport", "score": 0.0, "metrics": {}, "issues": [], "recommendations": []}
    
    async def _analyze_app_performance(self, app_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analisar performance de aplicação"""
        try:
            analysis = {
                "component": "application",
                "score": 0.0,
                "metrics": {},
                "issues": [],
                "recommendations": []
            }
            
            scores = []
            
            # Analisar slices
            if "slice_instances" in app_data:
                slice_score = await self._analyze_slice_performance(app_data["slice_instances"])
                scores.append(slice_score)
                analysis["metrics"]["slice_score"] = slice_score
            
            # Analisar UEs
            if "user_equipment" in app_data:
                ue_score = await self._analyze_ue_performance(app_data["user_equipment"])
                scores.append(ue_score)
                analysis["metrics"]["ue_score"] = ue_score
            
            # Analisar métricas de aplicação
            if "application_metrics" in app_data:
                app_metrics_score = await self._analyze_app_metrics_performance(app_data["application_metrics"])
                scores.append(app_metrics_score)
                analysis["metrics"]["app_metrics_score"] = app_metrics_score
            
            # Analisar métricas de serviço
            if "service_metrics" in app_data:
                service_score = await self._analyze_service_performance(app_data["service_metrics"])
                scores.append(service_score)
                analysis["metrics"]["service_score"] = service_score
            
            # Calcular score geral
            if scores:
                analysis["score"] = statistics.mean(scores)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Erro na análise de aplicação: {str(e)}")
            return {"component": "application", "score": 0.0, "metrics": {}, "issues": [], "recommendations": []}
    
    async def _analyze_component_performance(self, component_data: Dict[str, Any], component_name: str) -> float:
        """Analisar performance de um componente específico"""
        try:
            score = 100.0
            
            # Verificar CPU
            if "cpu_usage" in component_data:
                cpu_usage = component_data["cpu_usage"]
                if cpu_usage > self.thresholds["cpu_usage"]:
                    score -= (cpu_usage - self.thresholds["cpu_usage"]) * 2
            
            # Verificar memória
            if "memory_usage" in component_data:
                memory_usage = component_data["memory_usage"]
                if memory_usage > self.thresholds["memory_usage"]:
                    score -= (memory_usage - self.thresholds["memory_usage"]) * 2
            
            # Verificar latência
            if "latency" in component_data:
                latency = component_data["latency"]
                if latency > self.thresholds["latency"]:
                    score -= (latency - self.thresholds["latency"]) * 0.5
            
            # Verificar taxa de sucesso
            if "success_rate" in component_data:
                success_rate = component_data["success_rate"]
                if success_rate < self.thresholds["availability"]:
                    score -= (self.thresholds["availability"] - success_rate) * 2
            
            return max(0.0, min(100.0, score))
            
        except Exception as e:
            self.logger.error(f"Erro na análise do componente {component_name}: {str(e)}")
            return 0.0
    
    async def _analyze_cell_performance(self, cell_data: Dict[str, Any]) -> float:
        """Analisar performance de células"""
        try:
            score = 100.0
            
            # Verificar disponibilidade de células
            if "cell_availability" in cell_data:
                availability = cell_data["cell_availability"]
                if availability < self.thresholds["availability"]:
                    score -= (self.thresholds["availability"] - availability) * 2
            
            return max(0.0, min(100.0, score))
            
        except Exception as e:
            self.logger.error(f"Erro na análise de células: {str(e)}")
            return 0.0
    
    async def _analyze_radio_performance(self, radio_data: Dict[str, Any]) -> float:
        """Analisar performance de rádio"""
        try:
            score = 100.0
            
            # Verificar RSRP
            if "rsrp_avg" in radio_data:
                rsrp = radio_data["rsrp_avg"]
                if rsrp < -100:  # RSRP muito baixo
                    score -= 20
                elif rsrp < -90:
                    score -= 10
            
            # Verificar RSRQ
            if "rsrq_avg" in radio_data:
                rsrq = radio_data["rsrq_avg"]
                if rsrq < -15:  # RSRQ muito baixo
                    score -= 20
                elif rsrq < -12:
                    score -= 10
            
            # Verificar SINR
            if "sinr_avg" in radio_data:
                sinr = radio_data["sinr_avg"]
                if sinr < 10:  # SINR muito baixo
                    score -= 20
                elif sinr < 15:
                    score -= 10
            
            return max(0.0, min(100.0, score))
            
        except Exception as e:
            self.logger.error(f"Erro na análise de rádio: {str(e)}")
            return 0.0
    
    async def _analyze_traffic_performance(self, traffic_data: Dict[str, Any]) -> float:
        """Analisar performance de tráfego"""
        try:
            score = 100.0
            
            # Verificar throughput
            if "ul_throughput" in traffic_data and "dl_throughput" in traffic_data:
                total_throughput = traffic_data["ul_throughput"] + traffic_data["dl_throughput"]
                if total_throughput < 100:  # Throughput muito baixo
                    score -= 20
                elif total_throughput < 500:
                    score -= 10
            
            # Verificar latência
            if "ul_latency" in traffic_data:
                ul_latency = traffic_data["ul_latency"]
                if ul_latency > self.thresholds["latency"]:
                    score -= (ul_latency - self.thresholds["latency"]) * 0.5
            
            if "dl_latency" in traffic_data:
                dl_latency = traffic_data["dl_latency"]
                if dl_latency > self.thresholds["latency"]:
                    score -= (dl_latency - self.thresholds["latency"]) * 0.5
            
            return max(0.0, min(100.0, score))
            
        except Exception as e:
            self.logger.error(f"Erro na análise de tráfego: {str(e)}")
            return 0.0
    
    async def _analyze_handover_performance(self, handover_data: Dict[str, Any]) -> float:
        """Analisar performance de handover"""
        try:
            score = 100.0
            
            # Verificar taxa de sucesso de handover
            if "handover_success_rate" in handover_data:
                success_rate = handover_data["handover_success_rate"]
                if success_rate < 95:  # Taxa de sucesso muito baixa
                    score -= 30
                elif success_rate < 98:
                    score -= 15
            
            # Verificar tempo de handover
            if "avg_handover_time" in handover_data:
                handover_time = handover_data["avg_handover_time"]
                if handover_time > 5:  # Tempo muito alto
                    score -= 20
                elif handover_time > 3:
                    score -= 10
            
            return max(0.0, min(100.0, score))
            
        except Exception as e:
            self.logger.error(f"Erro na análise de handover: {str(e)}")
            return 0.0
    
    async def _analyze_resource_performance(self, resource_data: Dict[str, Any]) -> float:
        """Analisar performance de recursos"""
        try:
            score = 100.0
            
            # Verificar utilização de PRB
            if "prb_utilization" in resource_data:
                prb_util = resource_data["prb_utilization"]
                if prb_util > 90:  # Utilização muito alta
                    score -= 20
                elif prb_util > 80:
                    score -= 10
            
            # Verificar CPU
            if "cpu_usage" in resource_data:
                cpu_usage = resource_data["cpu_usage"]
                if cpu_usage > self.thresholds["cpu_usage"]:
                    score -= (cpu_usage - self.thresholds["cpu_usage"]) * 2
            
            # Verificar memória
            if "memory_usage" in resource_data:
                memory_usage = resource_data["memory_usage"]
                if memory_usage > self.thresholds["memory_usage"]:
                    score -= (memory_usage - self.thresholds["memory_usage"]) * 2
            
            return max(0.0, min(100.0, score))
            
        except Exception as e:
            self.logger.error(f"Erro na análise de recursos: {str(e)}")
            return 0.0
    
    async def _analyze_link_performance(self, link_data: Dict[str, Any]) -> float:
        """Analisar performance de links"""
        try:
            score = 100.0
            
            # Verificar disponibilidade de links
            if "link_availability" in link_data:
                availability = link_data["link_availability"]
                if availability < self.thresholds["availability"]:
                    score -= (self.thresholds["availability"] - availability) * 2
            
            return max(0.0, min(100.0, score))
            
        except Exception as e:
            self.logger.error(f"Erro na análise de links: {str(e)}")
            return 0.0
    
    async def _analyze_bandwidth_performance(self, bandwidth_data: Dict[str, Any]) -> float:
        """Analisar performance de largura de banda"""
        try:
            score = 100.0
            
            # Verificar utilização de largura de banda
            if "utilization_percentage" in bandwidth_data:
                utilization = bandwidth_data["utilization_percentage"]
                if utilization > 90:  # Utilização muito alta
                    score -= 20
                elif utilization > 80:
                    score -= 10
            
            return max(0.0, min(100.0, score))
            
        except Exception as e:
            self.logger.error(f"Erro na análise de largura de banda: {str(e)}")
            return 0.0
    
    async def _analyze_latency_performance(self, latency_data: Dict[str, Any]) -> float:
        """Analisar performance de latência"""
        try:
            score = 100.0
            
            # Verificar latência média
            if "avg_latency" in latency_data:
                avg_latency = latency_data["avg_latency"]
                if avg_latency > self.thresholds["latency"]:
                    score -= (avg_latency - self.thresholds["latency"]) * 0.5
            
            # Verificar latência máxima
            if "max_latency" in latency_data:
                max_latency = latency_data["max_latency"]
                if max_latency > self.thresholds["latency"] * 2:
                    score -= 30
                elif max_latency > self.thresholds["latency"] * 1.5:
                    score -= 15
            
            return max(0.0, min(100.0, score))
            
        except Exception as e:
            self.logger.error(f"Erro na análise de latência: {str(e)}")
            return 0.0
    
    async def _analyze_packet_performance(self, packet_data: Dict[str, Any]) -> float:
        """Analisar performance de pacotes"""
        try:
            score = 100.0
            
            # Verificar taxa de perda de pacotes
            if "packet_loss_rate" in packet_data:
                loss_rate = packet_data["packet_loss_rate"]
                if loss_rate > self.thresholds["packet_loss"]:
                    score -= (loss_rate - self.thresholds["packet_loss"]) * 1000
            
            # Verificar taxa de erro de pacotes
            if "packet_error_rate" in packet_data:
                error_rate = packet_data["packet_error_rate"]
                if error_rate > self.thresholds["packet_loss"]:
                    score -= (error_rate - self.thresholds["packet_loss"]) * 1000
            
            return max(0.0, min(100.0, score))
            
        except Exception as e:
            self.logger.error(f"Erro na análise de pacotes: {str(e)}")
            return 0.0
    
    async def _analyze_qos_performance(self, qos_data: Dict[str, Any]) -> float:
        """Analisar performance de QoS"""
        try:
            score = 100.0
            
            # Verificar taxa de conformidade de QoS
            if "qos_compliance_rate" in qos_data:
                compliance_rate = qos_data["qos_compliance_rate"]
                if compliance_rate < 95:  # Taxa de conformidade muito baixa
                    score -= 30
                elif compliance_rate < 98:
                    score -= 15
            
            return max(0.0, min(100.0, score))
            
        except Exception as e:
            self.logger.error(f"Erro na análise de QoS: {str(e)}")
            return 0.0
    
    async def _analyze_slice_performance(self, slice_data: Dict[str, Any]) -> float:
        """Analisar performance de slices"""
        try:
            score = 100.0
            
            # Verificar total de slices
            if "total_slices" in slice_data:
                total_slices = slice_data["total_slices"]
                if total_slices == 0:
                    score -= 50  # Nenhum slice ativo
                elif total_slices < 5:
                    score -= 20  # Poucos slices ativos
            
            return max(0.0, min(100.0, score))
            
        except Exception as e:
            self.logger.error(f"Erro na análise de slices: {str(e)}")
            return 0.0
    
    async def _analyze_ue_performance(self, ue_data: Dict[str, Any]) -> float:
        """Analisar performance de UEs"""
        try:
            score = 100.0
            
            # Verificar taxa de conexão de UEs
            if "ue_connection_rate" in ue_data:
                connection_rate = ue_data["ue_connection_rate"]
                if connection_rate < 80:  # Taxa de conexão muito baixa
                    score -= 30
                elif connection_rate < 90:
                    score -= 15
            
            return max(0.0, min(100.0, score))
            
        except Exception as e:
            self.logger.error(f"Erro na análise de UEs: {str(e)}")
            return 0.0
    
    async def _analyze_app_metrics_performance(self, app_metrics_data: Dict[str, Any]) -> float:
        """Analisar performance de métricas de aplicação"""
        try:
            score = 100.0
            
            # Verificar taxa de sucesso HTTP
            if "http_success_rate" in app_metrics_data:
                http_success = app_metrics_data["http_success_rate"]
                if http_success < 95:  # Taxa de sucesso muito baixa
                    score -= 20
                elif http_success < 98:
                    score -= 10
            
            # Verificar taxa de sucesso de API
            if "api_success_rate" in app_metrics_data:
                api_success = app_metrics_data["api_success_rate"]
                if api_success < 95:  # Taxa de sucesso muito baixa
                    score -= 20
                elif api_success < 98:
                    score -= 10
            
            return max(0.0, min(100.0, score))
            
        except Exception as e:
            self.logger.error(f"Erro na análise de métricas de aplicação: {str(e)}")
            return 0.0
    
    async def _analyze_service_performance(self, service_data: Dict[str, Any]) -> float:
        """Analisar performance de serviços"""
        try:
            score = 100.0
            
            # Verificar taxa de sucesso de serviços
            if "service_success_rate" in service_data:
                service_success = service_data["service_success_rate"]
                if service_success < 95:  # Taxa de sucesso muito baixa
                    score -= 20
                elif service_success < 98:
                    score -= 10
            
            # Verificar latência de serviços
            if "service_latency" in service_data:
                service_latency = service_data["service_latency"]
                if service_latency > self.thresholds["latency"]:
                    score -= (service_latency - self.thresholds["latency"]) * 0.5
            
            return max(0.0, min(100.0, score))
            
        except Exception as e:
            self.logger.error(f"Erro na análise de serviços: {str(e)}")
            return 0.0
    
    async def _generate_recommendations(self, performance_analysis: Dict[str, Any]) -> List[str]:
        """Gerar recomendações baseadas na análise de performance"""
        try:
            recommendations = []
            
            # Verificar score geral
            overall_score = performance_analysis.get("overall_score", 0)
            if overall_score < 70:
                recommendations.append("Revisar configuração geral da rede")
            
            # Verificar componentes
            components = performance_analysis.get("components", {})
            
            # Verificar 5G Core
            if "core" in components:
                core_score = components["core"].get("score", 0)
                if core_score < 70:
                    recommendations.append("Otimizar configuração do 5G Core")
            
            # Verificar RAN
            if "ran" in components:
                ran_score = components["ran"].get("score", 0)
                if ran_score < 70:
                    recommendations.append("Otimizar configuração do RAN")
            
            # Verificar transporte
            if "transport" in components:
                transport_score = components["transport"].get("score", 0)
                if transport_score < 70:
                    recommendations.append("Otimizar configuração de transporte")
            
            # Verificar aplicação
            if "application" in components:
                app_score = components["application"].get("score", 0)
                if app_score < 70:
                    recommendations.append("Otimizar configuração de aplicação")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar recomendações: {str(e)}")
            return []
    
    async def get_metrics_history(self) -> List[PerformanceMetrics]:
        """Obter histórico de métricas"""
        return self.metrics_history
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Obter status de saúde da rede"""
        try:
            if not self.metrics_history:
                return {"status": "unknown", "score": 0.0}
            
            # Obter métricas mais recentes
            latest_metrics = self.metrics_history[-1]
            overall_score = latest_metrics.metrics.get("overall_score", 0)
            
            # Determinar status
            if overall_score >= 90:
                status = "healthy"
            elif overall_score >= 70:
                status = "warning"
            else:
                status = "critical"
            
            return {
                "status": status,
                "score": overall_score,
                "timestamp": latest_metrics.timestamp.isoformat(),
                "component_scores": {
                    "core": latest_metrics.metrics.get("core_score", 0),
                    "ran": latest_metrics.metrics.get("ran_score", 0),
                    "transport": latest_metrics.metrics.get("transport_score", 0),
                    "app": latest_metrics.metrics.get("app_score", 0)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao obter status de saúde: {str(e)}")
            return {"status": "error", "score": 0.0}
