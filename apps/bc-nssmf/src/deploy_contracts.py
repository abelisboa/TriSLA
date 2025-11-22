import json
import os

from solcx import compile_standard, set_solc_version
from web3 import Web3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONTRACT_PATH = os.path.join(BASE_DIR, "contracts", "SLAContract.sol")
OUTPUT_JSON = os.path.join(BASE_DIR, "contracts", "contract_address.json")

# -------------------------------------------------------------------
# Configuração de RPC - Ethereum Permissionado (GoQuorum/Besu)
# Conforme dissertação TriSLA: usar infraestrutura Ethereum permissionada
# -------------------------------------------------------------------
RPC_URL = os.environ.get("BESU_RPC_URL", os.environ.get("TRISLA_RPC_URL", "http://besu-dev:8545"))

# -------------------------------------------------------------------
# CHAVE PRIVADA
# - Em DEV: usa a chave padrão do Besu (--network=dev)
# - Em PRODUÇÃO: usar TRISLA_PRIVATE_KEY (ou secret externo)
# -------------------------------------------------------------------
DEFAULT_DEV_PRIVATE_KEY = (
    "0x4f3edf983ac636a65a842ce7c78d9aa706d3b113b37c7e5e25f8fcd6f5a3d4e8"
)
DEFAULT_DEV_ADDRESS = "0x90f8bf6a479f320ead074411a4b0e7944ea8c9c1"


def _normalize_hex_key(key: str) -> str:
    """
    Normaliza uma chave hex:
    - remove '0x' se existir
    - valida tamanho (64 chars = 32 bytes)
    - valida se é hex
    - retorna com prefixo '0x'
    """
    if key is None:
        raise ValueError("Chave privada não pode ser None.")

    key = key.strip()
    if key.startswith(("0x", "0X")):
        key_body = key[2:]
    else:
        key_body = key

    if len(key_body) != 64:
        raise ValueError(
            f"Chave privada inválida: esperado 64 caracteres hex (32 bytes), obtido {len(key_body)}."
        )

    try:
        int(key_body, 16)
    except ValueError as exc:
        raise ValueError("Chave privada contém caracteres não-hexadecimais.") from exc

    return "0x" + key_body


def get_private_key() -> str:
    """
    Ordem de prioridade:
    1) TRISLA_PRIVATE_KEY  (modo produção)
    2) TRISLA_DEV_PRIVATE_KEY (override explícito em DEV)
    3) DEFAULT_DEV_PRIVATE_KEY (modo dev padrão Besu)
    """
    env_prod = os.environ.get("TRISLA_PRIVATE_KEY")
    env_dev = os.environ.get("TRISLA_DEV_PRIVATE_KEY")

    if env_prod:
        print("[TriSLA][BC] Usando TRISLA_PRIVATE_KEY (modo PRODUÇÃO).")
        return _normalize_hex_key(env_prod)

    if env_dev:
        print("[TriSLA][BC] Usando TRISLA_DEV_PRIVATE_KEY (override DEV).")
        return _normalize_hex_key(env_dev)

    print("[TriSLA][BC] Usando DEFAULT_DEV_PRIVATE_KEY (modo DEV).")
    return _normalize_hex_key(DEFAULT_DEV_PRIVATE_KEY)


def load_contract() -> str:
    with open(CONTRACT_PATH, "r", encoding="utf-8") as f:
        return f.read()


def deploy() -> None:
    print("[TriSLA] Compilando contrato Solidity...")
    set_solc_version("0.8.20")

    source = load_contract()

    compiled = compile_standard(
        {
            "language": "Solidity",
            "sources": {"SLAContract.sol": {"content": source}},
            "settings": {
                "outputSelection": {
                    "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
                }
            },
        }
    )

    abi = compiled["contracts"]["SLAContract.sol"]["SLAContract"]["abi"]
    bytecode = compiled["contracts"]["SLAContract.sol"]["SLAContract"]["evm"]["bytecode"]["object"]

    w3 = Web3(Web3.HTTPProvider(RPC_URL))

    if not w3.is_connected():
        raise RuntimeError(
            f"❌ Erro: RPC Besu (Ethereum permissionado) não conectado em {RPC_URL}. "
            f"Verifique se o nó GoQuorum/Besu está rodando."
        )

    private_key = get_private_key()
    acct = w3.eth.account.from_key(private_key)
    from_addr = acct.address
    print(f"[TriSLA] Usando conta: {from_addr}")

    # Verificar saldo
    balance = w3.eth.get_balance(from_addr)
    balance_eth = w3.from_wei(balance, "ether")
    print(f"[TriSLA] Saldo da conta: {balance_eth} ETH ({balance} wei)")

    # Em modo DEV, usar sempre a conta padrão pré-financiada do Besu
    if os.environ.get("TRISLA_PRIVATE_KEY") is None:
        # Chave privada padrão do Besu dev mode (conta pré-financiada)
        BESU_DEFAULT_KEY = "0x8f2a55949038a9610f50fb23b5883af3b4ecb3c3bb792cbcefbd1542c692be63"
        try:
            acct = w3.eth.account.from_key(BESU_DEFAULT_KEY)
            from_addr = acct.address
            balance = w3.eth.get_balance(from_addr)
            balance_eth = w3.from_wei(balance, "ether")
            print(f"[TriSLA] Usando conta padrão Besu DEV: {from_addr} (saldo: {balance_eth} ETH)")
            private_key = BESU_DEFAULT_KEY
        except Exception as e:
            print(f"[TriSLA][BC] ERRO: Não foi possível usar conta padrão: {e}")
            raise

    if balance < w3.to_wei("0.01", "ether"):
        raise RuntimeError(
            f"Saldo insuficiente: {balance_eth} ETH. "
            "Necessário pelo menos 0.01 ETH para deploy."
        )

    if DEFAULT_DEV_ADDRESS.lower() == from_addr.lower():
        print("[TriSLA][BC] AVISO: conta DEV padrão do Besu em uso (modo desenvolvimento).")
    else:
        print("[TriSLA][BC] Conta NÃO é a DEV padrão — cenário compatível com produção.")

    chain_id_str = os.environ.get("BESU_CHAIN_ID", os.environ.get("TRISLA_CHAIN_ID", "1337"))
    try:
        chain_id = int(chain_id_str)
    except ValueError:
        raise ValueError(f"TRISLA_CHAIN_ID inválido: {chain_id_str}")

    nonce = w3.eth.get_transaction_count(from_addr)

    contract = w3.eth.contract(abi=abi, bytecode=bytecode)

    tx = contract.constructor().build_transaction(
        {
            "from": from_addr,
            "chainId": chain_id,
            "nonce": nonce,
            "gas": 6_000_000,
            "gasPrice": w3.to_wei("1", "gwei"),
        }
    )

    signed = w3.eth.account.sign_transaction(tx, private_key=private_key)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"[TriSLA] Enviando transação de deploy: {tx_hash.hex()}")

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    contract_address = receipt.contractAddress
    print(f"[TriSLA] Contrato implantado em: {contract_address}")

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump({"address": contract_address, "abi": abi}, f, indent=4)

    print("[TriSLA] Endereço e ABI salvos em contract_address.json")


if __name__ == "__main__":
    deploy()
