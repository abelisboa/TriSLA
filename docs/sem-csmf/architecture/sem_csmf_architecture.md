# SEM-CSMF Architecture

## 1. Architectural Position in TriSLA

SEM-CSMF is the semantic front layer of the TriSLA control plane. It receives user intents, applies semantic interpretation and validation, and emits a normalized NEST artifact for downstream modules.

Logical flow:

Intent Ingestion -> Semantic Processing -> NEST Generation -> Dispatch (I-01/I-02)

This separation keeps decision policies in the Decision Engine while preserving semantic consistency at the boundary of the orchestration pipeline.

## 2. Main Components

- `IntentProcessor` - orchestrates end-to-end processing of intents
- `NLPParser` - parses natural language intents into structured fields
- `OntologyLoader` - loads OWL/Turtle ontology and manages runtime graph
- `SemanticReasoner` - performs semantic checks and inference
- `NESTGenerator` - builds network slice templates from validated intents
- `DecisionEngineClient` - gRPC dispatch to Decision Engine (I-01)
- `KafkaProducer` - event dispatch to ML-NSMF (I-02)
- `Repository` / DB models - persistence for intents and generated NESTs

## 3. Internal Structure (Code-Oriented)

Source layout:

```
apps/sem-csmf/src/
├── main.py
├── intent_processor.py
├── nest_generator.py
├── nest_generator_db.py
├── ontology/
│   ├── trisla.ttl
│   ├── loader.py
│   ├── reasoner.py
│   ├── parser.py
│   └── matcher.py
├── nlp/
│   └── parser.py
├── grpc_server.py
├── grpc_client.py
├── grpc_client_retry.py
├── kafka_producer.py
├── kafka_producer_retry.py
├── database.py
├── repository.py
└── models/
    ├── intent.py
    ├── nest.py
    └── db_models.py
```

## 4. Processing Layers

### 4.1 Input Layer

- Receives intents via REST/gRPC
- Supports both structured and natural-language payloads
- Performs schema-level validation (syntax and field integrity)

### 4.2 Semantic Layer

- Maps payload semantics to ontology concepts
- Validates constraints against ontology classes/properties
- Applies semantic reasoning (consistency + inferencing)

### 4.3 Transformation Layer

- Converts validated intent into NEST
- Maps requirements to multi-domain slice representation
- Enriches artifact with metadata for traceability

### 4.4 Integration Layer

- Dispatches metadata to Decision Engine (I-01 gRPC)
- Publishes NEST artifact to ML-NSMF (I-02 Kafka)
- Persists intent/NEST for audit and replayability

## 5. Data and Control Contracts

The architecture implements a strict data contract boundary:

- Input contract: user-level intent and SLA constraints
- Internal semantic contract: ontology-aligned representation
- Output contract: validated NEST + metadata

This contract-based design is essential for reproducibility and comparability across TriSLA experimental campaigns.

## 6. Non-Functional Guarantees

- **Traceability:** intent -> validation -> NEST -> dispatch chain
- **Explainability readiness:** explicit semantic mapping prior to scoring
- **Interoperability:** open interfaces (gRPC/Kafka)
- **Standards alignment:** OWL-based model with 3GPP/GSMA semantic grounding

## 7. Architecture Summary

SEM-CSMF is intentionally designed as a semantic normalization layer. By isolating interpretation and validation from final admission logic, the architecture improves modularity, verifiability, and scientific reproducibility in SLA-aware network slice orchestration.
