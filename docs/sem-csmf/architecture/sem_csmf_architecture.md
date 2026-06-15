# SEM-CSMF Architecture

> Operational catalog and endpoints: [`docs/modules/sem-csmf.md`](../../modules/sem-csmf.md).
> Full processing lifecycle: [`pipeline/processing_pipeline.md`](../pipeline/processing_pipeline.md).

## 1. Architectural Position in TriSLA

SEM-CSMF is the semantic front layer of the TriSLA control plane. It receives user intents via REST, applies semantic interpretation and validation, and emits normalized NEST artifacts for downstream evaluation.

```text
Intent (REST) → Semantic Processing → NEST → I-01 HTTP → Decision Engine
```

Decision policies remain in the Decision Engine. SEM-CSMF preserves semantic consistency at the orchestration boundary.

## 2. Main Components

| Component | File | Role |
|-----------|------|------|
| `IntentProcessor` | `intent_processor.py` | validate → GST → metadata |
| `NLPParser` | `nlp/parser.py` | NL extraction (optional) |
| `OntologyLoader` / `SemanticReasoner` / `SemanticMatcher` | `ontology/` | OWL load, inference, match |
| `SemanticCache` | `ontology/cache.py` | Reasoning result cache |
| `semantic_resolver` | `services/semantic_resolver.py` | KPI semantic fill |
| `canonical_sla` | `canonical_sla.py` | GSMA-aligned metadata block |
| `semantic_generator` | `services/semantic_generator.py` | Default SLA when portal omits requirements |
| `NESTGeneratorDB` | `nest_generator_db.py` | GST → NEST + persistence |
| `DecisionEngineHTTPClient` | `decision_engine_client.py` | I-01 HTTP (production) |
| `Repository` / DB models | `repository.py`, `models/db_models.py` | Intent/NEST persistence |
| `distributed_trace` | `observability/distributed_trace.py` | Cross-service trace propagation |

**Legacy (not production hot path):** `grpc_client.py`, `grpc_server.py`, `kafka_producer_retry.py`

## 3. Internal Structure (Code-Oriented)

```text
apps/sem-csmf/src/
├── main.py
├── intent_processor.py
├── canonical_sla.py
├── decision_engine_client.py
├── nest_generator_base.py
├── nest_generator_db.py
├── services/
│   ├── semantic_resolver.py
│   └── semantic_generator.py
├── ontology/
│   ├── trisla_complete.owl   (preferred at runtime)
│   ├── trisla.ttl
│   ├── loader.py
│   ├── reasoner.py
│   ├── parser.py
│   ├── matcher.py
│   └── cache.py
├── nlp/
│   └── parser.py
├── observability/
│   ├── metrics.py
│   └── distributed_trace.py
├── database.py
├── repository.py
├── auth.py
├── security.py
├── grpc_client.py              (TRACEABILITY_ONLY)
├── grpc_server.py              (TRACEABILITY_ONLY)
├── kafka_producer_retry.py     (LEGACY — not wired from main)
└── models/
    ├── intent.py
    ├── nest.py
    └── db_models.py
```

## 4. Processing Layers

### 4.1 Input Layer

- REST ingress on port `8080` (see operational doc for full endpoint list)
- Structured and natural-language payloads
- Schema-level validation via Pydantic models

### 4.2 Semantic Layer

- Ontology-grounded validation and inference
- Semantic fill of missing KPIs (ontology → GST → NEST precedence)
- `canonical_sla` parallel metadata generation

### 4.3 Transformation Layer

- GST template construction per slice type
- NEST generation with 3GPP TS 28.541 resource mapping
- DB persistence for intents and NESTs

### 4.4 Integration Layer

- **Production:** I-01 HTTP `POST /evaluate` to Decision Engine (telemetry enrichment via Portal Prometheus proxy)
- **Wave 3A:** optional NEST body on I-01 (`SEM_I01_NEST_TRANSMIT`, echo-only at DE)
- **Legacy:** gRPC I-01 stubs and Kafka I-02 producer — not active in `/intents` hot path

## 5. Data and Control Contracts

| Boundary | Contract |
|----------|----------|
| Input | User intent + SLA constraints (`IntentRequest`) |
| Internal | Ontology-aligned representation + semantic fill sources |
| Output | Validated NEST + metadata + I-01 payload |

Interface contracts: [`interfaces/interfaces.md`](../interfaces/interfaces.md)

## 6. Non-Functional Guarantees

- **Traceability:** intent → validation → NEST → I-01 dispatch chain
- **Explainability readiness:** explicit semantic mapping before DE scoring
- **Interoperability:** REST ingress + HTTP I-01 egress (production)
- **Standards alignment:** OWL model with 3GPP/GSMA semantic grounding

## 7. Architecture Summary

SEM-CSMF is a semantic normalization layer. By isolating interpretation and validation from admission logic, the architecture improves modularity, verifiability, and reproducibility in SLA-aware network slice orchestration.
