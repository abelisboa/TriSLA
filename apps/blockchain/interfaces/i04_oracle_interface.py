#!/usr/bin/env python3
"""
Interface I-04: BC-NSSMF ↔ Oracles (REST)
Comunicação com oráculos externos para dados e eventos
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
class OracleData:
    """Dados recebidos de oráculo externo"""
    data_id: str
    oracle_id: str
    data_type: str  # "network_status", "market_data", "external_events"
    timestamp: datetime
    data: Dict[str, Any]
    confidence: float
    source: str

@dataclass
class OracleEvent:
    """Evento publicado para oráculos externos"""
    event_id: str
    event_type: str  # "contract_created", "sla_violation", "payment_processed"
    timestamp: datetime
    data: Dict[str, Any]
    target_oracles: List[str]

@dataclass
class OracleResponse:
    """Resposta de oráculo externo"""
    request_id: str
    oracle_id: str
    status: str  # "success", "error", "timeout"
    data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    timestamp: Optional[datetime] = None

class I04_Oracle_Interface:
    """Interface I-04: BC-NSSMF ↔ Oracles (REST)"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # Configurações de oráculos
        self.oracles = {
            "network_oracle": {
                "url": "http://network-oracle:8080",
                "enabled": True,
                "data_types": ["network_status", "topology", "performance"]
            },
            "market_oracle": {
                "url": "http://market-oracle:8080",
                "enabled": True,
                "data_types": ["pricing", "demand", "supply"]
            },
            "external_oracle": {
                "url": "http://external-oracle:8080",
                "enabled": True,
                "data_types": ["weather", "events", "regulations"]
            }
        }
        
        # Cache de dados
        self.data_cache: Dict[str, OracleData] = {}
        self.cache_ttl = 300  # 5 minutos
    
    async def initialize(self):
        """Inicializar interface com oráculos"""
        try:
            self.logger.info("Inicializando Interface I-04...")
            
            # Verificar conectividade com oráculos
            await self._check_oracle_connectivity()
            
            self.logger.info("Interface I-04 inicializada com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar Interface I-04: {str(e)}")
            raise
    
    async def shutdown(self):
        """Encerrar interface"""
        try:
            await self.client.aclose()
            self.logger.info("Interface I-04 encerrada")
        except Exception as e:
            self.logger.error(f"Erro ao encerrar Interface I-04: {str(e)}")
    
    async def _check_oracle_connectivity(self):
        """Verificar conectividade com oráculos"""
        for oracle_id, config in self.oracles.items():
            if not config["enabled"]:
                continue
            
            try:
                response = await self.client.get(f"{config['url']}/health")
                if response.status_code == 200:
                    self.logger.info(f"Oráculo {oracle_id} conectado")
                else:
                    self.logger.warning(f"Oráculo {oracle_id} retornou status {response.status_code}")
            except Exception as e:
                self.logger.warning(f"Oráculo {oracle_id} não acessível: {str(e)}")
    
    async def get_network_events(self) -> List[OracleData]:
        """
        Obter eventos de rede de oráculos externos
        
        Returns:
            List[OracleData]: Lista de eventos de rede
        """
        try:
            self.logger.info("Obtendo eventos de rede de oráculos...")
            
            events = []
            
            # Obter dados do oráculo de rede
            network_data = await self._get_oracle_data("network_oracle", "network_status")
            if network_data:
                events.append(network_data)
            
            # Obter dados do oráculo externo
            external_data = await self._get_oracle_data("external_oracle", "events")
            if external_data:
                events.append(external_data)
            
            self.logger.info(f"Obtidos {len(events)} eventos de rede")
            return events
            
        except Exception as e:
            self.logger.error(f"Erro ao obter eventos de rede: {str(e)}")
            return []
    
    async def get_market_data(self) -> List[OracleData]:
        """
        Obter dados de mercado de oráculos
        
        Returns:
            List[OracleData]: Lista de dados de mercado
        """
        try:
            self.logger.info("Obtendo dados de mercado de oráculos...")
            
            market_data = []
            
            # Obter dados de preços
            pricing_data = await self._get_oracle_data("market_oracle", "pricing")
            if pricing_data:
                market_data.append(pricing_data)
            
            # Obter dados de demanda
            demand_data = await self._get_oracle_data("market_oracle", "demand")
            if demand_data:
                market_data.append(demand_data)
            
            # Obter dados de oferta
            supply_data = await self._get_oracle_data("market_oracle", "supply")
            if supply_data:
                market_data.append(supply_data)
            
            self.logger.info(f"Obtidos {len(market_data)} dados de mercado")
            return market_data
            
        except Exception as e:
            self.logger.error(f"Erro ao obter dados de mercado: {str(e)}")
            return []
    
    async def get_external_data(self, data_type: str) -> List[OracleData]:
        """
        Obter dados externos de oráculos
        
        Args:
            data_type: Tipo de dados a obter
            
        Returns:
            List[OracleData]: Lista de dados externos
        """
        try:
            self.logger.info(f"Obtendo dados externos do tipo {data_type}...")
            
            external_data = []
            
            # Obter dados do oráculo externo
            data = await self._get_oracle_data("external_oracle", data_type)
            if data:
                external_data.append(data)
            
            self.logger.info(f"Obtidos {len(external_data)} dados externos")
            return external_data
            
        except Exception as e:
            self.logger.error(f"Erro ao obter dados externos: {str(e)}")
            return []
    
    async def _get_oracle_data(self, oracle_id: str, data_type: str) -> Optional[OracleData]:
        """Obter dados de oráculo específico"""
        try:
            config = self.oracles.get(oracle_id)
            if not config or not config["enabled"]:
                return None
            
            # Verificar cache primeiro
            cache_key = f"{oracle_id}_{data_type}"
            if cache_key in self.data_cache:
                cached_data = self.data_cache[cache_key]
                if (datetime.now() - cached_data.timestamp).seconds < self.cache_ttl:
                    return cached_data
            
            # Fazer requisição para oráculo
            response = await self.client.get(
                f"{config['url']}/api/v1/data/{data_type}",
                params={"format": "json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                oracle_data = OracleData(
                    data_id=str(uuid.uuid4()),
                    oracle_id=oracle_id,
                    data_type=data_type,
                    timestamp=datetime.now(),
                    data=data,
                    confidence=data.get("confidence", 0.8),
                    source=oracle_id
                )
                
                # Armazenar no cache
                self.data_cache[cache_key] = oracle_data
                
                return oracle_data
            else:
                self.logger.warning(f"Oráculo {oracle_id} retornou status {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Erro ao obter dados do oráculo {oracle_id}: {str(e)}")
            return None
    
    async def publish_contract_event(self, event: OracleEvent) -> List[OracleResponse]:
        """
        Publicar evento de contrato para oráculos
        
        Args:
            event: Evento a ser publicado
            
        Returns:
            List[OracleResponse]: Respostas dos oráculos
        """
        try:
            self.logger.info(f"Publicando evento {event.event_type} para oráculos...")
            
            responses = []
            
            for oracle_id in event.target_oracles:
                config = self.oracles.get(oracle_id)
                if not config or not config["enabled"]:
                    continue
                
                try:
                    response = await self.client.post(
                        f"{config['url']}/api/v1/events",
                        json={
                            "event_id": event.event_id,
                            "event_type": event.event_type,
                            "timestamp": event.timestamp.isoformat(),
                            "data": event.data
                        }
                    )
                    
                    if response.status_code == 200:
                        oracle_response = OracleResponse(
                            request_id=str(uuid.uuid4()),
                            oracle_id=oracle_id,
                            status="success",
                            data=response.json(),
                            timestamp=datetime.now()
                        )
                    else:
                        oracle_response = OracleResponse(
                            request_id=str(uuid.uuid4()),
                            oracle_id=oracle_id,
                            status="error",
                            error_message=f"Status {response.status_code}",
                            timestamp=datetime.now()
                        )
                    
                    responses.append(oracle_response)
                    
                except Exception as e:
                    oracle_response = OracleResponse(
                        request_id=str(uuid.uuid4()),
                        oracle_id=oracle_id,
                        status="error",
                        error_message=str(e),
                        timestamp=datetime.now()
                    )
                    responses.append(oracle_response)
            
            self.logger.info(f"Publicado evento para {len(responses)} oráculos")
            return responses
            
        except Exception as e:
            self.logger.error(f"Erro ao publicar evento de contrato: {str(e)}")
            return []
    
    async def publish_sla_violation(self, violation_data: Dict[str, Any]) -> List[OracleResponse]:
        """
        Publicar violação de SLA para oráculos
        
        Args:
            violation_data: Dados da violação
            
        Returns:
            List[OracleResponse]: Respostas dos oráculos
        """
        try:
            event = OracleEvent(
                event_id=str(uuid.uuid4()),
                event_type="sla_violation",
                timestamp=datetime.now(),
                data=violation_data,
                target_oracles=["network_oracle", "market_oracle"]
            )
            
            return await self.publish_contract_event(event)
            
        except Exception as e:
            self.logger.error(f"Erro ao publicar violação de SLA: {str(e)}")
            return []
    
    async def publish_payment_event(self, payment_data: Dict[str, Any]) -> List[OracleResponse]:
        """
        Publicar evento de pagamento para oráculos
        
        Args:
            payment_data: Dados do pagamento
            
        Returns:
            List[OracleResponse]: Respostas dos oráculos
        """
        try:
            event = OracleEvent(
                event_id=str(uuid.uuid4()),
                event_type="payment_processed",
                timestamp=datetime.now(),
                data=payment_data,
                target_oracles=["market_oracle", "external_oracle"]
            )
            
            return await self.publish_contract_event(event)
            
        except Exception as e:
            self.logger.error(f"Erro ao publicar evento de pagamento: {str(e)}")
            return []
    
    async def get_oracle_status(self) -> Dict[str, Any]:
        """
        Obter status de todos os oráculos
        
        Returns:
            Dict[str, Any]: Status dos oráculos
        """
        try:
            status = {
                "timestamp": datetime.now().isoformat(),
                "oracles": {},
                "total_oracles": len(self.oracles),
                "active_oracles": 0,
                "cached_data": len(self.data_cache)
            }
            
            for oracle_id, config in self.oracles.items():
                oracle_status = {
                    "enabled": config["enabled"],
                    "url": config["url"],
                    "data_types": config["data_types"],
                    "status": "unknown"
                }
                
                if config["enabled"]:
                    try:
                        response = await self.client.get(f"{config['url']}/health", timeout=5.0)
                        if response.status_code == 200:
                            oracle_status["status"] = "healthy"
                            status["active_oracles"] += 1
                        else:
                            oracle_status["status"] = "unhealthy"
                    except Exception:
                        oracle_status["status"] = "unreachable"
                
                status["oracles"][oracle_id] = oracle_status
            
            return status
            
        except Exception as e:
            self.logger.error(f"Erro ao obter status dos oráculos: {str(e)}")
            return {"error": str(e)}
    
    async def clear_cache(self):
        """Limpar cache de dados"""
        try:
            self.data_cache.clear()
            self.logger.info("Cache de dados limpo")
        except Exception as e:
            self.logger.error(f"Erro ao limpar cache: {str(e)}")

# Função para criar interface
async def create_i04_interface() -> I04_Oracle_Interface:
    """Criar e inicializar Interface I-04"""
    interface = I04_Oracle_Interface()
    await interface.initialize()
    return interface

if __name__ == "__main__":
    # Teste da Interface I-04
    async def test_i04_interface():
        interface = await create_i04_interface()
        
        # Testar obtenção de eventos de rede
        network_events = await interface.get_network_events()
        print(f"Eventos de rede: {len(network_events)}")
        
        # Testar obtenção de dados de mercado
        market_data = await interface.get_market_data()
        print(f"Dados de mercado: {len(market_data)}")
        
        # Testar publicação de evento
        violation_data = {
            "slice_id": "slice-001",
            "violation_type": "latency",
            "threshold": 10,
            "actual_value": 15,
            "severity": "critical"
        }
        
        responses = await interface.publish_sla_violation(violation_data)
        print(f"Respostas de oráculos: {len(responses)}")
        
        # Obter status
        status = await interface.get_oracle_status()
        print(f"Status dos oráculos: {json.dumps(status, indent=2)}")
        
        # Encerrar
        await interface.shutdown()
    
    asyncio.run(test_i04_interface())




