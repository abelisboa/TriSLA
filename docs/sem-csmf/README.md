# SEM-CSMF — Semantic Interpretation Layer of TriSLA

## 1. Overview

The SEM-CSMF (Semantic-Enhanced Communication Service Management Function) is responsible for transforming high-level SLA intents into structured, machine-interpretable representations within the TriSLA architecture.

It acts as the semantic entry point of the system, bridging user-level intent and multi-domain SLA evaluation.

In scientific terms, the module operationalizes intent formalization by combining ontology-grounded validation, natural language interpretation, and deterministic template construction. This design supports reproducibility and formal analysis in research workflows and paper-grade experiments.

---

## 2. Role in TriSLA

Pipeline:

Intent -> NLP -> Ontology -> Semantic Validation -> NEST -> Decision Engine

The SEM-CSMF does not perform final SLA admission decisions. Instead, it produces semantically validated artifacts that can be consumed by downstream decision and prediction components under consistent assumptions.

---

## 3. Responsibilities

- Interpret natural language intents
- Validate SLA requirements using ontology
- Generate Network Slice Templates (NEST)
- Provide structured input for decision-making
- Preserve traceability metadata for observability and audit
- Enforce semantic consistency with 3GPP/GSMA-aligned concepts

---

## 4. Documentation Structure

- `architecture/` -> system structure, components, runtime model
- `ontology/` -> semantic model, classes, properties, reasoning process
- `pipeline/` -> processing flow and lifecycle
- `interfaces/` -> integration contracts (gRPC, Kafka)
- `examples/` -> runnable usage patterns and troubleshooting

---

## 5. Relation to SLA Decision

The SEM-CSMF does not decide SLA acceptance.

It prepares the structured input:

**Formal Definition**

$$
X = f(SLA, R_{ran}, R_{transport}, R_{core})
$$

which is later evaluated by the Decision Engine.

From a modeling perspective, SEM-CSMF materializes semantic constraints and intent semantics as computable structures, reducing ambiguity and improving inter-module consistency before numerical scoring and policy enforcement.

---

## 6. Scientific Model and Formalization

Core semantic model:

**Formal Definition**

$$
SLA_{semantic} = f(Intent, Constraints, SliceType, OntologyContext)
$$

where:

- `Intent` captures user-level service goals
- `Constraints` represent explicit SLA requirements (latency, throughput, reliability, jitter, packet loss)
- `SliceType` maps intent to 5G slice behavior (eMBB, URLLC, mMTC)
- `OntologyContext` provides formal semantic validation and inferencing

This model ensures that downstream modules consume inputs that are not only syntactically valid, but also semantically coherent with the TriSLA domain model.

---

## 7. Summary

SEM-CSMF enables SLA-aware decision-making by transforming unstructured intents into validated, semantically consistent representations.

The consolidated documentation in this directory is organized to serve as a reproducible and academically robust reference for implementation, experimentation, and publication.
