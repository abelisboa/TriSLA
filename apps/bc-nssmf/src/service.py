import json
import os
import logging

# Verificar se blockchain está habilitado (modo DEV)
BC_ENABLED = os.getenv("BC_ENABLED", "false").lower() == "true"

if BC_ENABLED:
    try:
        from web3 import Web3
        WEB3_AVAILABLE = True
    except ImportError:
        WEB3_AVAILABLE = False
        Web3 = None
    
    try:
        from solcx import set_solc_version
        SOLCX_AVAILABLE = True
    except ImportError:
        SOLCX_AVAILABLE = False
        set_solc_version = None
else:
    WEB3_AVAILABLE = False
    Web3 = None
    SOLCX_AVAILABLE = False
    set_solc_version = None

try:
    from .config import BCConfig
except ImportError:
    from config import BCConfig

logger = logging.getLogger(__name__)


class BCInfrastructureError(RuntimeError):
    """Erro de infraestrutura - RPC offline, conta não disponível, etc. Retorna 503."""
    pass


class BCBusinessError(RuntimeError):
    """Erro de negócio - saldo insuficiente, validação de dados, etc. Retorna 422."""
    pass


class BCService:

    def __init__(self):
        cfg = BCConfig()
        self.enabled = True
        self.w3 = None
        self.contract = None
        self.contract_address = None
        self.abi = None
        self.account = None

        if not BC_ENABLED:
            logger.info("ℹ️ BC-NSSMF: Modo DEV - Blockchain desabilitado (BC_ENABLED=false)")
            self.enabled = False
            return

        if not WEB3_AVAILABLE:
            logger.warning("⚠️ web3 não está instalado. BC-NSSMF em modo degraded.")
            self.enabled = False
            return

        if not SOLCX_AVAILABLE:
            logger.warning("⚠️ py-solc-x não está instalado. Compilação de contratos desabilitada.")
            # Continuar sem solcx, apenas sem compilação - não encerra o serviço

        try:
            self.w3 = Web3(Web3.HTTPProvider(cfg.rpc_url))
            if not self.w3.is_connected():
                logger.warning(f"⚠️ BC-NSSMF: Não conectado ao Besu RPC em {cfg.rpc_url}. Modo degraded.")
                self.enabled = False
                self.w3 = None
                return  # Continuar sem blockchain, mas serviço continua rodando
            
            # Carregar informações do contrato
            contract_path = cfg.contract_info_path
            if not os.path.isabs(contract_path):
                # Se caminho relativo, construir caminho absoluto
                base_dir = os.path.dirname(os.path.abspath(__file__))
                contract_path = os.path.join(base_dir, "contracts", "contract_address.json")
            
            if not os.path.exists(contract_path):
                raise FileNotFoundError(f"Arquivo de contrato não encontrado: {contract_path}")
            
            with open(contract_path, "r") as f:
                data = json.load(f)

            self.contract_address = data["address"]
            self.abi = data["abi"]

            self.contract = self.w3.eth.contract(
                address=self.contract_address,
                abi=self.abi
            )

            accounts = self.w3.eth.accounts
            if accounts:
                self.account = accounts[0]
            else:
                self.account = None
                
        except Exception as e:
            # Fallback: modo degraded
            logger.warning(f"⚠️ BC-NSSMF: RPC Besu não disponível. Entrando em modo degraded: {e}")
            self.enabled = False
            self.w3 = None
            self.contract = None

    def register_sla(self, customer, service_name, sla_hash, slos):
        """
        Registra SLA no blockchain
        
        Args:
            customer: Nome do cliente
            service_name: Nome do serviço
            sla_hash: Hash do SLA (bytes32)
            slos: Lista de SLOs [(name, value, threshold), ...]
        
        Returns:
            Transaction receipt
        
        Raises:
            BCInfrastructureError: Se RPC offline ou conta não disponível (503)
            BCBusinessError: Se saldo insuficiente ou erro de validação (422)
        """
        if not self.enabled or not self.contract:
            raise BCInfrastructureError("BC-NSSMF está em modo degraded. RPC Besu não disponível.")
        
        if not self.account:
            raise BCInfrastructureError("Conta blockchain não disponível.")
        
        # Verificar saldo antes de tentar registrar
        try:
            balance = self.w3.eth.get_balance(self.account)
            if balance == 0:
                logger.warning(f"Saldo insuficiente na conta {self.account}: {balance} wei")
                raise BCBusinessError("Saldo insuficiente na conta blockchain para registrar SLA.")
            
            logger.debug(f"Saldo da conta verificado: {balance} wei")
        except BCBusinessError:
            # Re-raise BCBusinessError sem modificação
            raise
        except Exception as e:
            # Erro ao verificar saldo - tratar como erro de infraestrutura
            logger.error(f"Erro ao verificar saldo da conta: {e}")
            raise BCInfrastructureError(f"Erro ao verificar saldo da conta blockchain: {str(e)}")
        
        try:
            tx = self.contract.functions.registerSLA(
                customer,
                service_name,
                sla_hash,
                slos
            ).transact({"from": self.account})

            receipt = self.w3.eth.wait_for_transaction_receipt(tx)
            logger.info(f"SLA registrado: tx_hash={receipt.transactionHash.hex()}, block={receipt.blockNumber}")
            return receipt
        except BCBusinessError:
            # Re-raise BCBusinessError sem modificação
            raise
        except BCInfrastructureError:
            # Re-raise BCInfrastructureError sem modificação
            raise
        except Exception as e:
            # Outros erros podem ser de infraestrutura (ex: transação falhou por rede)
            logger.error(f"Erro ao registrar SLA: {e}")
            raise BCInfrastructureError(f"Erro ao registrar SLA no blockchain: {str(e)}")

    def update_status(self, sla_id, status):
        """
        Atualiza status de SLA no blockchain
        
        Args:
            sla_id: ID do SLA
            status: Novo status (0=REQUESTED, 1=APPROVED, 2=REJECTED, 3=ACTIVE, 4=COMPLETED)
        
        Returns:
            Transaction receipt
        
        Raises:
            BCInfrastructureError: Se RPC offline ou conta não disponível (503)
            BCBusinessError: Se saldo insuficiente ou erro de validação (422)
        """
        if not self.enabled or not self.contract:
            raise BCInfrastructureError("BC-NSSMF está em modo degraded. RPC Besu não disponível.")
        
        if not self.account:
            raise BCInfrastructureError("Conta blockchain não disponível.")
        
        # Verificar saldo antes de tentar atualizar
        try:
            balance = self.w3.eth.get_balance(self.account)
            if balance == 0:
                logger.warning(f"Saldo insuficiente na conta {self.account}: {balance} wei")
                raise BCBusinessError("Saldo insuficiente na conta blockchain para atualizar SLA.")
        except BCBusinessError:
            raise
        except Exception as e:
            logger.error(f"Erro ao verificar saldo da conta: {e}")
            raise BCInfrastructureError(f"Erro ao verificar saldo da conta blockchain: {str(e)}")
        
        try:
            tx = self.contract.functions.updateSLAStatus(sla_id, status).transact(
                {"from": self.account}
            )
            receipt = self.w3.eth.wait_for_transaction_receipt(tx)
            logger.info(f"Status SLA {sla_id} atualizado: tx_hash={receipt.transactionHash.hex()}, status={status}")
            return receipt
        except BCBusinessError:
            raise
        except BCInfrastructureError:
            raise
        except Exception as e:
            logger.error(f"Erro ao atualizar status SLA {sla_id}: {e}")
            raise BCInfrastructureError(f"Erro ao atualizar status SLA no blockchain: {str(e)}")

    def get_sla(self, sla_id):
        """
        Obtém SLA do blockchain
        
        Args:
            sla_id: ID do SLA
        
        Returns:
            Tuple (customer, service_name, status, created_at, updated_at) ou None
        """
        if not self.enabled or not self.contract:
            return None  # Retornar None em modo degraded
        
        try:
            result = self.contract.functions.getSLA(sla_id).call()
            logger.debug(f"SLA {sla_id} obtido: {result}")
            return result
        except Exception as e:
            logger.warning(f"Erro ao obter SLA {sla_id}: {e}")
            return None
    
    def register_sla_on_chain(self, decision_result):
        """
        Registra SLA no blockchain a partir de DecisionResult (Interface I-06)
        
        Args:
            decision_result: DecisionResult do Decision Engine
        
        Returns:
            Transaction hash (hex) ou None
        """
        if not self.enabled or not self.contract:
            logger.warning("BC-NSSMF em modo degraded - não registrando SLA no blockchain")
            return None
        
        try:
            # Extrair dados do DecisionResult
            customer = decision_result.intent_id  # Usar intent_id como customer
            service_name = decision_result.action.value  # AC/RENEG/REJ
            sla_hash = self.w3.keccak(text=decision_result.decision_id)
            
            # Converter SLOs para formato do contrato
            slos = []
            if decision_result.slos:
                for slo in decision_result.slos:
                    slos.append((slo.name, int(slo.value * 1000), int(slo.threshold * 1000)))
            
            # Registrar SLA
            receipt = self.register_sla(customer, service_name, sla_hash, slos)
            
            return receipt.transactionHash.hex()
        except Exception as e:
            logger.error(f"Erro ao registrar SLA no blockchain: {e}")
            return None
