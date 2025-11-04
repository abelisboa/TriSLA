#!/usr/bin/env python3
"""
Interface I-03: ML-NSMF ← NASP Telemetry (Kafka)
Consome telemetria em tempo real do NASP para ML-NSMF
"""

import asyncio
import logging
import json
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from dataclasses import dataclass
import uuid

# Configurar logging
logger = logging.getLogger(__name__)

@dataclass
class NASPTelemetryData:
    """Dados de telemetria do NASP"""
    data_id: str
    timestamp: datetime
    source: str  # "RAN", "Transport", "Core", "NASP"
    data_type: str  # "metrics", "events", "alerts", "status"
    metrics: Dict[str, Any]
    metadata: Dict[str, Any]

@dataclass
class MLPredictionRequest:
    """Requisição de predição baseada em telemetria"""
    request_id: str
    telemetry_data: NASPTelemetryData
    prediction_type: str  # "sla_viability", "resource_availability", "performance"
    timestamp: datetime
    parameters: Dict[str, Any]

@dataclass
class MLPredictionResponse:
    """Resposta de predição do ML-NSMF"""
    request_id: str
    prediction_id: str
    prediction_type: str
    result: Dict[str, Any]
    confidence: float
    timestamp: datetime
    xai_explanation: Dict[str, Any]

