from src.observability.distributed_trace import (
    build_distributed_traceability,
    child_trace,
    new_root_trace,
)


def test_new_root_trace_has_ids():
    trace = new_root_trace("portal-backend")
    assert len(trace["trace_id"]) == 32
    assert len(trace["span_id"]) == 16
    assert trace["parent_span_id"] is None


def test_end_to_end_same_trace_id():
    root = new_root_trace("portal-backend")
    hops = [
        root,
        child_trace(root, "sem-csmf"),
        child_trace(root, "decision-engine"),
        child_trace(root, "bc-nssmf"),
        child_trace(root, "sla-agent"),
    ]
    block = build_distributed_traceability(root, hops)
    assert block["end_to_end"] is True
    assert block["trace_id"] == root["trace_id"]
    assert len(block["correlation_chain"]) == 5
