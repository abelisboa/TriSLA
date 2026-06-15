# Decision Engine Architecture

> **Operational SSOT:** [`docs/modules/decision-engine.md`](../../modules/decision-engine.md)

Architecture, component inventory, production hot path, and integration boundaries are maintained in the canonical module document to avoid duplication.

## Quick reference

| Layer | Module | Hot path |
|-------|--------|----------|
| HTTP ingress | `main.py` → `POST /evaluate` | Yes |
| Service | `service.py` → `DecisionService` | Yes |
| Admission rules | `engine.py` → `_apply_decision_rules` | Yes |
| ML client | `ml_client.py` | Yes |
| I-01 echo | `i01_metadata_echo.py`, `i01_nest_echo.py` | Yes |
| Explainability | `decision_snapshot.py`, `system_xai.py`, `decision_evidence.py` | Yes |
| Legacy gRPC | `grpc_server.py` + `RuleEngine` | No — TRACEABILITY_ONLY |
| Authority enrichers | `orchestration_authority.py`, `lifecycle_authority.py` | No — NOT WIRED |

Frozen chain position: SEM-CSMF → Decision Engine → (return) → Portal → NASP Adapter (post-ACCEPT).
