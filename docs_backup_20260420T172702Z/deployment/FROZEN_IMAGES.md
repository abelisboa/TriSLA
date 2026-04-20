# TriSLA v3.9.3 - Frozen Images Contract

**This document is normative and authoritative for TriSLA v3.9.3 deployment.**

**Audit Date**: 2026-01-22
**Cluster**: NASP
**Namespace**: trisla

## Mandatory Images

### Core Services

| Image | Tag | Digest | Role | Classification |
|-------|-----|--------|------|----------------|
| ghcr.io/abelisboa/trisla-sem-csmf | v3.9.4 | TBD | SEM-CSMF Service | Mandatory |
| ghcr.io/abelisboa/trisla-ml-nsmf | v3.9.4 | TBD | ML-NSMF Service | Mandatory |
| ghcr.io/abelisboa/trisla-decision-engine | v3.9.5-fix | TBD | Decision Engine | Mandatory |
| ghcr.io/abelisboa/trisla-bc-nssmf | v3.9.4 | TBD | BC-NSSMF Service | Mandatory |
| ghcr.io/abelisboa/trisla-sla-agent-layer | v3.9.4 | TBD | SLA Agent Layer | Mandatory |

### Infrastructure

| Image | Tag | Digest | Role | Classification |
|-------|-----|--------|------|----------------|
| apache/kafka | latest | TBD | Message Queue | Mandatory |

**WARNING**: Kafka is using 'latest' tag. For reproducibility, this should be fixed to a specific version (e.g., 3.6.0).

## Optional Images

| Image | Tag | Digest | Role | Classification |
|-------|-----|--------|------|----------------|
| ghcr.io/abelisboa/trisla-portal-backend | v3.8.1 | TBD | Portal Backend | Optional |
| ghcr.io/abelisboa/trisla-portal-frontend | v3.8.1 | TBD | Portal Frontend | Optional |
| ghcr.io/abelisboa/trisla-ui-dashboard | v3.9.4 | TBD | UI Dashboard | Optional |
| ghcr.io/abelisboa/trisla-traffic-exporter | v3 | TBD | Traffic Exporter | Optional |
| networkstatic/iperf3 | latest | TBD | Network Testing | Optional |

## Environment-Specific Images

| Image | Tag | Digest | Role | Classification |
|-------|-----|--------|------|----------------|
| ghcr.io/abelisboa/trisla-nasp-adapter | v3.9.4 | TBD | NASP Adapter | Environment-specific |

## Version Inconsistencies

1. **Decision Engine**: v3.9.5-fix (different from other v3.9.4 components)
2. **Portal Backend/Frontend**: v3.8.1 (older version)
3. **Traffic Exporter**: v3 (no specific patch version)

## Notes

- All images are pulled from ghcr.io (GitHub Container Registry)
- Authentication required: 
- Digest values should be retrieved and updated for full reproducibility
- This contract represents the frozen state at audit time
