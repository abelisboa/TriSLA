import os
from typing import Any, Dict, Optional

from web3 import Web3
from web3.exceptions import TransactionNotFound

from src.blockchain.wallet import load_account, get_sender_address


def get_rpc_url() -> str:
    url = os.getenv("BC_RPC_URL", "").strip()
    if not url:
        # fallback compatível com seu NASP
        url = os.getenv("BLOCKCHAIN_RPC_URL", "").strip()
    if not url:
        raise RuntimeError("BC_RPC_URL (ou BLOCKCHAIN_RPC_URL) não configurada.")
    return url


def w3() -> Web3:
    url = get_rpc_url()
    provider = Web3.HTTPProvider(url, request_kwargs={"timeout": 10})
    return Web3(provider)


def rpc_connected() -> bool:
    try:
        return bool(w3().is_connected())
    except Exception:
        return False


def build_and_send_signed_tx(
    to: str,
    data: str,
    value_wei: int = 0,
    gas: Optional[int] = None,
    gas_price_wei: Optional[int] = None,
    chain_id: Optional[int] = None,
) -> Dict[str, Any]:
    web3 = w3()
    if not web3.is_connected():
        raise RuntimeError("RPC blockchain indisponível.")

    acct = load_account()
    from_addr = acct.address

    # chain id
    if chain_id is None:
        chain_id = int(web3.eth.chain_id)

    # nonce
    nonce = web3.eth.get_transaction_count(from_addr)

    # gas price
    if gas_price_wei is None:
        gas_price_wei = int(web3.eth.gas_price)

    tx = {
        "to": Web3.to_checksum_address(to),
        "from": Web3.to_checksum_address(from_addr),
        "value": int(value_wei),
        "data": data,
        "nonce": nonce,
        "chainId": chain_id,
        "gasPrice": gas_price_wei,
    }

    # estimate gas
    if gas is None:
        try:
            gas = int(web3.eth.estimate_gas(tx))
        except Exception:
            # fallback conservador
            gas = 800000
    tx["gas"] = gas

    signed = acct.sign_transaction(tx)
    tx_hash = web3.eth.send_raw_transaction(signed.rawTransaction)

    return {
        "from": from_addr,
        "to": to,
        "nonce": nonce,
        "chain_id": chain_id,
        "gas": gas,
        "gas_price": gas_price_wei,
        "tx_hash": tx_hash.hex(),
    }

