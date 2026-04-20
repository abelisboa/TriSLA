# TriSLA Ontology — Semantic Foundation

## Overview

The ontology defines the semantic model used by SEM-CSMF to interpret and validate SLA intents.

It formalizes how intent, constraints, slice semantics, and domain context are represented before admission scoring.

## Role

- Map intent -> slice type
- Validate constraints
- Enable reasoning

## Model

`SLA_semantic = f(Intent, Constraints, SliceType)`

Extended analytical form used in this documentation set:

`SLA_semantic = f(Intent, Constraints, SliceType, DomainContext, OntologyRules)`

## Domains

- RAN
- Transport
- Core

## Integration

Used before decision-making.

The semantic output from ontology validation is consumed by NEST generation and dispatched to the Decision Engine and ML-NSMF.

## Consolidated References

- `semantic_model_reference.md` - complete classes, properties, prototyping and reasoning guide
- `../pipeline/processing_pipeline.md` - pipeline-level semantic lifecycle
- `../interfaces/interfaces.md` - interface contracts for semantic outputs