class I03_NASP_Telemetry_Interface:
    """Interface I-03: ML-NSMF ← NASP Telemetry (Kafka)"""
    
    def __init__(self, kafka_bootstrap_servers: str = "kafka:9092"):
        self.kafka_bootstrap_servers = kafka_bootstrap_servers
        self.logger = logging.getLogger(__name__)
        
        # Configurações de tópicos Kafka
        self.telemetry_topic = "nasp-telemetry"
        self.metrics_topic = "nasp-metrics"
        self.events_topic = "nasp-events"
        self.alerts_topic = "nasp-alerts"
        
        # Consumidores (serão inicializados quando necessário)
        self.consumer = None
        self.running = False
        
        # Callbacks para processamento de dados
        self.telemetry_callbacks: List[Callable[[NASPTelemetryData], None]] = []
        self.metrics_callbacks: List[Callable[[Dict[str, Any]], None]] = []
        self.events_callbacks: List[Callable[[Dict[str, Any]], None]] = []
        self.alerts_callbacks: List[Callable[[Dict[str, Any]], None]] = []
    
    async def initialize(self):
        """Inicializar conexões Kafka"""
        try:
            # Em produção, usar aiokafka ou kafka-python
            # Por simplicidade, simular interface Kafka
            self.logger.info("Inicializando Interface I-03...")
            self.running = True
            self.logger.info("Interface I-03 inicializada com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao inicializar Interface I-03: {str(e)}")
            raise
    
    async def shutdown(self):
        """Encerrar conexões Kafka"""
        try:
            self.running = False
            if self.consumer:
                await self.consumer.stop()
            self.logger.info("Interface I-03 encerrada")
        except Exception as e:
            self.logger.error(f"Erro ao encerrar Interface I-03: {str(e)}")
    
    async def start_consuming_telemetry(self):
        """Iniciar consumo de telemetria do NASP"""
        try:
            self.logger.info("Iniciando consumo de telemetria do NASP...")
            
            # Simular consumo de telemetria (em produção, usar Kafka real)
            while self.running:
                # Em produção:
                # async for message in self.consumer:
                #     telemetry_data = self._parse_telemetry_message(message)
                #     await self._process_telemetry_data(telemetry_data)
                
                # Simular recebimento de dados
                await self._simulate_telemetry_data()
                await asyncio.sleep(1)  # Simular ciclo de consumo
                
        except Exception as e:
            self.logger.error(f"Erro no consumo de telemetria: {str(e)}")
    
    async def _simulate_telemetry_data(self):
        """Simular dados de telemetria do NASP"""
        try:
            # Simular diferentes tipos de dados de telemetria
            data_types = ["metrics", "events", "alerts", "status"]
            sources = ["RAN", "Transport", "Core", "NASP"]
            
            for data_type in data_types:
                for source in sources:
                    if random.random() > 0.7:  # 30% de chance de gerar dados
                        telemetry_data = await self._generate_simulated_telemetry(
                            data_type, source
                        )
                        await self._process_telemetry_data(telemetry_data)
        
        except Exception as e:
            self.logger.error(f"Erro na simulação de telemetria: {str(e)}")
    
    async def _generate_simulated_telemetry(self, data_type: str, source: str) -> NASPTelemetryData:
        """Gerar dados de telemetria simulados"""
        import random
        
        current_time = datetime.now()
        
        if data_type == "metrics":
            metrics = {
                "cpu_usage": random.uniform(20, 90),
                "memory_usage": random.uniform(30, 95),
                "latency": random.uniform(1, 50),
                "throughput": random.uniform(100, 2000),
                "error_rate": random.uniform(0.001, 0.5)
            }
        elif data_type == "events":
            metrics = {
                "event_type": random.choice(["slice_created", "slice_modified", "slice_deleted"]),
                "slice_id": f"slice-{random.randint(1000, 9999)}",
                "timestamp": current_time.isoformat(),
                "severity": random.choice(["info", "warning", "error"])
            }
        elif data_type == "alerts":
            metrics = {
                "alert_type": random.choice(["sla_violation", "resource_exhaustion", "performance_degradation"]),
                "severity": random.choice(["low", "medium", "high", "critical"]),
                "message": f"Alert from {source}",
                "timestamp": current_time.isoformat()
            }
        else:  # status
            metrics = {
                "status": random.choice(["healthy", "warning", "critical"]),
                "uptime": random.uniform(95, 100),
                "last_check": current_time.isoformat()
            }
        
        return NASPTelemetryData(
            data_id=str(uuid.uuid4()),
            timestamp=current_time,
            source=source,
            data_type=data_type,
            metrics=metrics,
            metadata={
                "version": "1.0",
                "format": "json",
                "compression": "none"
            }
        )
    
    async def _process_telemetry_data(self, telemetry_data: NASPTelemetryData):
        """Processar dados de telemetria recebidos"""
        try:
            self.logger.debug(f"Processando telemetria: {telemetry_data.data_type} de {telemetry_data.source}")
            
            # Chamar callbacks registrados
            for callback in self.telemetry_callbacks:
                try:
                    await callback(telemetry_data)
                except Exception as e:
                    self.logger.error(f"Erro no callback de telemetria: {str(e)}")
            
            # Processar por tipo de dados
            if telemetry_data.data_type == "metrics":
                await self._process_metrics_data(telemetry_data)
            elif telemetry_data.data_type == "events":
                await self._process_events_data(telemetry_data)
            elif telemetry_data.data_type == "alerts":
                await self._process_alerts_data(telemetry_data)
            elif telemetry_data.data_type == "status":
                await self._process_status_data(telemetry_data)
        
        except Exception as e:
            self.logger.error(f"Erro ao processar dados de telemetria: {str(e)}")
    
    async def _process_metrics_data(self, telemetry_data: NASPTelemetryData):
        """Processar dados de métricas"""
        try:
            metrics = telemetry_data.metrics
            
            # Chamar callbacks de métricas
            for callback in self.metrics_callbacks:
                try:
                    await callback(metrics)
                except Exception as e:
                    self.logger.error(f"Erro no callback de métricas: {str(e)}")
            
            # Processar métricas específicas
            if "cpu_usage" in metrics:
                await self._process_cpu_metrics(metrics["cpu_usage"], telemetry_data.source)
            
            if "latency" in metrics:
                await self._process_latency_metrics(metrics["latency"], telemetry_data.source)
            
            if "throughput" in metrics:
                await self._process_throughput_metrics(metrics["throughput"], telemetry_data.source)
        
        except Exception as e:
            self.logger.error(f"Erro ao processar dados de métricas: {str(e)}")
    
    async def _process_events_data(self, telemetry_data: NASPTelemetryData):
        """Processar dados de eventos"""
        try:
            event_data = telemetry_data.metrics
            
            # Chamar callbacks de eventos
            for callback in self.events_callbacks:
                try:
                    await callback(event_data)
                except Exception as e:
                    self.logger.error(f"Erro no callback de eventos: {str(e)}")
            
            # Processar eventos específicos
            event_type = event_data.get("event_type")
            if event_type == "slice_created":
                await self._process_slice_created_event(event_data)
            elif event_type == "slice_modified":
                await self._process_slice_modified_event(event_data)
            elif event_type == "slice_deleted":
                await self._process_slice_deleted_event(event_data)
        
        except Exception as e:
            self.logger.error(f"Erro ao processar dados de eventos: {str(e)}")
    
    async def _process_alerts_data(self, telemetry_data: NASPTelemetryData):
        """Processar dados de alertas"""
        try:
            alert_data = telemetry_data.metrics
            
            # Chamar callbacks de alertas
            for callback in self.alerts_callbacks:
                try:
                    await callback(alert_data)
                except Exception as e:
                    self.logger.error(f"Erro no callback de alertas: {str(e)}")
            
            # Processar alertas específicos
            alert_type = alert_data.get("alert_type")
            severity = alert_data.get("severity")
            
            if severity == "critical":
                self.logger.critical(f"ALERTA CRÍTICO: {alert_type} de {telemetry_data.source}")
            elif severity == "high":
                self.logger.warning(f"ALERTA ALTO: {alert_type} de {telemetry_data.source}")
        
        except Exception as e:
            self.logger.error(f"Erro ao processar dados de alertas: {str(e)}")
    
    async def _process_status_data(self, telemetry_data: NASPTelemetryData):
        """Processar dados de status"""
        try:
            status_data = telemetry_data.metrics
            status = status_data.get("status")
            
            if status == "critical":
                self.logger.critical(f"Status crítico de {telemetry_data.source}")
            elif status == "warning":
                self.logger.warning(f"Status de aviso de {telemetry_data.source}")
            else:
                self.logger.debug(f"Status saudável de {telemetry_data.source}")
        
        except Exception as e:
            self.logger.error(f"Erro ao processar dados de status: {str(e)}")
    
    # Métodos de processamento específico de métricas
    async def _process_cpu_metrics(self, cpu_usage: float, source: str):
        """Processar métricas de CPU"""
        if cpu_usage > 80:
            self.logger.warning(f"Alto uso de CPU em {source}: {cpu_usage}%")
    
    async def _process_latency_metrics(self, latency: float, source: str):
        """Processar métricas de latência"""
        if latency > 20:
            self.logger.warning(f"Alta latência em {source}: {latency}ms")
    
    async def _process_throughput_metrics(self, throughput: float, source: str):
        """Processar métricas de throughput"""
        if throughput < 100:
            self.logger.warning(f"Baixo throughput em {source}: {throughput}")
    
    # Métodos de processamento de eventos
    async def _process_slice_created_event(self, event_data: Dict[str, Any]):
        """Processar evento de criação de slice"""
        slice_id = event_data.get("slice_id")
        self.logger.info(f"Slice criado: {slice_id}")
    
    async def _process_slice_modified_event(self, event_data: Dict[str, Any]):
        """Processar evento de modificação de slice"""
        slice_id = event_data.get("slice_id")
        self.logger.info(f"Slice modificado: {slice_id}")
    
    async def _process_slice_deleted_event(self, event_data: Dict[str, Any]):
        """Processar evento de exclusão de slice"""
        slice_id = event_data.get("slice_id")
        self.logger.info(f"Slice excluído: {slice_id}")
    
    # Métodos de registro de callbacks
    def register_telemetry_callback(self, callback: Callable[[NASPTelemetryData], None]):
        """Registrar callback para dados de telemetria"""
        self.telemetry_callbacks.append(callback)
        self.logger.info("Callback de telemetria registrado")
    
    def register_metrics_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Registrar callback para dados de métricas"""
        self.metrics_callbacks.append(callback)
        self.logger.info("Callback de métricas registrado")
    
    def register_events_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Registrar callback para dados de eventos"""
        self.events_callbacks.append(callback)
        self.logger.info("Callback de eventos registrado")
    
    def register_alerts_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Registrar callback para dados de alertas"""
        self.alerts_callbacks.append(callback)
        self.logger.info("Callback de alertas registrado")
    
    # Métodos de utilidade
    async def get_telemetry_summary(self) -> Dict[str, Any]:
        """Obter resumo de dados de telemetria (simulação)"""
        return {
            "timestamp": datetime.now().isoformat(),
            "total_data_points": 150,
            "sources": ["RAN", "Transport", "Core", "NASP"],
            "data_types": ["metrics", "events", "alerts", "status"],
            "status": "active"
        }

# Função para criar interface
async def create_i03_interface(kafka_bootstrap_servers: str = "kafka:9092") -> I03_NASP_Telemetry_Interface:
    """Criar e inicializar Interface I-03"""
    interface = I03_NASP_Telemetry_Interface(kafka_bootstrap_servers)
    await interface.initialize()
    return interface

if __name__ == "__main__":
    # Teste da Interface I-03
    async def test_i03_interface():
        interface = await create_i03_interface()
        
        # Registrar callbacks de teste
        async def telemetry_callback(data):
            print(f"Telemetria recebida: {data.data_type} de {data.source}")
        
        async def metrics_callback(metrics):
            print(f"Métricas recebidas: {metrics}")
        
        interface.register_telemetry_callback(telemetry_callback)
        interface.register_metrics_callback(metrics_callback)
        
        # Iniciar consumo por 10 segundos
        consumption_task = asyncio.create_task(interface.start_consuming_telemetry())
        await asyncio.sleep(10)
        
        # Parar consumo
        await interface.shutdown()
        consumption_task.cancel()
        
        # Obter resumo
        summary = await interface.get_telemetry_summary()
        print(f"Resumo: {json.dumps(summary, indent=2)}")
    
    asyncio.run(test_i03_interface())




