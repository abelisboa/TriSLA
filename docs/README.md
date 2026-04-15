# TriSLA Documentation (SSOT-Based)

This documentation is reconstructed from executable runtime behavior in
`apps/*/src` and is intended for scientific and engineering reproducibility.

## Documentation map

1. Architecture and formal model: `architecture/trisla_architecture.md`
2. Module-level runtime contracts: `modules/README.md`
3. NASP infrastructure integration: `infrastructure/nasp_integration.md`
4. Reproducibility setup and validation: `reproducibility/setup_guide.md`
5. Runbook separation policy: `development/runbook_reference.md`

## Canonical runtime pipeline

`SEM-CSMF -> ML-NSMF -> Decision Engine -> NASP Adapter -> BC-NSSMF -> SLA-Agent Layer`

## SSOT policy

- Source of truth for behavior, endpoints, and schemas: `apps/*/src`
- Documentation reflects implemented runtime contracts
- Mathematical formalization is derived from system behavior (not speculative)

## Scope

This public tree excludes internal lab-only artifacts and private operational
materials not required for open reproducibility.
