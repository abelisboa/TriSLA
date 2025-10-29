#!/usr/bin/env python3
"""
Analisador de Tráfego - NWDAF
"""

import asyncio
import logging
import statistics
import math
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import uuid

from ..models.data_models import NetworkData, TrafficPattern, SliceAnalytics
from apps.common.telemetry import trace_function, measure_time

class TrafficAnalyzer:
    """Analisador de padrões de tráfego"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Padrões de tráfego conhecidos
        self.traffic_patterns = {
            "burst": {
                "name": "Burst Traffic",
                "characteristics": ["high_peak", "short_duration", "irregular"],
                "thresholds": {"peak_factor": 3.0, "duration_max": 60}
            },
            "steady": {
                "name": "Steady Traffic",
                "characteristics": ["constant_rate", "low_variance", "predictable"],
                "thresholds": {"variance_max": 0.2, "rate_stability": 0.9}
            },
            "periodic": {
                "name": "Periodic Traffic",
                "characteristics": ["recurring", "time_based", "cyclical"],
                "thresholds": {"period_variance": 0.1, "cycle_detection": 0.8}
            },
            "sporadic": {
                "name": "Sporadic Traffic",
                "characteristics": ["random", "unpredictable", "low_frequency"],
                "thresholds": {"frequency_min": 0.1, "randomness": 0.7}
            }
        }
        
        # Histórico de padrões identificados
        self.pattern_history: List[TrafficPattern] = []
        self.max_history_size = 1000
        
        # Dados de tráfego para análise
        self.traffic_data_buffer: List[Dict[str, Any]] = []
        self.buffer_size = 100
        
        # Status do analisador
        self.running = False
        self.initialized = False
    
    async def initialize(self):
        """Inicializar analisador"""
        try:
            self.logger.info("Inicializando Traffic Analyzer")
            self.initialized = True
            self.logger.info("Traffic Analyzer inicializado")
        except Exception as e:
            self.logger.error(f"Erro ao inicializar Traffic Analyzer: {str(e)}")
            raise
    
    async def stop(self):
        """Parar analisador"""
        try:
            self.running = False
            self.logger.info("Traffic Analyzer parado")
        except Exception as e:
            self.logger.error(f"Erro ao parar Traffic Analyzer: {str(e)}")
    
    @trace_function(operation_name="analyze_traffic")
    @measure_time
    async def analyze_traffic(self, network_data: NetworkData) -> Dict[str, Any]:
        """Analisar padrões de tráfego"""
        try:
            self.logger.debug("Iniciando análise de tráfego")
            
            # Extrair dados de tráfego
            traffic_data = await self._extract_traffic_data(network_data)
            
            # Adicionar ao buffer
            self.traffic_data_buffer.append(traffic_data)
            if len(self.traffic_data_buffer) > self.buffer_size:
                self.traffic_data_buffer = self.traffic_data_buffer[-self.buffer_size:]
            
            # Analisar padrões de tráfego
            patterns = await self._identify_traffic_patterns(traffic_data)
            
            # Analisar slices
            slice_analysis = await self._analyze_slice_traffic(network_data)
            
            # Analisar tendências
            trends = await self._analyze_traffic_trends()
            
            # Consolidar análise
            traffic_analysis = {
                "analysis_type": "traffic_analysis",
                "timestamp": datetime.now().isoformat(),
                "traffic_data": traffic_data,
                "patterns": patterns,
                "slice_analysis": slice_analysis,
                "trends": trends,
                "recommendations": [],
                "alerts": []
            }
            
            # Gerar recomendações
            traffic_analysis["recommendations"] = await self._generate_traffic_recommendations(patterns, slice_analysis)
            
            # Gerar alertas
            traffic_analysis["alerts"] = await self._generate_traffic_alerts(patterns, slice_analysis)
            
            self.logger.info(f"Análise de tráfego concluída - Padrões: {len(patterns)}")
            return traffic_analysis
            
        except Exception as e:
            self.logger.error(f"Erro na análise de tráfego: {str(e)}")
            raise
    
    async def _extract_traffic_data(self, network_data: NetworkData) -> Dict[str, Any]:
        """Extrair dados de tráfego dos dados de rede"""
        try:
            traffic_data = {
                "timestamp": datetime.now().isoformat(),
                "throughput": {},
                "latency": {},
                "packet_rates": {},
                "connection_counts": {},
                "resource_utilization": {}
            }
            
            # Extrair throughput
            if "ran_data" in network_data.to_dict():
                ran_data = network_data.ran_data
                if "traffic_metrics" in ran_data:
                    traffic_metrics = ran_data["traffic_metrics"]
                    traffic_data["throughput"]["ul"] = traffic_metrics.get("ul_throughput", 0)
                    traffic_data["throughput"]["dl"] = traffic_metrics.get("dl_throughput", 0)
                    traffic_data["throughput"]["total"] = traffic_data["throughput"]["ul"] + traffic_data["throughput"]["dl"]
            
            # Extrair latência
            if "ran_data" in network_data.to_dict():
                ran_data = network_data.ran_data
                if "traffic_metrics" in ran_data:
                    traffic_metrics = ran_data["traffic_metrics"]
                    traffic_data["latency"]["ul"] = traffic_metrics.get("ul_latency", 0)
                    traffic_data["latency"]["dl"] = traffic_metrics.get("dl_latency", 0)
                    traffic_data["latency"]["avg"] = (traffic_data["latency"]["ul"] + traffic_data["latency"]["dl"]) / 2
            
            # Extrair taxas de pacotes
            if "transport_data" in network_data.to_dict():
                transport_data = network_data.transport_data
                if "packet_metrics" in transport_data:
                    packet_metrics = transport_data["packet_metrics"]
                    traffic_data["packet_rates"]["sent"] = packet_metrics.get("packets_sent", 0)
                    traffic_data["packet_rates"]["received"] = packet_metrics.get("packets_received", 0)
                    traffic_data["packet_rates"]["loss_rate"] = packet_metrics.get("packet_loss_rate", 0)
                    traffic_data["packet_rates"]["error_rate"] = packet_metrics.get("packet_error_rate", 0)
            
            # Extrair contagens de conexão
            if "app_data" in network_data.to_dict():
                app_data = network_data.app_data
                if "user_equipment" in app_data:
                    ue_data = app_data["user_equipment"]
                    traffic_data["connection_counts"]["total_ues"] = ue_data.get("connected_ues", 0)
                    traffic_data["connection_counts"]["active_ues"] = ue_data.get("active_ues", 0)
                    traffic_data["connection_counts"]["connection_rate"] = ue_data.get("ue_connection_rate", 0)
            
            # Extrair utilização de recursos
            if "ran_data" in network_data.to_dict():
                ran_data = network_data.ran_data
                if "resource_utilization" in ran_data:
                    resource_util = ran_data["resource_utilization"]
                    traffic_data["resource_utilization"]["prb"] = resource_util.get("prb_utilization", 0)
                    traffic_data["resource_utilization"]["cpu"] = resource_util.get("cpu_usage", 0)
                    traffic_data["resource_utilization"]["memory"] = resource_util.get("memory_usage", 0)
            
            return traffic_data
            
        except Exception as e:
            self.logger.error(f"Erro ao extrair dados de tráfego: {str(e)}")
            return {}
    
    async def _identify_traffic_patterns(self, traffic_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identificar padrões de tráfego"""
        try:
            patterns = []
            
            # Verificar se há dados suficientes
            if len(self.traffic_data_buffer) < 5:
                return patterns
            
            # Analisar padrão de burst
            burst_pattern = await self._detect_burst_pattern(traffic_data)
            if burst_pattern:
                patterns.append(burst_pattern)
            
            # Analisar padrão steady
            steady_pattern = await self._detect_steady_pattern(traffic_data)
            if steady_pattern:
                patterns.append(steady_pattern)
            
            # Analisar padrão periódico
            periodic_pattern = await self._detect_periodic_pattern(traffic_data)
            if periodic_pattern:
                patterns.append(periodic_pattern)
            
            # Analisar padrão esporádico
            sporadic_pattern = await self._detect_sporadic_pattern(traffic_data)
            if sporadic_pattern:
                patterns.append(sporadic_pattern)
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Erro na identificação de padrões: {str(e)}")
            return []
    
    async def _detect_burst_pattern(self, traffic_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detectar padrão de burst"""
        try:
            if len(self.traffic_data_buffer) < 3:
                return None
            
            # Calcular estatísticas de throughput
            throughput_values = []
            for data in self.traffic_data_buffer[-10:]:  # Últimos 10 pontos
                if "throughput" in data and "total" in data["throughput"]:
                    throughput_values.append(data["throughput"]["total"])
            
            if len(throughput_values) < 3:
                return None
            
            # Calcular média e desvio padrão
            mean_throughput = statistics.mean(throughput_values)
            std_throughput = statistics.stdev(throughput_values) if len(throughput_values) > 1 else 0
            
            # Verificar se há picos significativos
            current_throughput = traffic_data.get("throughput", {}).get("total", 0)
            peak_factor = current_throughput / mean_throughput if mean_throughput > 0 else 0
            
            if peak_factor > self.traffic_patterns["burst"]["thresholds"]["peak_factor"]:
                # Criar padrão de burst
                pattern = TrafficPattern(
                    pattern_id=str(uuid.uuid4()),
                    timestamp=datetime.now(),
                    pattern_type="burst",
                    characteristics={
                        "peak_factor": peak_factor,
                        "mean_throughput": mean_throughput,
                        "current_throughput": current_throughput,
                        "variance": std_throughput
                    },
                    confidence=min(1.0, peak_factor / 5.0),
                    duration=30.0,  # Simulado
                    nwdaf_id=traffic_data.get("nwdaf_id", "nwdaf-001")
                )
                
                # Armazenar no histórico
                self.pattern_history.append(pattern)
                if len(self.pattern_history) > self.max_history_size:
                    self.pattern_history = self.pattern_history[-self.max_history_size:]
                
                return pattern.to_dict()
            
            return None
            
        except Exception as e:
            self.logger.error(f"Erro na detecção de padrão burst: {str(e)}")
            return None
    
    async def _detect_steady_pattern(self, traffic_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detectar padrão steady"""
        try:
            if len(self.traffic_data_buffer) < 5:
                return None
            
            # Calcular estatísticas de throughput
            throughput_values = []
            for data in self.traffic_data_buffer[-20:]:  # Últimos 20 pontos
                if "throughput" in data and "total" in data["throughput"]:
                    throughput_values.append(data["throughput"]["total"])
            
            if len(throughput_values) < 5:
                return None
            
            # Calcular coeficiente de variação
            mean_throughput = statistics.mean(throughput_values)
            std_throughput = statistics.stdev(throughput_values) if len(throughput_values) > 1 else 0
            cv = std_throughput / mean_throughput if mean_throughput > 0 else 0
            
            # Verificar se é steady
            if cv < self.traffic_patterns["steady"]["thresholds"]["variance_max"]:
                # Criar padrão steady
                pattern = TrafficPattern(
                    pattern_id=str(uuid.uuid4()),
                    timestamp=datetime.now(),
                    pattern_type="steady",
                    characteristics={
                        "mean_throughput": mean_throughput,
                        "std_throughput": std_throughput,
                        "coefficient_of_variation": cv,
                        "stability": 1.0 - cv
                    },
                    confidence=1.0 - cv,
                    duration=300.0,  # Simulado
                    nwdaf_id=traffic_data.get("nwdaf_id", "nwdaf-001")
                )
                
                # Armazenar no histórico
                self.pattern_history.append(pattern)
                if len(self.pattern_history) > self.max_history_size:
                    self.pattern_history = self.pattern_history[-self.max_history_size:]
                
                return pattern.to_dict()
            
            return None
            
        except Exception as e:
            self.logger.error(f"Erro na detecção de padrão steady: {str(e)}")
            return None
    
    async def _detect_periodic_pattern(self, traffic_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detectar padrão periódico"""
        try:
            if len(self.traffic_data_buffer) < 10:
                return None
            
            # Calcular autocorrelação para detectar periodicidade
            throughput_values = []
            for data in self.traffic_data_buffer[-30:]:  # Últimos 30 pontos
                if "throughput" in data and "total" in data["throughput"]:
                    throughput_values.append(data["throughput"]["total"])
            
            if len(throughput_values) < 10:
                return None
            
            # Calcular autocorrelação
            autocorr = await self._calculate_autocorrelation(throughput_values)
            
            # Encontrar picos de autocorrelação
            peaks = []
            for i in range(1, len(autocorr) - 1):
                if autocorr[i] > autocorr[i-1] and autocorr[i] > autocorr[i+1] and autocorr[i] > 0.5:
                    peaks.append(i)
            
            if peaks:
                # Calcular período médio
                periods = [peaks[i] - peaks[i-1] for i in range(1, len(peaks))]
                if periods:
                    avg_period = statistics.mean(periods)
                    period_variance = statistics.stdev(periods) if len(periods) > 1 else 0
                    
                    # Verificar se é periódico
                    if period_variance < self.traffic_patterns["periodic"]["thresholds"]["period_variance"]:
                        # Criar padrão periódico
                        pattern = TrafficPattern(
                            pattern_id=str(uuid.uuid4()),
                            timestamp=datetime.now(),
                            pattern_type="periodic",
                            characteristics={
                                "period": avg_period,
                                "period_variance": period_variance,
                                "autocorrelation_peaks": len(peaks),
                                "max_autocorrelation": max(autocorr)
                            },
                            confidence=min(1.0, max(autocorr)),
                            duration=avg_period * 2,
                            nwdaf_id=traffic_data.get("nwdaf_id", "nwdaf-001")
                        )
                        
                        # Armazenar no histórico
                        self.pattern_history.append(pattern)
                        if len(self.pattern_history) > self.max_history_size:
                            self.pattern_history = self.pattern_history[-self.max_history_size:]
                        
                        return pattern.to_dict()
            
            return None
            
        except Exception as e:
            self.logger.error(f"Erro na detecção de padrão periódico: {str(e)}")
            return None
    
    async def _detect_sporadic_pattern(self, traffic_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detectar padrão esporádico"""
        try:
            if len(self.traffic_data_buffer) < 10:
                return None
            
            # Calcular frequência de atividade
            active_periods = 0
            total_periods = len(self.traffic_data_buffer)
            
            for data in self.traffic_data_buffer:
                if "throughput" in data and "total" in data["throughput"]:
                    if data["throughput"]["total"] > 0:
                        active_periods += 1
            
            activity_frequency = active_periods / total_periods if total_periods > 0 else 0
            
            # Verificar se é esporádico
            if activity_frequency < self.traffic_patterns["sporadic"]["thresholds"]["frequency_min"]:
                # Calcular aleatoriedade
                randomness = await self._calculate_randomness(self.traffic_data_buffer)
                
                if randomness > self.traffic_patterns["sporadic"]["thresholds"]["randomness"]:
                    # Criar padrão esporádico
                    pattern = TrafficPattern(
                        pattern_id=str(uuid.uuid4()),
                        timestamp=datetime.now(),
                        pattern_type="sporadic",
                        characteristics={
                            "activity_frequency": activity_frequency,
                            "randomness": randomness,
                            "active_periods": active_periods,
                            "total_periods": total_periods
                        },
                        confidence=randomness,
                        duration=60.0,  # Simulado
                        nwdaf_id=traffic_data.get("nwdaf_id", "nwdaf-001")
                    )
                    
                    # Armazenar no histórico
                    self.pattern_history.append(pattern)
                    if len(self.pattern_history) > self.max_history_size:
                        self.pattern_history = self.pattern_history[-self.max_history_size:]
                    
                    return pattern.to_dict()
            
            return None
            
        except Exception as e:
            self.logger.error(f"Erro na detecção de padrão esporádico: {str(e)}")
            return None
    
    async def _calculate_autocorrelation(self, values: List[float]) -> List[float]:
        """Calcular autocorrelação"""
        try:
            n = len(values)
            if n < 2:
                return [0.0]
            
            # Normalizar valores
            mean_val = statistics.mean(values)
            std_val = statistics.stdev(values) if n > 1 else 1.0
            
            if std_val == 0:
                return [0.0] * n
            
            normalized_values = [(v - mean_val) / std_val for v in values]
            
            # Calcular autocorrelação
            autocorr = []
            for lag in range(n):
                if lag == 0:
                    autocorr.append(1.0)
                else:
                    numerator = sum(normalized_values[i] * normalized_values[i + lag] for i in range(n - lag))
                    denominator = sum(v * v for v in normalized_values)
                    if denominator > 0:
                        autocorr.append(numerator / denominator)
                    else:
                        autocorr.append(0.0)
            
            return autocorr
            
        except Exception as e:
            self.logger.error(f"Erro no cálculo de autocorrelação: {str(e)}")
            return [0.0]
    
    async def _calculate_randomness(self, data_buffer: List[Dict[str, Any]]) -> float:
        """Calcular aleatoriedade dos dados"""
        try:
            if len(data_buffer) < 5:
                return 0.0
            
            # Extrair valores de throughput
            throughput_values = []
            for data in data_buffer:
                if "throughput" in data and "total" in data["throughput"]:
                    throughput_values.append(data["throughput"]["total"])
            
            if len(throughput_values) < 5:
                return 0.0
            
            # Calcular entropia de Shannon
            # Discretizar valores
            min_val = min(throughput_values)
            max_val = max(throughput_values)
            if max_val == min_val:
                return 0.0
            
            # Dividir em bins
            num_bins = min(10, len(throughput_values))
            bin_size = (max_val - min_val) / num_bins
            
            bins = [0] * num_bins
            for val in throughput_values:
                bin_idx = min(int((val - min_val) / bin_size), num_bins - 1)
                bins[bin_idx] += 1
            
            # Calcular entropia
            entropy = 0.0
            for count in bins:
                if count > 0:
                    p = count / len(throughput_values)
                    entropy -= p * math.log2(p)
            
            # Normalizar entropia
            max_entropy = math.log2(num_bins)
            normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
            
            return normalized_entropy
            
        except Exception as e:
            self.logger.error(f"Erro no cálculo de aleatoriedade: {str(e)}")
            return 0.0
    
    async def _analyze_slice_traffic(self, network_data: NetworkData) -> Dict[str, Any]:
        """Analisar tráfego por slice"""
        try:
            slice_analysis = {
                "slices": {},
                "total_traffic": 0,
                "traffic_distribution": {}
            }
            
            # Analisar slices URLLC
            if "app_data" in network_data.to_dict():
                app_data = network_data.app_data
                if "slice_instances" in app_data:
                    slice_instances = app_data["slice_instances"]
                    
                    # URLLC
                    if "urllc_slices" in slice_instances:
                        urllc_count = slice_instances["urllc_slices"]
                        slice_analysis["slices"]["urllc"] = {
                            "count": urllc_count,
                            "traffic_type": "low_latency",
                            "expected_throughput": 1.0,
                            "expected_latency": 1.0,
                            "priority": "high"
                        }
                    
                    # eMBB
                    if "embb_slices" in slice_instances:
                        embb_count = slice_instances["embb_slices"]
                        slice_analysis["slices"]["embb"] = {
                            "count": embb_count,
                            "traffic_type": "high_throughput",
                            "expected_throughput": 1000.0,
                            "expected_latency": 10.0,
                            "priority": "medium"
                        }
                    
                    # mMTC
                    if "mmtc_slices" in slice_instances:
                        mmtc_count = slice_instances["mmtc_slices"]
                        slice_analysis["slices"]["mmtc"] = {
                            "count": mmtc_count,
                            "traffic_type": "massive_connections",
                            "expected_throughput": 1.0,
                            "expected_latency": 100.0,
                            "priority": "low"
                        }
            
            # Calcular distribuição de tráfego
            total_slices = sum(slice_analysis["slices"][slice_type]["count"] for slice_type in slice_analysis["slices"])
            if total_slices > 0:
                for slice_type, slice_data in slice_analysis["slices"].items():
                    slice_analysis["traffic_distribution"][slice_type] = slice_data["count"] / total_slices
            
            return slice_analysis
            
        except Exception as e:
            self.logger.error(f"Erro na análise de tráfego por slice: {str(e)}")
            return {"slices": {}, "total_traffic": 0, "traffic_distribution": {}}
    
    async def _analyze_traffic_trends(self) -> Dict[str, Any]:
        """Analisar tendências de tráfego"""
        try:
            if len(self.traffic_data_buffer) < 5:
                return {"trend": "insufficient_data", "slope": 0.0, "confidence": 0.0}
            
            # Extrair valores de throughput ao longo do tempo
            throughput_values = []
            timestamps = []
            
            for data in self.traffic_data_buffer[-20:]:  # Últimos 20 pontos
                if "throughput" in data and "total" in data["throughput"]:
                    throughput_values.append(data["throughput"]["total"])
                    timestamps.append(data.get("timestamp", datetime.now().isoformat()))
            
            if len(throughput_values) < 5:
                return {"trend": "insufficient_data", "slope": 0.0, "confidence": 0.0}
            
            # Calcular regressão linear simples
            n = len(throughput_values)
            x_values = list(range(n))
            
            # Calcular coeficientes
            sum_x = sum(x_values)
            sum_y = sum(throughput_values)
            sum_xy = sum(x * y for x, y in zip(x_values, throughput_values))
            sum_x2 = sum(x * x for x in x_values)
            
            # Calcular slope
            denominator = n * sum_x2 - sum_x * sum_x
            if denominator != 0:
                slope = (n * sum_xy - sum_x * sum_y) / denominator
            else:
                slope = 0.0
            
            # Calcular coeficiente de correlação
            mean_x = sum_x / n
            mean_y = sum_y / n
            
            numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(x_values, throughput_values))
            denominator_x = sum((x - mean_x) ** 2 for x in x_values)
            denominator_y = sum((y - mean_y) ** 2 for y in throughput_values)
            
            if denominator_x > 0 and denominator_y > 0:
                correlation = numerator / math.sqrt(denominator_x * denominator_y)
            else:
                correlation = 0.0
            
            # Determinar tendência
            if abs(slope) < 0.1:
                trend = "stable"
            elif slope > 0.1:
                trend = "increasing"
            else:
                trend = "decreasing"
            
            return {
                "trend": trend,
                "slope": slope,
                "correlation": correlation,
                "confidence": abs(correlation),
                "data_points": n
            }
            
        except Exception as e:
            self.logger.error(f"Erro na análise de tendências: {str(e)}")
            return {"trend": "error", "slope": 0.0, "confidence": 0.0}
    
    async def _generate_traffic_recommendations(self, patterns: List[Dict[str, Any]], slice_analysis: Dict[str, Any]) -> List[str]:
        """Gerar recomendações baseadas na análise de tráfego"""
        try:
            recommendations = []
            
            # Recomendações baseadas em padrões
            for pattern in patterns:
                pattern_type = pattern.get("pattern_type", "")
                
                if pattern_type == "burst":
                    recommendations.append("Implementar buffer de tráfego para lidar com picos de burst")
                    recommendations.append("Considerar escalonamento automático para picos de tráfego")
                
                elif pattern_type == "steady":
                    recommendations.append("Otimizar recursos para tráfego constante")
                    recommendations.append("Implementar previsão de capacidade baseada em padrão steady")
                
                elif pattern_type == "periodic":
                    recommendations.append("Implementar agendamento baseado em padrões periódicos")
                    recommendations.append("Otimizar recursos para picos previsíveis")
                
                elif pattern_type == "sporadic":
                    recommendations.append("Implementar políticas de QoS para tráfego esporádico")
                    recommendations.append("Considerar recursos sob demanda para tráfego imprevisível")
            
            # Recomendações baseadas em slices
            if "traffic_distribution" in slice_analysis:
                distribution = slice_analysis["traffic_distribution"]
                
                if "urllc" in distribution and distribution["urllc"] > 0.5:
                    recommendations.append("Priorizar recursos para slices URLLC")
                
                if "embb" in distribution and distribution["embb"] > 0.5:
                    recommendations.append("Otimizar largura de banda para slices eMBB")
                
                if "mmtc" in distribution and distribution["mmtc"] > 0.5:
                    recommendations.append("Implementar políticas de conexão para slices mMTC")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar recomendações de tráfego: {str(e)}")
            return []
    
    async def _generate_traffic_alerts(self, patterns: List[Dict[str, Any]], slice_analysis: Dict[str, Any]) -> List[str]:
        """Gerar alertas baseados na análise de tráfego"""
        try:
            alerts = []
            
            # Alertas baseados em padrões
            for pattern in patterns:
                pattern_type = pattern.get("pattern_type", "")
                confidence = pattern.get("confidence", 0)
                
                if pattern_type == "burst" and confidence > 0.8:
                    alerts.append(f"ALERTA: Padrão de burst detectado com confiança {confidence:.2f}")
                
                elif pattern_type == "sporadic" and confidence > 0.7:
                    alerts.append(f"ALERTA: Padrão esporádico detectado com confiança {confidence:.2f}")
            
            # Alertas baseados em slices
            if "slices" in slice_analysis:
                for slice_type, slice_data in slice_analysis["slices"].items():
                    count = slice_data.get("count", 0)
                    if count == 0:
                        alerts.append(f"ALERTA: Nenhum slice {slice_type} ativo")
                    elif count > 10:
                        alerts.append(f"ALERTA: Muitos slices {slice_type} ativos ({count})")
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar alertas de tráfego: {str(e)}")
            return []
    
    async def get_pattern_history(self) -> List[TrafficPattern]:
        """Obter histórico de padrões"""
        return self.pattern_history
    
    async def get_traffic_statistics(self) -> Dict[str, Any]:
        """Obter estatísticas de tráfego"""
        try:
            if not self.traffic_data_buffer:
                return {"status": "no_data"}
            
            # Calcular estatísticas
            throughput_values = []
            latency_values = []
            
            for data in self.traffic_data_buffer:
                if "throughput" in data and "total" in data["throughput"]:
                    throughput_values.append(data["throughput"]["total"])
                
                if "latency" in data and "avg" in data["latency"]:
                    latency_values.append(data["latency"]["avg"])
            
            stats = {
                "data_points": len(self.traffic_data_buffer),
                "throughput": {
                    "mean": statistics.mean(throughput_values) if throughput_values else 0,
                    "std": statistics.stdev(throughput_values) if len(throughput_values) > 1 else 0,
                    "min": min(throughput_values) if throughput_values else 0,
                    "max": max(throughput_values) if throughput_values else 0
                },
                "latency": {
                    "mean": statistics.mean(latency_values) if latency_values else 0,
                    "std": statistics.stdev(latency_values) if len(latency_values) > 1 else 0,
                    "min": min(latency_values) if latency_values else 0,
                    "max": max(latency_values) if latency_values else 0
                },
                "patterns_detected": len(self.pattern_history)
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Erro ao obter estatísticas de tráfego: {str(e)}")
            return {"status": "error"}
