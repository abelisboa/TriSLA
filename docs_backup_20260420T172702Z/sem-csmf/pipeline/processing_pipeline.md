# SEM-CSMF Processing Pipeline

## 1. Canonical Flow

Intent -> NLP -> Ontology -> Validation -> NEST -> Dispatch

The pipeline formalizes how raw intent statements become semantically validated artifacts for decision and prediction modules.

## 2. End-to-End Lifecycle

1. **Intent Reception**
   - Accepts intent from REST/gRPC endpoint
   - Supports natural language and structured JSON payloads
   - Validates schema-level consistency

2. **NLP Extraction**
   - Identifies slice type candidates (`eMBB`, `URLLC`, `mMTC`)
   - Extracts requirement entities (latency, throughput, reliability, jitter, packet loss)
   - Normalizes units and lexical variants

3. **Ontology Validation**
   - Loads ontology graph (`trisla.ttl`) via `owlready2`
   - Checks class/property compatibility
   - Rejects semantically inconsistent intent formulations

4. **Semantic Matching**
   - Resolves intent constraints into ontology-grounded slice semantics
   - Applies reasoner-based validation
   - Produces validated semantic representation

5. **NEST Generation**
   - Converts validated intent to NEST artifact (GST-to-NEST mapping)
   - Includes multi-domain semantic structure (RAN, Transport, Core)
   - Persists NEST and processing metadata

6. **Dispatch to Decision Engine and ML-NSMF**
   - I-01 gRPC dispatch of decision metadata to Decision Engine
   - I-02 Kafka publish of NEST event to ML-NSMF
   - Emits observability traces and metrics

## 3. Formal View

Semantic projection:

`NEST = T(V(O(P(I))))`

where:

- `I`: raw intent
- `P`: NLP parsing and normalization
- `O`: ontology mapping
- `V`: semantic validation and reasoning
- `T`: template transformation (NEST generation)

This decomposition allows deterministic analysis of failure points and supports reproducible experiment design.

## 4. Failure Modes and Guardrails

- **Parsing ambiguity:** mitigated by fallback to structured constraints
- **Ontology mismatch:** explicit validation failure with traceable diagnostics
- **Interface dispatch failure:** retry-enabled clients for gRPC and Kafka
- **Persistence unavailability:** repository-level error handling and controlled failure propagation

## 5. Reproducibility Notes

- Maintain stable ontology version and parser configuration during experiments
- Log full intent, normalized fields, and validation outcomes
- Preserve dispatch timestamps for cross-module correlation

## 6. Pipeline Summary

The SEM-CSMF pipeline is not a generic ETL chain; it is a semantic control process that converts human-level intent into machine-level contractual artifacts suitable for SLA-aware decisioning in TriSLA.
