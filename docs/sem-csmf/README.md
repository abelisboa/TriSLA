# SEM-CSMF

SEM-CSMF is the intent-processing entry point for TriSLA. It accepts structured or free-form SLA requests, validates and fills SLA requirements, generates GST and NEST objects, persists them, and sends an evaluation request to the Decision Engine.

## Runtime contract

- HTTP service: `8080`
- Health: `GET /health`
- Metrics: `GET /metrics`
- Primary submission: `POST /api/v1/intents`
- Text interpretation: `POST /api/v1/interpret`
- Kubernetes service: `trisla-sem-csmf`
- Database: `DATABASE_URL`, with SQLite used when the variable is absent

The Decision Engine endpoint is configured by `DECISION_ENGINE_URL`. Its default value is the in-cluster `trisla-decision-engine` service and `/evaluate` path.

## Documentation

- [Architecture](architecture/sem_csmf_architecture.md)
- [HTTP interface](interfaces/interfaces.md)
- [Processing flow](pipeline/processing_pipeline.md)
- [Ontology components](ontology/README.md)
- [Semantic model reference](ontology/semantic_model_reference.md)
- [Usage examples](examples/usage_and_reproducibility.md)

## Implementation

- [Application](../../apps/sem-csmf/src/main.py)
- [Intent processor](../../apps/sem-csmf/src/intent_processor.py)
- [NEST generator](../../apps/sem-csmf/src/nest_generator_db.py)
- [Decision Engine client](../../apps/sem-csmf/src/decision_engine_client.py)
