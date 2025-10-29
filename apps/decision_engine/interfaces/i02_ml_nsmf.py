#!/usr/bin/env python3
"""
Interface I-02: ML-NSMF → Decision Engine (gRPC)
Recebe predições e resultados XAI do ML-NSMF
"""

import grpc
import asyncio
from typing import Dict, Any, Optional
import logging
from concurrent import futures
import json

# Configurar logging
logger = logging.getLogger(__name__)

class MLPredictionRequest:
    """Requisição de predição para ML-NSMF"""
    def __init__(self, nest_template: Dict[str, Any], requirements: Dict[str, Any]):
        self.nest_template = nest_template
        self.requirements = requirements

class MLPredictionResponse:
    """Resposta de predição do ML-NSMF"""
    def __init__(self, prediction: Dict[str, Any], confidence: float, xai_explanation: Dict[str, Any]):
        self.prediction = prediction
        self.confidence = confidence
        self.xai_explanation = xai_explanation

class I02_ML_NSMF_Interface:
    """Interface I-02: ML-NSMF → Decision Engine (gRPC)"""
    
    def __init__(self, ml_nsmf_url: str = "http://ml-nsmf:8080"):
        self.ml_nsmf_url = ml_nsmf_url
        self.logger = logging.getLogger(__name__)
    
    async def get_prediction(self, nest_template: Dict[str, Any], requirements: Dict[str, Any]) -> MLPredictionResponse:
        """
        Receber predições e resultados XAI do ML-NSMF
        
        Args:
            nest_template: Template NEST validado pelo SEM-NSMF
            requirements: Requisitos de SLA da requisição
            
        Returns:
            MLPredictionResponse: Predição com explicação XAI
        """
        try:
            self.logger.info("Solicitando predição do ML-NSMF")
            
            # Preparar dados para ML-NSMF
            prediction_data = {
                "nest_template": nest_template,
                "requirements": requirements,
                "timestamp": asyncio.get_event_loop().time()
            }
            
            # Chamar ML-NSMF via HTTP (simulando gRPC)
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ml_nsmf_url}/api/v1/predict",
                    json=prediction_data,
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()
            
            # Processar resposta
            prediction = result.get("prediction", {})
            confidence = result.get("confidence", 0.5)
            xai_explanation = result.get("xai_explanation", {})
            
            self.logger.info(f"Predição recebida: confidence={confidence}")
            
            return MLPredictionResponse(
                prediction=prediction,
                confidence=confidence,
                xai_explanation=xai_explanation
            )
            
        except Exception as e:
            self.logger.error(f"Erro ao obter predição do ML-NSMF: {str(e)}")
            # Retornar predição padrão em caso de erro
            return MLPredictionResponse(
                prediction={"resource_availability": 0.5, "sla_viability": "unknown"},
                confidence=0.0,
                xai_explanation={"error": "ML-NSMF não disponível"}
            )
    
    async def get_resource_availability(self, requirements: Dict[str, Any]) -> float:
        """
        Obter disponibilidade de recursos específica
        
        Args:
            requirements: Requisitos de SLA
            
        Returns:
            float: Disponibilidade de recursos (0.0 a 1.0)
        """
        try:
            prediction = await self.get_prediction({}, requirements)
            return prediction.prediction.get("resource_availability", 0.5)
        except Exception as e:
            self.logger.error(f"Erro ao obter disponibilidade de recursos: {str(e)}")
            return 0.5
    
    async def get_sla_viability(self, requirements: Dict[str, Any]) -> str:
        """
        Obter viabilidade de SLA
        
        Args:
            requirements: Requisitos de SLA
            
        Returns:
            str: "viable", "risky", "not_viable"
        """
        try:
            prediction = await self.get_prediction({}, requirements)
            return prediction.prediction.get("sla_viability", "unknown")
        except Exception as e:
            self.logger.error(f"Erro ao obter viabilidade de SLA: {str(e)}")
            return "unknown"
    
    async def get_xai_explanation(self, nest_template: Dict[str, Any], requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Obter explicação XAI da predição
        
        Args:
            nest_template: Template NEST
            requirements: Requisitos de SLA
            
        Returns:
            Dict: Explicação XAI detalhada
        """
        try:
            prediction = await self.get_prediction(nest_template, requirements)
            return prediction.xai_explanation
        except Exception as e:
            self.logger.error(f"Erro ao obter explicação XAI: {str(e)}")
            return {"error": "Explicação XAI não disponível"}

# Servidor gRPC para receber predições (opcional)
class MLPredictionServicer:
    """Servidor gRPC para receber predições do ML-NSMF"""
    
    def __init__(self, decision_engine):
        self.decision_engine = decision_engine
        self.logger = logging.getLogger(__name__)
    
    async def ReceivePrediction(self, request, context):
        """Receber predição via gRPC"""
        try:
            # Processar predição recebida
            prediction_data = {
                "prediction": json.loads(request.prediction),
                "confidence": request.confidence,
                "xai_explanation": json.loads(request.xai_explanation)
            }
            
            self.logger.info(f"Predição recebida via gRPC: confidence={request.confidence}")
            
            # Aqui você pode processar a predição recebida
            # Por exemplo, atualizar cache ou triggerar decisão
            
            return grpc.aio.ServicerContext()
            
        except Exception as e:
            self.logger.error(f"Erro ao processar predição gRPC: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Erro interno: {str(e)}")
            return grpc.aio.ServicerContext()

def create_grpc_server(decision_engine, port: int = 50051):
    """Criar servidor gRPC para Interface I-02"""
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Adicionar servicer (implementar proto file se necessário)
    # ml_pb2_grpc.add_MLPredictionServicer_to_server(MLPredictionServicer(decision_engine), server)
    
    server.add_insecure_port(f'[::]:{port}')
    return server

if __name__ == "__main__":
    # Teste da interface
    async def test_interface():
        interface = I02_ML_NSMF_Interface()
        
        # Teste com dados de exemplo
        nest_template = {
            "slice_type": "URLLC",
            "latency": 5,
            "reliability": 99.9
        }
        
        requirements = {
            "latency": 10,
            "reliability": 99.9,
            "bandwidth": 100
        }
        
        prediction = await interface.get_prediction(nest_template, requirements)
        print(f"Predição: {prediction.prediction}")
        print(f"Confiança: {prediction.confidence}")
        print(f"XAI: {prediction.xai_explanation}")
    
    asyncio.run(test_interface())
