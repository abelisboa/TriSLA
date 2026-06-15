from typing import Sequence

from interfaces.base_interface import log_interface


class RANI1Interface:
    """RAN-I1: domínio RAN referenciado na decisão."""

    @staticmethod
    def trace_domains(domains: Sequence[str]) -> None:
        active = any(str(d).upper() == "RAN" or "RAN" in str(d).upper() for d in (domains or []))
        if active:
            log_interface("RAN-I1", {"active": True, "domains": list(domains)})
