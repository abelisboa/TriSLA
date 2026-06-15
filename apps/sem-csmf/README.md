# SEM-CSMF

Documentation: [`docs/modules/sem-csmf.md`](../../docs/modules/sem-csmf.md) (operational entry) · [`docs/sem-csmf/`](../../docs/sem-csmf/README.md) (specialized references)

Implementation: `apps/sem-csmf/src/main.py` (FastAPI v3.10.0)

Pipeline: Intent → Ontology → GST → NEST → semantic fill → canonical SLA → **I-01 HTTP** → Decision Engine

Interface I-01: **HTTP POST `/evaluate`** (`decision_engine_client.py`). gRPC and Kafka are legacy/traceability only.
