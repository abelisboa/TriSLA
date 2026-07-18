# SEM-CSMF Ontology Components

SEM-CSMF uses ontology resources to validate SLA requirements and help map them to a supported service type.

## Runtime resources

The loader checks these packaged files in order:

1. `apps/sem-csmf/src/ontology/trisla_complete.owl`
2. `apps/sem-csmf/src/ontology/trisla.ttl`

If the ontology library or resource cannot be loaded, the reasoner uses its implemented value-based mapping for service-type inference.

## Components

| Source | Purpose |
|---|---|
| [`loader.py`](../../../apps/sem-csmf/src/ontology/loader.py) | Load OWL or TTL data and execute queries |
| [`reasoner.py`](../../../apps/sem-csmf/src/ontology/reasoner.py) | Infer service type and validate SLA values |
| [`matcher.py`](../../../apps/sem-csmf/src/ontology/matcher.py) | Match parsed intent data to supported concepts |
| [`parser.py`](../../../apps/sem-csmf/src/ontology/parser.py) | Convert intent data for matching |
| [`cache.py`](../../../apps/sem-csmf/src/ontology/cache.py) | Cache reasoner results |

See the [semantic model reference](semantic_model_reference.md) for supported inputs and behavior.
