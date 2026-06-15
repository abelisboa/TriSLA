from typing import Any

from interfaces.base_interface import log_interface


class CNI1Interface:
    """
    CN-I1 no Decision Engine: traço do plano de controlo SEM → Decision → ML.
    NASP/Core instantiate ocorre no portal-backend, não aqui.
    """

    @staticmethod
    def trace_phase(phase: str, intent_id: str, **extra: Any) -> None:
        log_interface("CN-I1", {"phase": phase, "intent_id": intent_id, **extra})
