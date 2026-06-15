from typing import Optional

from interfaces.base_interface import log_interface


class BCI1Interface:
    """BC-I1: tentativa de registo on-chain no âmbito do Decision Engine (quando aplicável)."""

    @staticmethod
    def trace_register_path(
        intent_id: str, is_accept: bool, tx_hash: Optional[str]
    ) -> None:
        log_interface(
            "BC-I1",
            {
                "intent_id": intent_id,
                "is_accept": is_accept,
                "tx_hash_present": bool(tx_hash),
            },
        )
