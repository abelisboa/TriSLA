#!/usr/bin/env python3
"""
Modelos de dados para NWDAF
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

class DataSource(Enum):
    """Fontes de dados de rede"""
    CORE_5G = "core_5g"
    RAN = "ran"
    TRANSPORT = "transport"
    APPLICATION = "application"
    EXTERNAL = "external"

class AnalyticsStatus(Enum):
    """Status das análises"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class NetworkData:
    """Dados de rede coletados pelo NWDAF"""
    data_id: str
    timestamp: datetime
    core_data: Dict[str, Any]
    ran_data: Dict[str, Any]
    transport_data: Dict[str, Any]
    app_data: Dict[str, Any]
    nwdaf_id: str
    data_sources: List[DataSource] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário"""
        return {
            "data_id": self.data_id,
            "timestamp": self.timestamp.isoformat(),
            "core_data": self.core_data,
            "ran_data": self.ran_data,
            "transport_data": self.transport_data,
            "app_data": self.app_data,
            "nwdaf_id": self.nwdaf_id,
            "data_sources": [ds.value for ds in self.data_sources],
            "metadata": self.metadata
        }

@dataclass
class AnalyticsData:
    """Dados de análise do NWDAF"""
    analytics_id: str
    timestamp: datetime
    network_data_id: str
    analyses: List[Dict[str, Any]]
    nwdaf_id: str
    status: AnalyticsStatus = AnalyticsStatus.COMPLETED
    processing_time: float = 0.0
    confidence_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário"""
        return {
            "analytics_id": self.analytics_id,
            "timestamp": self.timestamp.isoformat(),
            "network_data_id": self.network_data_id,
            "analyses": self.analyses,
            "nwdaf_id": self.nwdaf_id,
            "status": self.status.value,
            "processing_time": self.processing_time,
            "confidence_score": self.confidence_score,
            "metadata": self.metadata
        }

@dataclass
class PredictionResult:
    """Resultado de predição do NWDAF"""
    prediction_id: str
    timestamp: datetime
    prediction_type: str
    predicted_value: float
    confidence: float
    actual_value: Optional[float] = None
    accuracy: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário"""
        return {
            "prediction_id": self.prediction_id,
            "timestamp": self.timestamp.isoformat(),
            "prediction_type": self.prediction_type,
            "predicted_value": self.predicted_value,
            "confidence": self.confidence,
            "actual_value": self.actual_value,
            "accuracy": self.accuracy,
            "metadata": self.metadata
        }

@dataclass
class NetworkInsight:
    """Insight de rede gerado pelo NWDAF"""
    insight_id: str
    timestamp: datetime
    insight_type: str
    description: str
    severity: str
    affected_components: List[str]
    recommendations: List[str]
    nwdaf_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário"""
        return {
            "insight_id": self.insight_id,
            "timestamp": self.timestamp.isoformat(),
            "insight_type": self.insight_type,
            "description": self.description,
            "severity": self.severity,
            "affected_components": self.affected_components,
            "recommendations": self.recommendations,
            "nwdaf_id": self.nwdaf_id,
            "metadata": self.metadata
        }

@dataclass
class QoSProfile:
    """Perfil de QoS para análise"""
    profile_id: str
    name: str
    latency_requirement: float  # ms
    reliability_requirement: float  # %
    throughput_requirement: float  # Mbps
    jitter_requirement: float  # ms
    packet_loss_requirement: float  # %
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário"""
        return {
            "profile_id": self.profile_id,
            "name": self.name,
            "latency_requirement": self.latency_requirement,
            "reliability_requirement": self.reliability_requirement,
            "throughput_requirement": self.throughput_requirement,
            "jitter_requirement": self.jitter_requirement,
            "packet_loss_requirement": self.packet_loss_requirement,
            "metadata": self.metadata
        }

@dataclass
class SliceAnalytics:
    """Análise de slice de rede"""
    slice_id: str
    slice_type: str  # URLLC, eMBB, mMTC
    timestamp: datetime
    performance_metrics: Dict[str, float]
    sla_compliance: bool
    violations: List[str]
    recommendations: List[str]
    nwdaf_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário"""
        return {
            "slice_id": self.slice_id,
            "slice_type": self.slice_type,
            "timestamp": self.timestamp.isoformat(),
            "performance_metrics": self.performance_metrics,
            "sla_compliance": self.sla_compliance,
            "violations": self.violations,
            "recommendations": self.recommendations,
            "nwdaf_id": self.nwdaf_id,
            "metadata": self.metadata
        }

@dataclass
class TrafficPattern:
    """Padrão de tráfego identificado"""
    pattern_id: str
    timestamp: datetime
    pattern_type: str
    characteristics: Dict[str, Any]
    confidence: float
    duration: float  # segundos
    nwdaf_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário"""
        return {
            "pattern_id": self.pattern_id,
            "timestamp": self.timestamp.isoformat(),
            "pattern_type": self.pattern_type,
            "characteristics": self.characteristics,
            "confidence": self.confidence,
            "duration": self.duration,
            "nwdaf_id": self.nwdaf_id,
            "metadata": self.metadata
        }

@dataclass
class AnomalyDetection:
    """Detecção de anomalia"""
    anomaly_id: str
    timestamp: datetime
    anomaly_type: str
    severity: str
    affected_components: List[str]
    description: str
    confidence: float
    nwdaf_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário"""
        return {
            "anomaly_id": self.anomaly_id,
            "timestamp": self.timestamp.isoformat(),
            "anomaly_type": self.anomaly_type,
            "severity": self.severity,
            "affected_components": self.affected_components,
            "description": self.description,
            "confidence": self.confidence,
            "nwdaf_id": self.nwdaf_id,
            "metadata": self.metadata
        }

@dataclass
class NetworkHealth:
    """Saúde da rede"""
    health_id: str
    timestamp: datetime
    overall_health: str  # healthy, warning, critical
    component_health: Dict[str, str]
    health_score: float  # 0-100
    issues: List[str]
    recommendations: List[str]
    nwdaf_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário"""
        return {
            "health_id": self.health_id,
            "timestamp": self.timestamp.isoformat(),
            "overall_health": self.overall_health,
            "component_health": self.component_health,
            "health_score": self.health_score,
            "issues": self.issues,
            "recommendations": self.recommendations,
            "nwdaf_id": self.nwdaf_id,
            "metadata": self.metadata
        }

@dataclass
class PerformanceMetrics:
    """Métricas de performance"""
    metrics_id: str
    timestamp: datetime
    component: str
    metrics: Dict[str, float]
    thresholds: Dict[str, float]
    violations: List[str]
    nwdaf_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário"""
        return {
            "metrics_id": self.metrics_id,
            "timestamp": self.timestamp.isoformat(),
            "component": self.component,
            "metrics": self.metrics,
            "thresholds": self.thresholds,
            "violations": self.violations,
            "nwdaf_id": self.nwdaf_id,
            "metadata": self.metadata
        }
