from typing import Any, Dict, Optional

from interfaces.base_interface import log_interface


class OBSI1Interface:
    """OBS-I1: presença de contexto/telemetria na avaliação (sem coletar Prometheus aqui)."""

    @staticmethod
    def observe_context(context: Optional[Dict[str, Any]]) -> None:
        if not context:
            log_interface("OBS-I1", {"telemetry_snapshot": False, "context": None})
            return
        keys = list(context.keys())[:24]
        ts = "telemetry_snapshot" in context
        log_interface(
            "OBS-I1",
            {"telemetry_snapshot": ts, "context_key_count": len(context), "context_keys": keys},
        )
