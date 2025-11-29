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

from .config import BCConfig

logger = logging.getLogger(__name__)

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
            # Continuar sem solcx, apenas sem compilação

        try:
            self.w3 = Web3(Web3.HTTPProvider(cfg.rpc_url))
            if not self.w3.is_connected():
                raise Exception("Não conectado ao Besu RPC.")
            
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
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"⚠️ BC-NSSMF: RPC Besu não disponível. Entrando em modo degraded: {e}")
            self.enabled = False
            self.w3 = None
            self.contract = None

    def register_sla(self, customer, service_name, sla_hash, slos):
        if not self.enabled or not self.contract:
            raise RuntimeError("BC-NSSMF está em modo degraded. RPC Besu não disponível.")
        
        tx = self.contract.functions.registerSLA(
            customer,
            service_name,
            sla_hash,
            slos
        ).transact({"from": self.account})

        receipt = self.w3.eth.wait_for_transaction_receipt(tx)
        return receipt

    def update_status(self, sla_id, status):
        if not self.enabled or not self.contract:
            raise RuntimeError("BC-NSSMF está em modo degraded. RPC Besu não disponível.")
        
        tx = self.contract.functions.updateSLAStatus(sla_id, status).transact(
            {"from": self.account}
        )
        receipt = self.w3.eth.wait_for_transaction_receipt(tx)
        return receipt

    def get_sla(self, sla_id):
        if not self.enabled or not self.contract:
            return None  # Retornar None em modo degraded
        
        try:
            return self.contract.functions.getSLA(sla_id).call()
        except Exception:
            return None
