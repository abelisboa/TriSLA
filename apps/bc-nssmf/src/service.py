import json
import os
from web3 import Web3
from solcx import set_solc_version
from .config import BCConfig

class BCService:

    def __init__(self):
        cfg = BCConfig()
        self.enabled = True
        self.w3 = None
        self.contract = None
        self.contract_address = None
        self.abi = None
        self.account = None

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
