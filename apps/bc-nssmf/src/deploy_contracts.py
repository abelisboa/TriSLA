import json
import os
import logging

logger = logging.getLogger(__name__)

try:
    from solcx import compile_standard, set_solc_version, install_solc
    SOLCX_AVAILABLE = True
except ImportError as e:
    logger.error(f"❌ py-solc-x não está instalado: {e}")
    SOLCX_AVAILABLE = False
    compile_standard = None
    set_solc_version = None
    install_solc = None

try:
    from web3 import Web3
    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False
    Web3 = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONTRACT_PATH = os.path.join(BASE_DIR, "contracts", "SLAContract.sol")
OUTPUT_JSON = os.path.join(BASE_DIR, "contracts", "contract_address.json")

# -------------------------------------------------------------------
# Configuração de RPC
# -------------------------------------------------------------------
RPC_URL = os.environ.get("TRISLA_RPC_URL", "http://127.0.0.1:8545")

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
    1) TRISLA_PRIVATE_KEY
    2) TRISLA_DEV_PRIVATE_KEY (somente quando configurada explicitamente)
    """
    env_prod = os.environ.get("TRISLA_PRIVATE_KEY")
    env_dev = os.environ.get("TRISLA_DEV_PRIVATE_KEY")

    if env_prod:
        print("[TriSLA][BC] Usando TRISLA_PRIVATE_KEY (modo PRODUÇÃO).")
        return _normalize_hex_key(env_prod)

    if env_dev:
        print("[TriSLA][BC] Usando TRISLA_DEV_PRIVATE_KEY (override DEV).")
        return _normalize_hex_key(env_dev)

    raise RuntimeError(
        "Configure TRISLA_PRIVATE_KEY ou TRISLA_DEV_PRIVATE_KEY por secret externo."
    )


def load_contract() -> str:
    with open(CONTRACT_PATH, "r", encoding="utf-8") as f:
        return f.read()


def deploy() -> None:
    if not SOLCX_AVAILABLE:
        raise ImportError("py-solc-x não está instalado. Execute: pip install py-solc-x>=1.1.1")
    
    if not WEB3_AVAILABLE:
        raise ImportError("web3 não está instalado. Execute: pip install web3>=6.0.0")
    
    print("[TriSLA] Compilando contrato Solidity...")
    try:
        # Tentar instalar versão específica do solc se não estiver disponível
        try:
            set_solc_version("0.8.20")
        except Exception as e:
            logger.warning(f"⚠️ Versão 0.8.20 não encontrada, tentando instalar: {e}")
            if install_solc:
                install_solc("0.8.20")
                set_solc_version("0.8.20")
            else:
                raise
    except Exception as e:
        logger.error(f"❌ Erro ao configurar solc 0.8.20: {e}")
        logger.info("ℹ️ Tentando usar versão disponível...")
        # Tentar usar versão padrão disponível
        try:
            set_solc_version("0.8.20")
        except:
            logger.warning("⚠️ Continuando sem versão específica do solc")

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
        print(f"⚠️ AVISO: RPC Besu não conectado em {RPC_URL}.")
        print("   Deploy de contratos será pulado. Módulo entrará em modo degraded.")
        return  # Não interromper startup, apenas pular deploy

    private_key = get_private_key()
    acct = w3.eth.account.from_key(private_key)
    from_addr = acct.address
    print(f"[TriSLA] Usando conta: {from_addr}")

    # Verificar saldo
    balance = w3.eth.get_balance(from_addr)
    balance_eth = w3.from_wei(balance, "ether")
    print(f"[TriSLA] Saldo da conta: {balance_eth} ETH ({balance} wei)")

    if balance < w3.to_wei("0.01", "ether"):
        raise RuntimeError(
            f"Saldo insuficiente: {balance_eth} ETH. "
            "Necessário pelo menos 0.01 ETH para deploy."
        )

    print("[TriSLA][BC] Conta carregada exclusivamente de configuração externa.")

    chain_id_str = os.environ.get("TRISLA_CHAIN_ID", "1337")
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
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    print(f"[TriSLA] Enviando transação de deploy: {tx_hash.hex()}")

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    contract_address = receipt.contractAddress
    print(f"[TriSLA] Contrato implantado em: {contract_address}")

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump({"address": contract_address, "abi": abi}, f, indent=4)

    print("[TriSLA] Endereço e ABI salvos em contract_address.json")


if __name__ == "__main__":
    deploy()
