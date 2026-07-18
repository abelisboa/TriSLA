# SEM-CSMF Semantic Model Reference

## Supported service types

| API value | Primary service characteristic |
|---|---|
| `eMBB` | High-throughput connectivity |
| `URLLC` | Low latency and high reliability |
| `mMTC` | High device density |

## SLA fields

The `SLARequirements` model accepts:

- `latency`
- `throughput`
- `reliability`
- `availability`
- `jitter`
- `coverage`
- `device_density`

Latency, throughput, jitter, and coverage are strings in the API model. Reliability, availability, and device density are numeric values.

## Loading and inference

`OntologyLoader` prefers the packaged OWL resource and uses the TTL resource when the OWL file is unavailable. When reasoning support is available, the loader applies it during initialization. `SemanticReasoner` caches successful inference and validation results.

When ontology inference is unavailable, the implemented value mapping uses latency, throughput, and reliability to select a service type. It returns `eMBB` when no more specific match is found.

## Processing output

Validated requirements are used to generate:

- a GST identifier and template;
- a NEST containing one or more network slices;
- metadata passed to the Decision Engine;
- a canonical SLA object returned with processing results.

The API data models are defined in [`models/intent.py`](../../../apps/sem-csmf/src/models/intent.py) and [`models/nest.py`](../../../apps/sem-csmf/src/models/nest.py).
