#!/usr/bin/env python3
"""
Interface I-06: Decision Engine ↔ NASP API (REST)
Ativação e ajustes de slice no NASP
"""

import httpx
import asyncio
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
import json

# Configurar logging
logger = logging.getLogger(__name__)

class NASPNetworkStatus:
    """Status da rede NASP"""
    def __init__(self, status: str, resources: Dict[str, Any], slices: List[Dict[str, Any]]):
        self.status = status
        self.resources = resources
        self.slices = slices
        self.timestamp = datetime.now()

class NASPActivationResult:
    """Resultado da ativação de slice no NASP"""
    def __init__(self, success: bool, slice_id: str, message: str, details: Dict[str, Any]):
        self.success = success
        self.slice_id = slice_id
        self.message = message
        self.details = details
        self.timestamp = datetime.now()

class I06_NASP_API_Interface:
    """Interface I-06: Decision Engine ↔ NASP API (REST)"""
    
    def __init__(self, nasp_api_url: str = "http://nasp-api:8080"):
        self.nasp_api_url = nasp_api_url
        self.logger = logging.getLogger(__name__)
        self.timeout = 30.0
    
    async def activate_slice(self, slice_config: Dict[str, Any]) -> NASPActivationResult:
        """
        Ativar slice no NASP
        
        Args:
            slice_config: Configuração do slice para ativação
            
        Returns:
            NASPActivationResult: Resultado da ativação
        """
        try:
            self.logger.info(f"Ativando slice {slice_config.get('slice_id')} no NASP")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.nasp_api_url}/api/v1/slices/activate",
                    json=slice_config,
                    timeout=self.timeout
                )
                response.raise_for_status()
                result = response.json()
            
            success = result.get("success", False)
            message = result.get("message", "Ativação processada")
            details = result.get("details", {})
            
            self.logger.info(f"Slice ativado: {success} - {message}")
            
            return NASPActivationResult(
                success=success,
                slice_id=slice_config.get("slice_id", "unknown"),
                message=message,
                details=details
            )
            
        except httpx.TimeoutException:
            self.logger.error("Timeout ao ativar slice no NASP")
            return NASPActivationResult(
                success=False,
                slice_id=slice_config.get("slice_id", "unknown"),
                message="Timeout na comunicação com NASP",
                details={"error": "timeout"}
            )
        except Exception as e:
            self.logger.error(f"Erro ao ativar slice no NASP: {str(e)}")
            return NASPActivationResult(
                success=False,
                slice_id=slice_config.get("slice_id", "unknown"),
                message=f"Erro na ativação: {str(e)}",
                details={"error": str(e)}
            )
    
    async def deactivate_slice(self, slice_id: str) -> NASPActivationResult:
        """
        Desativar slice no NASP
        
        Args:
            slice_id: ID do slice para desativação
            
        Returns:
            NASPActivationResult: Resultado da desativação
        """
        try:
            self.logger.info(f"Desativando slice {slice_id} no NASP")
            
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.nasp_api_url}/api/v1/slices/{slice_id}",
                    timeout=self.timeout
                )
                response.raise_for_status()
                result = response.json()
            
            success = result.get("success", False)
            message = result.get("message", "Desativação processada")
            
            self.logger.info(f"Slice desativado: {success} - {message}")
            
            return NASPActivationResult(
                success=success,
                slice_id=slice_id,
                message=message,
                details=result.get("details", {})
            )
            
        except Exception as e:
            self.logger.error(f"Erro ao desativar slice no NASP: {str(e)}")
            return NASPActivationResult(
                success=False,
                slice_id=slice_id,
                message=f"Erro na desativação: {str(e)}",
                details={"error": str(e)}
            )
    
    async def adjust_slice(self, slice_id: str, adjustments: Dict[str, Any]) -> NASPActivationResult:
        """
        Ajustar configuração de slice no NASP
        
        Args:
            slice_id: ID do slice
            adjustments: Ajustes a serem aplicados
            
        Returns:
            NASPActivationResult: Resultado do ajuste
        """
        try:
            self.logger.info(f"Ajustando slice {slice_id} no NASP")
            
            adjustment_data = {
                "slice_id": slice_id,
                "adjustments": adjustments,
                "timestamp": datetime.now().isoformat()
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.nasp_api_url}/api/v1/slices/{slice_id}/adjust",
                    json=adjustment_data,
                    timeout=self.timeout
                )
                response.raise_for_status()
                result = response.json()
            
            success = result.get("success", False)
            message = result.get("message", "Ajuste processado")
            
            self.logger.info(f"Slice ajustado: {success} - {message}")
            
            return NASPActivationResult(
                success=success,
                slice_id=slice_id,
                message=message,
                details=result.get("details", {})
            )
            
        except Exception as e:
            self.logger.error(f"Erro ao ajustar slice no NASP: {str(e)}")
            return NASPActivationResult(
                success=False,
                slice_id=slice_id,
                message=f"Erro no ajuste: {str(e)}",
                details={"error": str(e)}
            )
    
    async def get_network_status(self) -> NASPNetworkStatus:
        """
        Obter status da rede do NASP
        
        Returns:
            NASPNetworkStatus: Status atual da rede
        """
        try:
            self.logger.info("Obtendo status da rede NASP")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.nasp_api_url}/api/v1/network/status",
                    timeout=self.timeout
                )
                response.raise_for_status()
                result = response.json()
            
            status = result.get("status", "unknown")
            resources = result.get("resources", {})
            slices = result.get("slices", [])
            
            self.logger.info(f"Status da rede: {status}")
            
            return NASPNetworkStatus(
                status=status,
                resources=resources,
                slices=slices
            )
            
        except Exception as e:
            self.logger.error(f"Erro ao obter status da rede NASP: {str(e)}")
            return NASPNetworkStatus(
                status="error",
                resources={},
                slices=[]
            )
    
    async def get_slice_status(self, slice_id: str) -> Dict[str, Any]:
        """
        Obter status de um slice específico
        
        Args:
            slice_id: ID do slice
            
        Returns:
            Dict: Status do slice
        """
        try:
            self.logger.info(f"Obtendo status do slice {slice_id}")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.nasp_api_url}/api/v1/slices/{slice_id}/status",
                    timeout=self.timeout
                )
                response.raise_for_status()
                result = response.json()
            
            self.logger.info(f"Status do slice {slice_id}: {result.get('status')}")
            return result
            
        except Exception as e:
            self.logger.error(f"Erro ao obter status do slice {slice_id}: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def get_available_resources(self) -> Dict[str, Any]:
        """
        Obter recursos disponíveis no NASP
        
        Returns:
            Dict: Recursos disponíveis
        """
        try:
            self.logger.info("Obtendo recursos disponíveis do NASP")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.nasp_api_url}/api/v1/resources/available",
                    timeout=self.timeout
                )
                response.raise_for_status()
                result = response.json()
            
            self.logger.info("Recursos disponíveis obtidos")
            return result
            
        except Exception as e:
            self.logger.error(f"Erro ao obter recursos disponíveis: {str(e)}")
            return {"error": str(e)}
    
    async def validate_slice_config(self, slice_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validar configuração de slice antes da ativação
        
        Args:
            slice_config: Configuração do slice
            
        Returns:
            Dict: Resultado da validação
        """
        try:
            self.logger.info("Validando configuração de slice no NASP")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.nasp_api_url}/api/v1/slices/validate",
                    json=slice_config,
                    timeout=self.timeout
                )
                response.raise_for_status()
                result = response.json()
            
            valid = result.get("valid", False)
            self.logger.info(f"Configuração válida: {valid}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erro ao validar configuração: {str(e)}")
            return {"valid": False, "error": str(e)}

# Cliente para operações em lote
class NASPBatchClient:
    """Cliente para operações em lote no NASP"""
    
    def __init__(self, nasp_interface: I06_NASP_API_Interface):
        self.nasp_interface = nasp_interface
        self.logger = logging.getLogger(__name__)
    
    async def activate_multiple_slices(self, slice_configs: List[Dict[str, Any]]) -> List[NASPActivationResult]:
        """
        Ativar múltiplos slices em paralelo
        
        Args:
            slice_configs: Lista de configurações de slices
            
        Returns:
            List[NASPActivationResult]: Resultados das ativações
        """
        tasks = [
            self.nasp_interface.activate_slice(config)
            for config in slice_configs
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Processar resultados e exceções
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(NASPActivationResult(
                    success=False,
                    slice_id=slice_configs[i].get("slice_id", "unknown"),
                    message=f"Erro: {str(result)}",
                    details={"error": str(result)}
                ))
            else:
                processed_results.append(result)
        
        return processed_results

if __name__ == "__main__":
    # Teste da interface
    async def test_interface():
        interface = I06_NASP_API_Interface()
        
        # Teste com dados de exemplo
        slice_config = {
            "slice_id": "test-slice-001",
            "type": "URLLC",
            "requirements": {
                "latency": 10,
                "reliability": 99.9
            }
        }
        
        # Testar ativação
        result = await interface.activate_slice(slice_config)
        print(f"Ativação: {result.success} - {result.message}")
        
        # Testar status da rede
        status = await interface.get_network_status()
        print(f"Status da rede: {status.status}")
        
        # Testar recursos disponíveis
        resources = await interface.get_available_resources()
        print(f"Recursos: {resources}")
    
    asyncio.run(test_interface())
