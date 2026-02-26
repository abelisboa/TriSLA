import os
import threading
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


# S55: Lock per sender — single worker sends sequentially per account (avoids nonce collision)
_TX_LOCK = threading.Lock()

# S55: Config
_BC_TX_QUEUE_ENABLED = os.getenv("BC_TX_QUEUE_ENABLED", "true").lower() == "true"
_BC_TX_RECEIPT_TIMEOUT = int(os.getenv("BC_TX_RECEIPT_TIMEOUT", "60"))
_BC_GAS_BUMP_PERCENT = int(os.getenv("BC_GAS_BUMP_PERCENT", "20"))
_MAX_RETRIES = 3


def _get_pending_nonce(web3: Web3, address: str) -> int:
    """S55: Nonce source = pending (eth_getTransactionCount(address, 'pending'))."""
    return web3.eth.get_transaction_count(Web3.to_checksum_address(address), block_identifier="pending")


def _is_replacement_or_nonce_error(exc: Exception) -> bool:
    msg = (getattr(exc, "message", None) or str(exc)).lower()
    return (
        "replacement transaction underpriced" in msg
        or "nonce too low" in msg
        or "already known" in msg
    )


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

    if chain_id is None:
        chain_id = int(web3.eth.chain_id)

    min_gas_wei = int(os.getenv("BC_MIN_GAS_PRICE_WEI", "1000000000"))  # 1 gwei default (S53)

    lock = _TX_LOCK if _BC_TX_QUEUE_ENABLED else None
    if lock:
        lock.acquire()
    try:
        current_gas = gas_price_wei
        for attempt in range(_MAX_RETRIES):
            # S55: always use pending nonce when queue enabled
            nonce = _get_pending_nonce(web3, from_addr) if _BC_TX_QUEUE_ENABLED else web3.eth.get_transaction_count(from_addr)

            if current_gas is None:
                current_gas = int(web3.eth.gas_price)
            if current_gas < min_gas_wei:
                current_gas = min_gas_wei

            tx = {
                "to": Web3.to_checksum_address(to),
                "from": Web3.to_checksum_address(from_addr),
                "value": int(value_wei),
                "data": data,
                "nonce": nonce,
                "chainId": chain_id,
                "gasPrice": current_gas,
            }

            if gas is None:
                try:
                    tx["gas"] = int(web3.eth.estimate_gas(tx))
                except Exception:
                    tx["gas"] = 800000
            else:
                tx["gas"] = gas

            signed = acct.sign_transaction(tx)
            try:
                tx_hash = web3.eth.send_raw_transaction(signed.rawTransaction)
                break
            except Exception as e:
                if _is_replacement_or_nonce_error(e) and attempt < _MAX_RETRIES - 1:
                    # S55: retry with bumped gas and fresh pending nonce
                    current_gas = current_gas + (current_gas * _BC_GAS_BUMP_PERCENT // 100)
                    continue
                raise

        # S55: optional receipt wait with bounded timeout
        if _BC_TX_RECEIPT_TIMEOUT > 0:
            try:
                receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=_BC_TX_RECEIPT_TIMEOUT)
            except Exception as e:
                if "timeout" in str(e).lower() or "timed out" in str(e).lower():
                    raise RuntimeError(
                        f"Transaction {tx_hash.hex()} not mined within {_BC_TX_RECEIPT_TIMEOUT}s."
                    ) from e
                raise

        return {
            "from": from_addr,
            "to": to,
            "nonce": nonce,
            "chain_id": chain_id,
            "gas": tx["gas"],
            "gas_price": current_gas,
            "tx_hash": tx_hash.hex(),
        }
    finally:
        if lock:
            lock.release()
