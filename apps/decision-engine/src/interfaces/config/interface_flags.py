import os

INTERFACE_LAYER_ENABLED = os.getenv("INTERFACE_LAYER_ENABLED", "false").lower() == "true"
INTERFACE_LAYER_MODE = os.getenv("INTERFACE_LAYER_MODE", "shadow")  # shadow | active | off


def should_emit_interface_signals() -> bool:
    if not INTERFACE_LAYER_ENABLED:
        return False
    if (INTERFACE_LAYER_MODE or "").lower() == "off":
        return False
    return True
