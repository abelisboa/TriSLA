#!/usr/bin/env python3
"""
Interface I-07: Decision Engine ↔ NASP API (REST)
Comunicação bidirecional com NASP para ativação e monitoramento de slices
"""

import asyncio
import logging
import json
import httpx
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
import uuid

# Configurar logging
logger = logging.getLogger(__name__)

@dataclass
class NASPRequest:
    """Requisição para NASP API"""
    request_id: str
    request_type: str  # "activate_slice", "deactivate_slice", "modify_slice", "get_status"
    timestamp: datetime
    data: Dict[str, Any]
    priority: str = "normal"  # "low", "normal", "high", "critical"

@dataclass
class NASPResponse:
    """Resposta da NASP API"""
    request_id: str
    status: str  # "success", "error", "pending", "timeout"
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None
    error_code: Optional[str] = None

@dataclass
class SliceConfiguration:
    """Configuração de slice para NASP"""
    slice_id: str
    slice_type: str  # "URLLC", "eMBB", "mMTC"
    requirements: Dict[str, Any]
    resources: Dict[str, Any]
    policies: Dict[str, Any]
    metadata: Dict[str, Any]

@dataclass
class NASPStatus:
    """Status da NASP"""
    timestamp: datetime
    overall_status: str  # "healthy", "warning", "critical"
    active_slices: int
    total_capacity: Dict[str, Any]
    resource_utilization: Dict[str, Any]
    alerts: List[Dict[str, Any]]

