import os
from pydantic import BaseModel, Field

class BCConfig(BaseModel):
    rpc_url: str = Field(
        default="http://127.0.0.1:8545",
        env="BESU_RPC_URL"
    )
    contract_info_path: str = "apps/bc-nssmf/src/contracts/contract_address.json"
    
    @property
    def effective_rpc_url(self) -> str:
        """
        Returns the RPC URL, prioritizing environment variables in the following order:
        1. BESU_RPC_URL
        2. TRISLA_RPC_URL
        3. Default value
        """
        return (
            os.getenv("BESU_RPC_URL")
            or os.getenv("TRISLA_RPC_URL")
            or self.rpc_url
        )
