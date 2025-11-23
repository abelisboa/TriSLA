import json
from web3 import Web3
from solcx import set_solc_version
from .config import BCConfig

class BCService:

    def __init__(self):
        cfg = BCConfig()

        self.w3 = Web3(Web3.HTTPProvider(cfg.rpc_url))
        if not self.w3.is_connected():
            raise Exception("Não conectado ao Besu RPC.")

        with open(cfg.contract_info_path, "r") as f:
            data = json.load(f)

        self.contract_address = data["address"]
        self.abi = data["abi"]

        self.contract = self.w3.eth.contract(
            address=self.contract_address,
            abi=self.abi
        )

        self.account = self.w3.eth.accounts[0]

    def register_sla(self, customer, service_name, sla_hash, slos):
        tx = self.contract.functions.registerSLA(
            customer,
            service_name,
            sla_hash,
            slos
        ).transact({"from": self.account})

        receipt = self.w3.eth.wait_for_transaction_receipt(tx)
        return receipt

    def update_status(self, sla_id, status):
        tx = self.contract.functions.updateSLAStatus(sla_id, status).transact(
            {"from": self.account}
        )
        receipt = self.w3.eth.wait_for_transaction_receipt(tx)
        return receipt

    def get_sla(self, sla_id):
        return self.contract.functions.getSLA(sla_id).call()
