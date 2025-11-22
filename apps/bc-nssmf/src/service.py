"""
BCService - BC-NSSMF
Serviço para interação com Smart Contracts Solidity em Ethereum Permissionado (GoQuorum/Besu)

Conforme dissertação TriSLA:
- Execução descentralizada dos contratos
- Rastreabilidade das cláusulas
- Infraestrutura Ethereum permissionada (GoQuorum/Besu)
"""

import json
import os
from typing import Dict, Any, Optional, List
from web3 import Web3
from eth_account import Account
from opentelemetry import trace

from config import BCConfig

tracer = trace.get_tracer(__name__)


class BCService:
    """
    Serviço para interação com Smart Contracts Solidity em Ethereum Permissionado (GoQuorum/Besu)
    
    IMPORTANTE: Todas as operações são executadas na blockchain real, nunca em simulação Python.
    A fonte de verdade sobre o estado de um SLA é o contrato Solidity em GoQuorum/Besu.
    """
    
    def __init__(self, config: Optional[BCConfig] = None):
        """
        Inicializa BCService conectando à rede Ethereum permissionada (GoQuorum/Besu)
        
        Args:
            config: Configuração BC (padrão: BCConfig())
        """
        self.config = config or BCConfig()
        
        # Conectar ao nó Besu/GoQuorum
        self.w3 = Web3(Web3.HTTPProvider(self.config.rpc_url))
        
        if not self.w3.is_connected():
            raise RuntimeError(
                f"❌ Não conectado ao Besu RPC em {self.config.rpc_url}. "
                f"Verifique se o nó Ethereum permissionado (GoQuorum/Besu) está rodando."
            )
        
        print(f"✅ Conectado ao Ethereum permissionado (GoQuorum/Besu) em {self.config.rpc_url}")
        print(f"   Chain ID: {self.config.chain_id}")
        print(f"   Blockchain: {self.config.blockchain_type}")
        
        # Carregar contrato deployado
        if not os.path.exists(self.config.contract_info_path):
            raise FileNotFoundError(
                f"❌ Arquivo de contrato não encontrado: {self.config.contract_info_path}. "
                f"Execute deploy_contracts.py primeiro para fazer deploy do contrato Solidity."
            )
        
        with open(self.config.contract_info_path, "r", encoding="utf-8") as f:
            contract_data = json.load(f)
        
        self.contract_address = contract_data["address"]
        self.abi = contract_data["abi"]
        
        # Criar instância do contrato
        self.contract = self.w3.eth.contract(
            address=self.contract_address,
            abi=self.abi
        )
        
        print(f"✅ Contrato Solidity carregado: {self.contract_address}")
        
        # Configurar conta para assinar transações
        self.account = self._setup_account()
        
        print(f"✅ Conta configurada: {self.account.address}")
    
    def _setup_account(self) -> Account:
        """
        Configura conta Ethereum para assinar transações
        
        Returns:
            Account configurada
        """
        if self.config.private_key:
            # Usar chave privada configurada
            account = Account.from_key(self.config.private_key)
            print(f"   Usando chave privada configurada (modo produção)")
        else:
            # Modo dev: usar primeira conta disponível (pré-financiada no Besu dev)
            accounts = self.w3.eth.accounts
            if not accounts:
                raise RuntimeError(
                    "❌ Nenhuma conta disponível no nó Besu. "
                    "Configure BESU_PRIVATE_KEY ou use modo dev do Besu."
                )
            account = Account.from_key(self.w3.eth.accounts[0])
            print(f"   Usando conta dev padrão (modo desenvolvimento)")
        
        # Verificar saldo
        balance = self.w3.eth.get_balance(account.address)
        balance_eth = self.w3.from_wei(balance, "ether")
        print(f"   Saldo: {balance_eth} ETH")
        
        if balance < self.w3.to_wei("0.01", "ether"):
            print(f"⚠️ Saldo baixo: {balance_eth} ETH. Pode não ser suficiente para transações.")
        
        return account
    
    def register_sla(
        self,
        customer: str,
        service_name: str,
        sla_hash: str,
        slos: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Registra SLA no contrato Solidity em Ethereum permissionado (GoQuorum/Besu)
        
        IMPORTANTE: Esta operação é executada na blockchain real, não em simulação.
        
        Args:
            customer: ID do tenant/cliente
            service_name: Nome do serviço (ex: nest_id)
            sla_hash: Hash do SLA (bytes32)
            slos: Lista de SLOs (conforme struct SLO do contrato)
        
        Returns:
            Receipt da transação blockchain com transaction_hash
        """
        with tracer.start_as_current_span("register_sla_blockchain") as span:
            span.set_attribute("blockchain.type", "Ethereum Permissionado (GoQuorum/Besu)")
            span.set_attribute("blockchain.contract_address", self.contract_address)
            span.set_attribute("sla.customer", customer)
            span.set_attribute("sla.service_name", service_name)
            
            try:
                # Converter sla_hash para bytes32 (formato esperado pelo web3)
                if isinstance(sla_hash, str):
                    # Se é string hex, converter para bytes32
                    if sla_hash.startswith("0x"):
                        sla_hash_hex = sla_hash[2:]
                    else:
                        sla_hash_hex = sla_hash
                    # Garantir que tem 64 caracteres (32 bytes)
                    if len(sla_hash_hex) < 64:
                        sla_hash_hex = sla_hash_hex.ljust(64, '0')
                    elif len(sla_hash_hex) > 64:
                        sla_hash_hex = sla_hash_hex[:64]
                    # Web3 aceita hex string diretamente para bytes32
                    sla_hash_bytes32 = "0x" + sla_hash_hex
                elif isinstance(sla_hash, bytes):
                    # Se já é bytes, converter para hex string
                    sla_hash_bytes32 = self.w3.to_hex(sla_hash)
                    # Garantir que tem 66 caracteres (0x + 64 hex)
                    if len(sla_hash_bytes32) < 66:
                        sla_hash_bytes32 = sla_hash_bytes32[:2] + sla_hash_bytes32[2:].ljust(64, '0')
                    elif len(sla_hash_bytes32) > 66:
                        sla_hash_bytes32 = sla_hash_bytes32[:66]
                else:
                    # Tentar converter para hex string
                    sla_hash_bytes32 = self.w3.to_hex(self.w3.to_bytes(32, byteorder='big', value=int(sla_hash)))
                
                # Preparar SLOs para o contrato
                slos_formatted = [
                    (slo["name"], int(slo["value"]), int(slo["threshold"]))
                    for slo in slos
                ]
                
                # Construir transação
                nonce = self.w3.eth.get_transaction_count(self.account.address)
                
                tx = self.contract.functions.registerSLA(
                    customer,
                    service_name,
                    sla_hash_bytes32,
                    slos_formatted
                ).build_transaction({
                    "from": self.account.address,
                    "chainId": self.config.chain_id,
                    "nonce": nonce,
                    "gas": self.config.gas_limit,
                    "gasPrice": self.config.gas_price
                })
                
                # Assinar transação
                signed_tx = self.account.sign_transaction(tx)
                
                # Enviar transação para blockchain
                tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                
                print(f"🔄 Transação enviada: {tx_hash.hex()}")
                span.set_attribute("blockchain.tx_hash", tx_hash.hex())
                
                # Aguardar confirmação
                receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
                
                # Extrair SLA ID do evento
                sla_id = None
                if receipt.logs:
                    # Buscar evento SLARequested
                    for log in receipt.logs:
                        try:
                            event = self.contract.events.SLARequested().process_log(log)
                            sla_id = event.args.slaId
                            break
                        except:
                            continue
                
                print(f"✅ SLA registrado na blockchain: ID={sla_id}, TX={receipt.transactionHash.hex()}")
                
                span.set_attribute("blockchain.sla_id", sla_id)
                span.set_attribute("blockchain.block_number", receipt.blockNumber)
                span.set_attribute("blockchain.status", "success")
                
                return {
                    "transaction_hash": receipt.transactionHash.hex(),
                    "sla_id": sla_id,
                    "block_number": receipt.blockNumber,
                    "status": "success",
                    "contract_address": self.contract_address
                }
                
            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                print(f"❌ Erro ao registrar SLA na blockchain: {e}")
                raise
    
    def update_sla_status(self, sla_id: int, status: int) -> Dict[str, Any]:
        """
        Atualiza status do SLA no contrato Solidity
        
        IMPORTANTE: Esta operação é executada na blockchain real.
        
        Args:
            sla_id: ID do SLA (uint256)
            status: Novo status (0=REQUESTED, 1=APPROVED, 2=REJECTED, 3=ACTIVE, 4=COMPLETED)
        
        Returns:
            Receipt da transação
        """
        with tracer.start_as_current_span("update_sla_status_blockchain") as span:
            span.set_attribute("blockchain.type", "Ethereum Permissionado (GoQuorum/Besu)")
            span.set_attribute("sla.id", sla_id)
            span.set_attribute("sla.status", status)
            
            try:
                nonce = self.w3.eth.get_transaction_count(self.account.address)
                
                tx = self.contract.functions.updateSLAStatus(
                    sla_id,
                    status
                ).build_transaction({
                    "from": self.account.address,
                    "chainId": self.config.chain_id,
                    "nonce": nonce,
                    "gas": self.config.gas_limit,
                    "gasPrice": self.config.gas_price
                })
                
                signed_tx = self.account.sign_transaction(tx)
                tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                
                receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
                
                print(f"✅ Status do SLA atualizado: ID={sla_id}, TX={receipt.transactionHash.hex()}")
                
                span.set_attribute("blockchain.tx_hash", receipt.transactionHash.hex())
                span.set_attribute("blockchain.block_number", receipt.blockNumber)
                
                return {
                    "transaction_hash": receipt.transactionHash.hex(),
                    "sla_id": sla_id,
                    "block_number": receipt.blockNumber,
                    "status": "success"
                }
                
            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                print(f"❌ Erro ao atualizar status do SLA: {e}")
                raise
    
    def get_sla(self, sla_id: int) -> Dict[str, Any]:
        """
        Obtém informações do SLA do contrato Solidity (chamada read-only)
        
        Args:
            sla_id: ID do SLA
        
        Returns:
            Dicionário com informações do SLA
        """
        with tracer.start_as_current_span("get_sla_blockchain") as span:
            span.set_attribute("sla.id", sla_id)
            
            try:
                # Chamada read-only (não gera transação)
                result = self.contract.functions.getSLA(sla_id).call()
                
                # Converter resultado para dicionário
                sla_info = {
                    "sla_id": sla_id,
                    "customer": result[0],
                    "service_name": result[1],
                    "status": result[2],  # Enum SLAStatus
                    "created_at": result[3],
                    "updated_at": result[4],
                    "contract_address": self.contract_address
                }
                
                span.set_attribute("sla.status", result[2])
                
                return sla_info
                
            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                print(f"❌ Erro ao obter SLA: {e}")
                raise
    
    def get_sla_events(self, sla_id: int, from_block: int = 0) -> List[Dict[str, Any]]:
        """
        Obtém eventos do SLA (SLARequested, SLAUpdated, SLACompleted)
        
        Args:
            sla_id: ID do SLA
            from_block: Bloco inicial para buscar eventos
        
        Returns:
            Lista de eventos
        """
        with tracer.start_as_current_span("get_sla_events") as span:
            span.set_attribute("sla.id", sla_id)
            
            try:
                events = []
                
                # Buscar evento SLARequested
                requested_events = self.contract.events.SLARequested().get_logs(
                    argument_filters={"slaId": sla_id},
                    fromBlock=from_block
                )
                for event in requested_events:
                    events.append({
                        "event": "SLARequested",
                        "sla_id": event.args.slaId,
                        "customer": event.args.customer,
                        "service_name": event.args.serviceName,
                        "block_number": event.blockNumber,
                        "transaction_hash": event.transactionHash.hex()
                    })
                
                # Buscar evento SLAUpdated
                updated_events = self.contract.events.SLAUpdated().get_logs(
                    argument_filters={"slaId": sla_id},
                    fromBlock=from_block
                )
                for event in updated_events:
                    events.append({
                        "event": "SLAUpdated",
                        "sla_id": event.args.slaId,
                        "status": event.args.status,
                        "block_number": event.blockNumber,
                        "transaction_hash": event.transactionHash.hex()
                    })
                
                # Buscar evento SLACompleted
                completed_events = self.contract.events.SLACompleted().get_logs(
                    argument_filters={"slaId": sla_id},
                    fromBlock=from_block
                )
                for event in completed_events:
                    events.append({
                        "event": "SLACompleted",
                        "sla_id": event.args.slaId,
                        "block_number": event.blockNumber,
                        "transaction_hash": event.transactionHash.hex()
                    })
                
                span.set_attribute("events.count", len(events))
                
                return events
                
            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                print(f"❌ Erro ao obter eventos do SLA: {e}")
                return []
