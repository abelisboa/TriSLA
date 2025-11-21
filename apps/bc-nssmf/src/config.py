from pydantic import BaseModel

class BCConfig(BaseModel):
    rpc_url: str = "http://127.0.0.1:8545"
    contract_info_path: str = "apps/bc-nssmf/src/contracts/contract_address.json"