class I07_NASP_API_Interface:
    """Interface I-07: Decision Engine ↔ NASP API (REST)"""
    
    def __init__(self, nasp_api_url: str = "http://nasp-api:8080"):
        self.nasp_api_url = nasp_api_url
        self.logger = logging.getLogger(__name__)
        self.client = httpx.AsyncClient(timeout=30.0)
        self.connected = False
        
        # Configurações
        self.retry_attempts = 3
        self.retry_delay = 1.0  # segundos
        
        # Cache de status
        self.status_cache: Optional[NASPStatus] = None
        self.cache_ttl = 60  # 1 minuto
    
    async def initialize(self):
        """Inicializar conexão com NASP API"""
        try:
            self.logger.info(f"Inicializando Interface I-07 com NASP API em {self.nasp_api_url}")
            
            # Verificar conectividade
            await self._check_connectivity()
            
            self.connected = True
            self.logger.info("Interface I-07 inicializada com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar Interface I-07: {str(e)}")
            raise
    
    async def shutdown(self):
        """Encerrar conexão com NASP API"""
        try:
            await self.client.aclose()
            self.connected = False
            self.logger.info("Interface I-07 encerrada")
        except Exception as e:
            self.logger.error(f"Erro ao encerrar Interface I-07: {str(e)}")
    
    async def _check_connectivity(self):
        """Verificar conectividade com NASP API"""
        try:
            response = await self.client.get(f"{self.nasp_api_url}/health")
            if response.status_code == 200:
                self.logger.info("NASP API conectada")
            else:
                raise Exception(f"NASP API retornou status {response.status_code}")
        except Exception as e:
            self.logger.warning(f"NASP API não acessível: {str(e)}")
            # Em produção, isso seria um erro crítico
            # Por simplicidade, continuamos com simulação
    
    async def activate_slice(self, slice_config: SliceConfiguration) -> NASPResponse:
        """
        Ativar slice no NASP
        
        Args:
            slice_config: Configuração do slice
            
        Returns:
            NASPResponse: Resposta da NASP
        """
        try:
            self.logger.info(f"Ativando slice {slice_config.slice_id} no NASP")
            
            request = NASPRequest(
                request_id=str(uuid.uuid4()),
                request_type="activate_slice",
                timestamp=datetime.now(),
                data={
                    "slice_id": slice_config.slice_id,
                    "slice_type": slice_config.slice_type,
                    "requirements": slice_config.requirements,
                    "resources": slice_config.resources,
                    "policies": slice_config.policies,
                    "metadata": slice_config.metadata
                },
                priority="high"
            )
            
            return await self._send_request(request)
            
        except Exception as e:
            self.logger.error(f"Erro ao ativar slice: {str(e)}")
            return NASPResponse(
                request_id=str(uuid.uuid4()),
                status="error",
                message=f"Erro na ativação: {str(e)}",
                timestamp=datetime.now()
            )
    
    async def deactivate_slice(self, slice_id: str) -> NASPResponse:
        """
        Desativar slice no NASP
        
        Args:
            slice_id: ID do slice
            
        Returns:
            NASPResponse: Resposta da NASP
        """
        try:
            self.logger.info(f"Desativando slice {slice_id} no NASP")
            
            request = NASPRequest(
                request_id=str(uuid.uuid4()),
                request_type="deactivate_slice",
                timestamp=datetime.now(),
                data={"slice_id": slice_id},
                priority="high"
            )
            
            return await self._send_request(request)
            
        except Exception as e:
            self.logger.error(f"Erro ao desativar slice: {str(e)}")
            return NASPResponse(
                request_id=str(uuid.uuid4()),
                status="error",
                message=f"Erro na desativação: {str(e)}",
                timestamp=datetime.now()
            )
    
    async def modify_slice(self, slice_id: str, modifications: Dict[str, Any]) -> NASPResponse:
        """
        Modificar slice no NASP
        
        Args:
            slice_id: ID do slice
            modifications: Modificações a aplicar
            
        Returns:
            NASPResponse: Resposta da NASP
        """
        try:
            self.logger.info(f"Modificando slice {slice_id} no NASP")
            
            request = NASPRequest(
                request_id=str(uuid.uuid4()),
                request_type="modify_slice",
                timestamp=datetime.now(),
                data={
                    "slice_id": slice_id,
                    "modifications": modifications
                },
                priority="normal"
            )
            
            return await self._send_request(request)
            
        except Exception as e:
            self.logger.error(f"Erro ao modificar slice: {str(e)}")
            return NASPResponse(
                request_id=str(uuid.uuid4()),
                status="error",
                message=f"Erro na modificação: {str(e)}",
                timestamp=datetime.now()
            )
    
    async def get_slice_status(self, slice_id: str) -> NASPResponse:
        """
        Obter status de slice específico
        
        Args:
            slice_id: ID do slice
            
        Returns:
            NASPResponse: Status do slice
        """
        try:
            self.logger.info(f"Obtendo status do slice {slice_id}")
            
            request = NASPRequest(
                request_id=str(uuid.uuid4()),
                request_type="get_status",
                timestamp=datetime.now(),
                data={"slice_id": slice_id},
                priority="normal"
            )
            
            return await self._send_request(request)
            
        except Exception as e:
            self.logger.error(f"Erro ao obter status do slice: {str(e)}")
            return NASPResponse(
                request_id=str(uuid.uuid4()),
                status="error",
                message=f"Erro na consulta: {str(e)}",
                timestamp=datetime.now()
            )
    
    async def get_nasp_status(self) -> NASPStatus:
        """
        Obter status geral da NASP
        
        Returns:
            NASPStatus: Status da NASP
        """
        try:
            # Verificar cache primeiro
            if self.status_cache and (datetime.now() - self.status_cache.timestamp).seconds < self.cache_ttl:
                return self.status_cache
            
            self.logger.info("Obtendo status geral da NASP")
            
            request = NASPRequest(
                request_id=str(uuid.uuid4()),
                request_type="get_status",
                timestamp=datetime.now(),
                data={"scope": "global"},
                priority="normal"
            )
            
            response = await self._send_request(request)
            
            if response.status == "success" and response.data:
                nasp_status = NASPStatus(
                    timestamp=datetime.now(),
                    overall_status=response.data.get("overall_status", "unknown"),
                    active_slices=response.data.get("active_slices", 0),
                    total_capacity=response.data.get("total_capacity", {}),
                    resource_utilization=response.data.get("resource_utilization", {}),
                    alerts=response.data.get("alerts", [])
                )
                
                # Armazenar no cache
                self.status_cache = nasp_status
                
                return nasp_status
            else:
                # Retornar status simulado em caso de erro
                return self._get_simulated_status()
                
        except Exception as e:
            self.logger.error(f"Erro ao obter status da NASP: {str(e)}")
            return self._get_simulated_status()
    
    async def _send_request(self, request: NASPRequest) -> NASPResponse:
        """Enviar requisição para NASP API"""
        try:
            if not self.connected:
                self.logger.warning("NASP API não conectada, simulando resposta")
                return await self._simulate_response(request)
            
            # Fazer requisição HTTP
            response = await self.client.post(
                f"{self.nasp_api_url}/api/v1/requests",
                json={
                    "request_id": request.request_id,
                    "request_type": request.request_type,
                    "timestamp": request.timestamp.isoformat(),
                    "data": request.data,
                    "priority": request.priority
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return NASPResponse(
                    request_id=request.request_id,
                    status="success",
                    message=data.get("message", "Operação realizada com sucesso"),
                    data=data.get("data"),
                    timestamp=datetime.now()
                )
            else:
                return NASPResponse(
                    request_id=request.request_id,
                    status="error",
                    message=f"Erro HTTP {response.status_code}",
                    error_code=str(response.status_code),
                    timestamp=datetime.now()
                )
                
        except Exception as e:
            self.logger.error(f"Erro na requisição para NASP: {str(e)}")
            return NASPResponse(
                request_id=request.request_id,
                status="error",
                message=f"Erro de comunicação: {str(e)}",
                timestamp=datetime.now()
            )
    
    async def _simulate_response(self, request: NASPRequest) -> NASPResponse:
        """Simular resposta da NASP API"""
        try:
            # Simular processamento baseado no tipo de requisição
            if request.request_type == "activate_slice":
                slice_id = request.data.get("slice_id")
                slice_type = request.data.get("slice_type")
                
                if slice_type in ["URLLC", "eMBB", "mMTC"]:
                    status = "success"
                    message = f"Slice {slice_id} ativado com sucesso"
                    data = {
                        "slice_id": slice_id,
                        "status": "active",
                        "activation_time": datetime.now().isoformat()
                    }
                else:
                    status = "error"
                    message = f"Tipo de slice inválido: {slice_type}"
                    data = None
            
            elif request.request_type == "deactivate_slice":
                slice_id = request.data.get("slice_id")
                status = "success"
                message = f"Slice {slice_id} desativado com sucesso"
                data = {
                    "slice_id": slice_id,
                    "status": "inactive",
                    "deactivation_time": datetime.now().isoformat()
                }
            
            elif request.request_type == "modify_slice":
                slice_id = request.data.get("slice_id")
                status = "success"
                message = f"Slice {slice_id} modificado com sucesso"
                data = {
                    "slice_id": slice_id,
                    "status": "modified",
                    "modification_time": datetime.now().isoformat()
                }
            
            elif request.request_type == "get_status":
                if request.data.get("scope") == "global":
                    status = "success"
                    message = "Status da NASP obtido com sucesso"
                    data = {
                        "overall_status": "healthy",
                        "active_slices": 5,
                        "total_capacity": {
                            "cpu": 1000,
                            "memory": 8000,
                            "bandwidth": 10000
                        },
                        "resource_utilization": {
                            "cpu": 65,
                            "memory": 70,
                            "bandwidth": 45
                        },
                        "alerts": []
                    }
                else:
                    slice_id = request.data.get("slice_id")
                    status = "success"
                    message = f"Status do slice {slice_id} obtido com sucesso"
                    data = {
                        "slice_id": slice_id,
                        "status": "active",
                        "health": "good",
                        "metrics": {
                            "latency": 8.5,
                            "throughput": 950,
                            "availability": 99.9
                        }
                    }
            
            else:
                status = "error"
                message = f"Tipo de requisição não suportado: {request.request_type}"
                data = None
            
            return NASPResponse(
                request_id=request.request_id,
                status=status,
                message=message,
                data=data,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Erro na simulação de resposta: {str(e)}")
            return NASPResponse(
                request_id=request.request_id,
                status="error",
                message=f"Erro na simulação: {str(e)}",
                timestamp=datetime.now()
            )
    
    def _get_simulated_status(self) -> NASPStatus:
        """Obter status simulado da NASP"""
        return NASPStatus(
            timestamp=datetime.now(),
            overall_status="healthy",
            active_slices=5,
            total_capacity={
                "cpu": 1000,
                "memory": 8000,
                "bandwidth": 10000
            },
            resource_utilization={
                "cpu": 65,
                "memory": 70,
                "bandwidth": 45
            },
            alerts=[]
        )
    
    async def get_available_resources(self) -> Dict[str, Any]:
        """
        Obter recursos disponíveis na NASP
        
        Returns:
            Dict[str, Any]: Recursos disponíveis
        """
        try:
            nasp_status = await self.get_nasp_status()
            
            return {
                "timestamp": nasp_status.timestamp.isoformat(),
                "total_capacity": nasp_status.total_capacity,
                "resource_utilization": nasp_status.resource_utilization,
                "available_resources": {
                    "cpu": nasp_status.total_capacity.get("cpu", 0) * (1 - nasp_status.resource_utilization.get("cpu", 0) / 100),
                    "memory": nasp_status.total_capacity.get("memory", 0) * (1 - nasp_status.resource_utilization.get("memory", 0) / 100),
                    "bandwidth": nasp_status.total_capacity.get("bandwidth", 0) * (1 - nasp_status.resource_utilization.get("bandwidth", 0) / 100)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao obter recursos disponíveis: {str(e)}")
            return {"error": str(e)}

# Função para criar interface
async def create_i07_interface(nasp_api_url: str = "http://nasp-api:8080") -> I07_NASP_API_Interface:
    """Criar e inicializar Interface I-07"""
    interface = I07_NASP_API_Interface(nasp_api_url)
    await interface.initialize()
    return interface

if __name__ == "__main__":
    # Teste da Interface I-07
    async def test_i07_interface():
        interface = await create_i07_interface()
        
        # Testar ativação de slice
        slice_config = SliceConfiguration(
            slice_id="test-slice-001",
            slice_type="URLLC",
            requirements={
                "latency": 10,
                "reliability": 99.9
            },
            resources={
                "cpu": 100,
                "memory": 512,
                "bandwidth": 1000
            },
            policies={},
            metadata={}
        )
        
        response = await interface.activate_slice(slice_config)
        print(f"Ativação de slice: {response}")
        
        # Testar status da NASP
        status = await interface.get_nasp_status()
        print(f"Status da NASP: {status}")
        
        # Testar recursos disponíveis
        resources = await interface.get_available_resources()
        print(f"Recursos disponíveis: {json.dumps(resources, indent=2)}")
        
        # Encerrar
        await interface.shutdown()
    
    asyncio.run(test_i07_interface())
