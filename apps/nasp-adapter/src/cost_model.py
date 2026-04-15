"""
Cost Model determinístico (PROMPT_SMDCE_V2_CAPACITY_ACCOUNTING).
cost(slice_type, sla_requirements) -> resources_reserved.
Parametrizado por env COST_* (por slice type); defaults conservadores no Runbook.
"""

import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def _int_env(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


def cost(slice_type: str, sla_requirements: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Retorna recursos reservados (unidades por domínio) para o slice.
    Usado pelo ledger para delta = sum(active) + cost() <= capacity_effective.
    """
    sla_requirements = sla_requirements or {}
    # Env: COST_EMBB_CORE, COST_EMBB_RAN, COST_EMBB_TRANSPORT, etc.
    st = (slice_type or "eMBB").strip()
    if st not in ("eMBB", "URLLC", "mMTC"):
        st = "eMBB"
    prefix = f"COST_{st.upper()}_"
    core = _int_env(f"COST_{st.upper()}_CORE", 1)
    ran = _int_env(f"COST_{st.upper()}_RAN", 1)
    transport = _int_env(f"COST_{st.upper()}_TRANSPORT", 1)
    return {
        "core": core,
        "ran": ran,
        "transport": transport,
        "sliceType": st,
    }
