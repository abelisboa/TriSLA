import os
from typing import Optional

from eth_account import Account
from eth_account.signers.local import LocalAccount

Account.enable_unaudited_hdwallet_features()


def get_private_key() -> str:
    pk = os.getenv("BC_PRIVATE_KEY", "").strip()
    if not pk:
        raise RuntimeError("BC_PRIVATE_KEY não configurada.")
    # aceitar com/sem 0x
    if pk.startswith("0x"):
        pk = pk[2:]
    if len(pk) != 64:
        raise RuntimeError("BC_PRIVATE_KEY inválida (tamanho incorreto).")
    return "0x" + pk


def load_account() -> LocalAccount:
    pk = get_private_key()
    return Account.from_key(pk)


def get_sender_address() -> str:
    return load_account().address

