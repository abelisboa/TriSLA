from typing import Sequence

from interfaces.base_interface import log_interface


class TNI1Interface:
    """TN-I1: domínio transporte referenciado na decisão."""

    @staticmethod
    def trace_domains(domains: Sequence[str]) -> None:
        def _is_transport(d: str) -> bool:
            u = str(d).upper()
            return "TRANSPORT" in u or u == "TRANSPORTE"

        active = any(_is_transport(str(d)) for d in (domains or []))
        if active:
            log_interface("TN-I1", {"active": True, "domains": list(domains)})
