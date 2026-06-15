# TriSLA Ontology — Semantic Foundation

## Overview

The ontology defines the semantic model used by SEM-CSMF to interpret and validate SLA intents.

## Role

- Map intent → slice type
- Validate constraints
- Enable reasoning
- Supply KPI fallbacks for semantic fill (`services/semantic_resolver.py`)

Runtime loader prefers `apps/sem-csmf/src/ontology/trisla_complete.owl`, then `trisla.ttl`.

## Documentation

| Document | Content |
|----------|---------|
| [`semantic_model_reference.md`](semantic_model_reference.md) | Class hierarchy, properties, SPARQL, Protégé steps |
| [`../pipeline/processing_pipeline.md`](../pipeline/processing_pipeline.md) | Semantic fill and validation lifecycle |
| [`../interfaces/interfaces.md`](../interfaces/interfaces.md) | I-01 output contracts |
| [`../../modules/sem-csmf.md`](../../modules/sem-csmf.md) | Operational entry point |

Semantic output feeds NEST generation and I-01 HTTP dispatch to the Decision Engine.
