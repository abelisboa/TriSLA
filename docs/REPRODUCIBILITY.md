# Reproducibility

This document describes how to reproduce a baseline TriSLA deployment and validate the end-to-end pipeline behavior.

## What you can reproduce publicly
- Service health and readiness (all core modules)
- Portal submission flow and decision response
- Correlation IDs (intent_id / decision_id)
- Observability availability (metrics + traces, if enabled)

## What is intentionally excluded
- Private lab evidence packs
- Internal audit logs and operational scripts
- Institution-specific NASP credentials and infrastructure details

## Recommended validation checklist
- Submit a SLA request via Portal Backend
- Validate Decision Engine response
- Validate ML-NSMF inference output fields
- Validate SEM-CSMF semantic processing logs
- Validate Kafka decision event emission
- Validate BC-NSSMF event if Besu is enabled
