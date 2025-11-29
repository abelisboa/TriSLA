"""
Cliente BC-NSSMF - Decision Engine
Integração com Blockchain via Web3 (Interface I-06)
Registra SLA no contrato inteligente após decisão
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
from web3 import Web3
from opentelemetry import trace

from config import config
from models import DecisionResult, DecisionAction

tracer = trace.get_tracer(__name__)


class BCClient:
    """
    Cliente para comunicação com BC-NSSMF (Interface I-06)
    Registra e atualiza SLAs no contrato inteligente Besu
    """
    
    def __init__(self):
        self.w3: Optional[Web3] = None
        self.contract = None
        self.contract_address = None
        self.account = None
        self._initialize()
    
    def _initialize(self):
        """Inicializa conexão Web3 e contrato"""
        with tracer.start_as_current_span("bc_client_init") as span:
            try:
                # Conectar ao Besu RPC
                self.w3 = Web3(Web3.HTTPProvider(config.bc_nssmf_rpc_url))

                if not self.w3.is_connected():
                    # Fallback: modo degraded - não interromper servidor
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"⚠️ Decision Engine: Besu RPC não disponível em {config.bc_nssmf_rpc_url}. Modo degraded ativado.")
                    self.w3 = None
                    self.contract = None
                    self.contract_address = None
                    self.account = None
                    span.set_attribute("bc.initialized", False)
                    span.set_attribute("bc.mode", "degraded")
                    return  # Continuar sem blockchain

                # Carregar informações do contrato
                configured_path = Path(config.bc_nssmf_contract_path)

                if configured_path.is_absolute():
                    contract_path = configured_path
                else:
                    project_root = Path(__file__).resolve().parents[3]
                    contract_path = (
                        project_root /
                        "apps" / "bc-nssmf" / "src" / "contracts" /
                        "contract_address.json"
                    )

                if not contract_path.exists():
                    raise FileNotFoundError(
                        f"contract_address.json não encontrado em {contract_path}"
                    )

                with open(contract_path, "r") as f:
                    contract_data = json.load(f)

                self.contract_address = contract_data["address"]
                self.abi = contract_data["abi"]

                self.contract = self.w3.eth.contract(
                    address=Web3.to_checksum_address(self.contract_address),
                    abi=self.abi,
                )

                accounts = self.w3.eth.accounts
                if accounts:
                    self.account = accounts[0]
                else:
                    from eth_account import Account
                    private_key = os.getenv(
                        "TRISLA_PRIVATE_KEY",
                        "0x8f2a55949038a9610f50fb23b5883af3b4ecb3c3bb792cbcefbd1542c692be63",
                    )
                    self.account = Account.from_key(private_key).address

                span.set_attribute("bc.contract_address", self.contract_address)
                span.set_attribute("bc.account", self.account)

            except Exception as e:
                span.record_exception(e)
                # Fallback: modo degraded - não interromper servidor
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"⚠️ Decision Engine: Erro ao inicializar BC Client. Modo degraded ativado: {e}")
                self.w3 = None
                self.contract = None
                self.contract_address = None
                self.account = None
                span.set_attribute("bc.initialized", False)
                span.set_attribute("bc.mode", "degraded")
                span.set_status(trace.Status(trace.StatusCode.OK, "Degraded mode"))
                # Não levantar exceção - continuar sem blockchain
    
    async def register_sla_on_chain(self, decision_result: DecisionResult) -> Optional[str]:
        """
        Registra SLA no blockchain após decisão AC
        
        Args:
            decision_result: Resultado da decisão com intent e action
        
        Returns:
            Hash da transação ou None em caso de erro
        """
        with tracer.start_as_current_span("register_sla_blockchain") as span:
            # Verificar se BC está disponível
            if not self.w3 or not self.contract:
                span.set_attribute("bc.skip_reason", "Degraded mode - BC not available")
                import logging
                logger = logging.getLogger(__name__)
                logger.info("⚠️ Decision Engine: BC-NSSMF não disponível. Registro no blockchain pulado (modo degraded).")
                return None
            span.set_attribute("decision.id", decision_result.decision_id)
            span.set_attribute("decision.action", decision_result.action.value)
            
            # Só registrar se decisão for ACCEPT
            if decision_result.action != DecisionAction.ACCEPT:
                span.set_attribute("bc.skip_reason", "Decision not ACCEPT")
                return None
            
            try:
                # Preparar dados para registro
                customer = decision_result.intent_id  # Usar intent_id como customer ID
                service_name = f"SLA-{decision_result.intent_id}"
                
                # Calcular hash do SLA (simplificado)
                import hashlib
                sla_content = f"{decision_result.intent_id}{decision_result.reasoning}"
                sla_hash = hashlib.sha256(sla_content.encode()).hexdigest()
                sla_hash_bytes = bytes.fromhex(sla_hash)
                
                # Converter SLOs para formato do contrato
                slos_tuples = []
                if decision_result.slos:
                    for slo in decision_result.slos:
                        slos_tuples.append((
                            slo.name,
                            int(slo.value),
                            int(slo.threshold)
                        ))
                else:
                    # SLOs padrão se não especificados
                    slos_tuples = [
                        ("latency", 10, 10),
                        ("reliability", 999, 999)
                    ]
                
                # Obter nonce
                nonce = self.w3.eth.get_transaction_count(self.account)
                
                # Construir transação
                tx = self.contract.functions.registerSLA(
                    customer,
                    service_name,
                    sla_hash_bytes,
                    slos_tuples
                ).build_transaction({
                    "from": self.account,
                    "chainId": config.bc_nssmf_chain_id,
                    "nonce": nonce,
                    "gas": 500000,
                    "gasPrice": self.w3.to_wei("1", "gwei")
                })
                
                # Assinar e enviar transação
                private_key = os.getenv(
                    "TRISLA_PRIVATE_KEY",
                    "0x8f2a55949038a9610f50fb23b5883af3b4ecb3c3bb792cbcefbd1542c692be63"
                )
                from eth_account import Account
                account = Account.from_key(private_key)
                signed_tx = account.sign_transaction(tx)
                
                tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                
                # Aguardar confirmação
                receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)
                
                span.set_attribute("bc.tx_hash", receipt.transactionHash.hex())
                span.set_attribute("bc.block_number", receipt.blockNumber)
                
                return receipt.transactionHash.hex()
                
            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                return None
    
    async def update_sla_status(self, sla_id: int, status: int) -> Optional[str]:
        """
        Atualiza status de SLA no blockchain
        
        Args:
            sla_id: ID do SLA no contrato
            status: Novo status (0=REQUESTED, 1=APPROVED, 2=REJECTED, 3=ACTIVE, 4=COMPLETED)
        
        Returns:
            Hash da transação ou None
        """
        with tracer.start_as_current_span("update_sla_status_blockchain") as span:
            # Verificar se BC está disponível
            if not self.w3 or not self.contract:
                span.set_attribute("bc.skip_reason", "Degraded mode - BC not available")
                return None
            span.set_attribute("bc.sla_id", sla_id)
            span.set_attribute("bc.status", status)
            
            try:
                nonce = self.w3.eth.get_transaction_count(self.account)
                
                tx = self.contract.functions.updateSLAStatus(
                    sla_id,
                    status
                ).build_transaction({
                    "from": self.account,
                    "chainId": config.bc_nssmf_chain_id,
                    "nonce": nonce,
                    "gas": 200000,
                    "gasPrice": self.w3.to_wei("1", "gwei")
                })
                
                private_key = os.getenv(
                    "TRISLA_PRIVATE_KEY",
                    "0x8f2a55949038a9610f50fb23b5883af3b4ecb3c3bb792cbcefbd1542c692be63"
                )
                from eth_account import Account
                account = Account.from_key(private_key)
                signed_tx = account.sign_transaction(tx)
                
                tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)
                
                return receipt.transactionHash.hex()
                
            except Exception as e:
                span.record_exception(e)
                return None
    
    def get_sla_from_chain(self, sla_id: int) -> Optional[Dict[str, Any]]:
        """
        Lê SLA do blockchain
        
        Args:
            sla_id: ID do SLA
        
        Returns:
            Dados do SLA ou None
        """
        if not self.w3 or not self.contract:
            return None  # Modo degraded
        
        try:
            result = self.contract.functions.getSLA(sla_id).call()
            return {
                "customer": result[0],
                "service_name": result[1],
                "status": result[2],
                "created_at": result[3],
                "updated_at": result[4]
            }
        except Exception:
            return None

