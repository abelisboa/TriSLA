# SEM-CSMF — Documentation Index

Semantic interpretation layer of TriSLA: transforms SLA intents into ontology-validated GST/NEST artifacts and forwards structured input to the Decision Engine.

## Operational entry point

**[`docs/modules/sem-csmf.md`](../modules/sem-csmf.md)** — REST catalog, runtime paths, digest pin, integrations, env vars.

Use that document for operations, integration, and freeze alignment. This directory holds specialized references only.

## Documentation map

| Directory | Content |
|-----------|---------|
| [`architecture/`](architecture/sem_csmf_architecture.md) | Components, code layout, processing layers |
| [`pipeline/`](pipeline/processing_pipeline.md) | Full runtime lifecycle (single in-depth pipeline reference) |
| [`interfaces/`](interfaces/interfaces.md) | I-01 HTTP SSOT, REST ingress, I-02/I-01 gRPC legacy |
| [`ontology/`](ontology/README.md) | OWL semantic model index |
| [`examples/`](examples/usage_and_reproducibility.md) | Runnable patterns, env vars, tests, troubleshooting |

## Scope boundary

SEM-CSMF **does not** perform final SLA admission. Decision authority remains in the Decision Engine; orchestration and on-chain registration occur downstream via Portal relay.

Implementation: `apps/sem-csmf/src/`
