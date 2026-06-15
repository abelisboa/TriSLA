from typing import Any, Dict, Optional, Sequence

from interfaces.bc_i1 import BCI1Interface
from interfaces.cn_i1 import CNI1Interface
from interfaces.obs_i1 import OBSI1Interface
from interfaces.ran_i1 import RANI1Interface
from interfaces.tn_i1 import TNI1Interface


def hook_evaluate_begin(intent_id: str, context: Optional[Dict[str, Any]]) -> None:
    CNI1Interface.trace_phase("evaluate_begin", intent_id)
    OBSI1Interface.observe_context(context)


def hook_ml_predict_begin(intent_id: str) -> None:
    CNI1Interface.trace_phase("ml_predict_begin", intent_id)


def hook_ml_predict_end(intent_id: str, ml_prediction: Any) -> None:
    CNI1Interface.trace_phase(
        "ml_predict_end",
        intent_id,
        ml_prediction_present=ml_prediction is not None,
    )


def hook_after_decision_rules(
    intent_id: str, domains: Sequence[str], action_label: str
) -> None:
    RANI1Interface.trace_domains(domains)
    TNI1Interface.trace_domains(domains)
    CNI1Interface.trace_phase("decision_rules_applied", intent_id, action=action_label)


def hook_bc_register_path(
    intent_id: str, is_accept: bool, tx_hash: Optional[str]
) -> None:
    BCI1Interface.trace_register_path(intent_id, is_accept, tx_hash)
