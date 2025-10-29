#!/usr/bin/env python3
"""
Interface I-01: SEM-NSMF → ML-NSMF (gRPC)
Envia templates NEST validados para ML-NSMF
"""

import grpc
import asyncio
import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from concurrent import futures
import uuid

# Configurar logging
logger = logging.getLogger(__name__)

@dataclass
class NESTTemplate:
    """Template NEST para envio ao ML-NSMF"""
    template_id: str
    slice_type: str  # "URLLC", "eMBB", "mMTC"
    requirements: Dict[str, Any]
    semantic_analysis: Dict[str, Any]
    validation_status: str  # "validated", "pending", "failed"
    timestamp: datetime
    confidence: float
    metadata: Dict[str, Any]

@dataclass
class NESTResponse:
    """Resposta do ML-NSMF para template NEST"""
    template_id: str
    status: str  # "accepted", "rejected", "pending"
    message: str
    prediction_id: Optional[str] = None
    confidence: Optional[float] = None
    timestamp: Optional[datetime] = None

class I01_ML_NSMF_Interface:
    """Interface I-01: SEM-NSMF → ML-NSMF (gRPC)"""
    
    def __init__(self, ml_nsmf_url: str = "ml-nsmf:50051"):
        self.ml_nsmf_url = ml_nsmf_url
        self.logger = logging.getLogger(__name__)
        self.channel = None
        self.stub = None
        self.connected = False
    
    async def initialize(self):
        """Inicializar conexão gRPC com ML-NSMF"""
        try:
            # Em produção, usar gRPC real
            # self.channel = grpc.aio.insecure_channel(self.ml_nsmf_url)
            # self.stub = nest_pb2_grpc.NESTServicerStub(self.channel)
            
            self.connected = True
            self.logger.info(f"Interface I-01 inicializada com ML-NSMF em {self.ml_nsmf_url}")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar Interface I-01: {str(e)}")
            raise
    
    async def shutdown(self):
        """Encerrar conexão gRPC"""
        try:
            if self.channel:
                await self.channel.close()
            self.connected = False
            self.logger.info("Interface I-01 encerrada")
        except Exception as e:
            self.logger.error(f"Erro ao encerrar Interface I-01: {str(e)}")
    
    async def send_nest_template(self, template: NESTTemplate) -> NESTResponse:
        """
        Enviar template NEST validado para ML-NSMF
        
        Args:
            template: Template NEST validado pelo SEM-NSMF
            
        Returns:
            NESTResponse: Resposta do ML-NSMF
        """
        try:
            if not self.connected:
                self.logger.warning("Interface I-01 não conectada, simulando envio")
                return await self._simulate_nest_response(template)
            
            self.logger.info(f"Enviando template NEST {template.template_id} para ML-NSMF")
            
            # Em produção, usar gRPC real:
            # request = nest_pb2.NESTRequest(
            #     template_id=template.template_id,
            #     slice_type=template.slice_type,
            #     requirements=json.dumps(template.requirements),
            #     semantic_analysis=json.dumps(template.semantic_analysis),
            #     confidence=template.confidence
            # )
            # response = await self.stub.SendNESTTemplate(request)
            
            # Simular resposta (em produção, usar resposta real do gRPC)
            return await self._simulate_nest_response(template)
            
        except Exception as e:
            self.logger.error(f"Erro ao enviar template NEST: {str(e)}")
            return NESTResponse(
                template_id=template.template_id,
                status="rejected",
                message=f"Erro na comunicação: {str(e)}",
                timestamp=datetime.now()
            )
    
    async def _simulate_nest_response(self, template: NESTTemplate) -> NESTResponse:
        """Simular resposta do ML-NSMF (em produção, usar gRPC real)"""
        try:
            # Simular processamento baseado no tipo de slice
            if template.slice_type == "URLLC":
                if template.requirements.get("latency", 0) <= 10:
                    status = "accepted"
                    confidence = 0.95
                    message = "Template URLLC aceito - latência adequada"
                else:
                    status = "rejected"
                    confidence = 0.1
                    message = "Template URLLC rejeitado - latência inadequada"
            
            elif template.slice_type == "eMBB":
                if template.requirements.get("bandwidth", 0) >= 1000:
                    status = "accepted"
                    confidence = 0.90
                    message = "Template eMBB aceito - largura de banda adequada"
                else:
                    status = "rejected"
                    confidence = 0.2
                    message = "Template eMBB rejeitado - largura de banda inadequada"
            
            elif template.slice_type == "mMTC":
                if template.requirements.get("connections", 0) >= 10000:
                    status = "accepted"
                    confidence = 0.85
                    message = "Template mMTC aceito - densidade de conexões adequada"
                else:
                    status = "rejected"
                    confidence = 0.3
                    message = "Template mMTC rejeitado - densidade de conexões inadequada"
            
            else:
                status = "rejected"
                confidence = 0.0
                message = "Tipo de slice não reconhecido"
            
            # Gerar ID de predição se aceito
            prediction_id = str(uuid.uuid4()) if status == "accepted" else None
            
            return NESTResponse(
                template_id=template.template_id,
                status=status,
                message=message,
                prediction_id=prediction_id,
                confidence=confidence,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Erro na simulação de resposta: {str(e)}")
            return NESTResponse(
                template_id=template.template_id,
                status="rejected",
                message=f"Erro na simulação: {str(e)}",
                timestamp=datetime.now()
            )
    
    async def send_batch_templates(self, templates: List[NESTTemplate]) -> List[NESTResponse]:
        """
        Enviar múltiplos templates NEST em lote
        
        Args:
            templates: Lista de templates NEST
            
        Returns:
            List[NESTResponse]: Lista de respostas do ML-NSMF
        """
        try:
            self.logger.info(f"Enviando {len(templates)} templates NEST em lote")
            
            # Processar templates em paralelo
            tasks = [self.send_nest_template(template) for template in templates]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Processar respostas e exceções
            processed_responses = []
            for i, response in enumerate(responses):
                if isinstance(response, Exception):
                    processed_responses.append(NESTResponse(
                        template_id=templates[i].template_id,
                        status="rejected",
                        message=f"Erro no processamento: {str(response)}",
                        timestamp=datetime.now()
                    ))
                else:
                    processed_responses.append(response)
            
            self.logger.info(f"Processados {len(processed_responses)} templates NEST")
            return processed_responses
            
        except Exception as e:
            self.logger.error(f"Erro ao enviar templates em lote: {str(e)}")
            return []
    
    async def get_template_status(self, template_id: str) -> Optional[NESTResponse]:
        """
        Obter status de template específico
        
        Args:
            template_id: ID do template
            
        Returns:
            NESTResponse: Status do template ou None se não encontrado
        """
        try:
            # Em produção, implementar consulta de status via gRPC
            self.logger.info(f"Consultando status do template {template_id}")
            
            # Simular consulta de status
            return NESTResponse(
                template_id=template_id,
                status="accepted",
                message="Template processado com sucesso",
                prediction_id=str(uuid.uuid4()),
                confidence=0.9,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Erro ao consultar status do template: {str(e)}")
            return None
    
    async def validate_template(self, template: NESTTemplate) -> bool:
        """
        Validar template antes do envio
        
        Args:
            template: Template NEST para validação
            
        Returns:
            bool: True se válido, False caso contrário
        """
        try:
            # Validar campos obrigatórios
            if not template.template_id:
                self.logger.warning("Template ID não fornecido")
                return False
            
            if not template.slice_type:
                self.logger.warning("Tipo de slice não fornecido")
                return False
            
            if not template.requirements:
                self.logger.warning("Requisitos não fornecidos")
                return False
            
            if template.confidence < 0.0 or template.confidence > 1.0:
                self.logger.warning("Confiança deve estar entre 0.0 e 1.0")
                return False
            
            # Validar tipo de slice
            valid_slice_types = ["URLLC", "eMBB", "mMTC"]
            if template.slice_type not in valid_slice_types:
                self.logger.warning(f"Tipo de slice inválido: {template.slice_type}")
                return False
            
            self.logger.info(f"Template {template.template_id} validado com sucesso")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro na validação do template: {str(e)}")
            return False

# Servidor gRPC para receber templates (opcional)
class NESTServicer:
    """Servidor gRPC para receber templates NEST"""
    
    def __init__(self, semantic_processor):
        self.semantic_processor = semantic_processor
        self.logger = logging.getLogger(__name__)
    
    async def SendNESTTemplate(self, request, context):
        """Processar template NEST recebido via gRPC"""
        try:
            # Processar template recebido
            template = NESTTemplate(
                template_id=request.template_id,
                slice_type=request.slice_type,
                requirements=json.loads(request.requirements),
                semantic_analysis=json.loads(request.semantic_analysis),
                validation_status="received",
                timestamp=datetime.now(),
                confidence=request.confidence,
                metadata={}
            )
            
            self.logger.info(f"Template NEST recebido: {template.template_id}")
            
            # Processar template (implementar lógica específica)
            # result = await self.semantic_processor.process_template(template)
            
            # Retornar resposta (implementar proto response)
            # return nest_pb2.NESTResponse(status="accepted", message="Template processado")
            
        except Exception as e:
            self.logger.error(f"Erro ao processar template NEST: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Erro interno: {str(e)}")

def create_grpc_server(semantic_processor, port: int = 50051):
    """Criar servidor gRPC para Interface I-01"""
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Adicionar servicer (implementar proto file se necessário)
    # nest_pb2_grpc.add_NESTServicer_to_server(NESTServicer(semantic_processor), server)
    
    server.add_insecure_port(f'[::]:{port}')
    return server

# Função para criar interface
async def create_i01_interface(ml_nsmf_url: str = "ml-nsmf:50051") -> I01_ML_NSMF_Interface:
    """Criar e inicializar Interface I-01"""
    interface = I01_ML_NSMF_Interface(ml_nsmf_url)
    await interface.initialize()
    return interface

if __name__ == "__main__":
    # Teste da Interface I-01
    async def test_i01_interface():
        interface = await create_i01_interface()
        
        # Criar template de teste
        template = NESTTemplate(
            template_id="test-template-001",
            slice_type="URLLC",
            requirements={
                "latency": 5,
                "reliability": 99.9,
                "bandwidth": 100
            },
            semantic_analysis={
                "confidence": 0.95,
                "analysis": "Análise semântica completa"
            },
            validation_status="validated",
            timestamp=datetime.now(),
            confidence=0.95,
            metadata={"source": "test"}
        )
        
        # Enviar template
        response = await interface.send_nest_template(template)
        print(f"Resposta ML-NSMF: {response}")
        
        # Encerrar
        await interface.shutdown()
    
    asyncio.run(test_i01_interface())
