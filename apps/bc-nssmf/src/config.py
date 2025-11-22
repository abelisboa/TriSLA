"""
Configuração BC-NSSMF - Ethereum Permissionado (GoQuorum/Besu)
Configurações para integração com rede Ethereum permissionada
Alinhado com dissertação TriSLA: "Ethereum permissionado (GoQuorum/Besu)"
"""

import os
from pydantic import BaseModel
from typing import Optional


class BCConfig(BaseModel):
    """
    Configuração do BC-NSSMF para Ethereum Permissionado (GoQuorum/Besu)
    
    Conforme dissertação TriSLA:
    - Infraestrutura Ethereum permissionada (GoQuorum/Besu)
    - Execução descentralizada dos contratos
    - Rastreabilidade das cláusulas
    """
    
    # RPC URL do nó Besu/GoQuorum
    # Padrão: http://besu-dev:8545 (container) ou http://127.0.0.1:8545 (local)
    rpc_url: str = os.getenv(
        "BESU_RPC_URL",
        os.getenv("TRISLA_RPC_URL", "http://besu-dev:8545")
    )
    
    # Chain ID da rede permissionada
    # Padrão: 1337 (conforme genesis.json)
    chain_id: int = int(os.getenv("BESU_CHAIN_ID", os.getenv("TRISLA_CHAIN_ID", "1337")))
    
    # Chave privada para assinar transações
    # Em produção: usar BESU_PRIVATE_KEY ou TRISLA_PRIVATE_KEY
    # Em dev: usar chave padrão do Besu (--network=dev)
    private_key: Optional[str] = os.getenv("BESU_PRIVATE_KEY", os.getenv("TRISLA_PRIVATE_KEY"))
    
    # Caminho para arquivo com endereço e ABI do contrato deployado
    contract_info_path: str = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "src",
        "contracts",
        "contract_address.json"
    )
    
    # Gas price (em redes permissionadas pode ser zero ou controlado)
    gas_price: int = int(os.getenv("BESU_GAS_PRICE", "1000000000"))  # 1 gwei
    
    # Gas limit para transações
    gas_limit: int = int(os.getenv("BESU_GAS_LIMIT", "6000000"))
    
    @property
    def is_production(self) -> bool:
        """Verifica se está em modo produção (chave privada configurada)"""
        return self.private_key is not None and self.private_key != ""
    
    @property
    def blockchain_type(self) -> str:
        """Tipo de blockchain (conforme dissertação)"""
        return "Ethereum Permissionado (GoQuorum/Besu)"
