# NASP Adapter

**Role.** NASP Adapter is the integration layer between TriSLA and the NASP environment. It exposes a stable API for retrieving platform metrics and, when applicable, invoking platform-specific actions.

## Responsibilities
- Normalize and expose platform metrics to TriSLA modules
- Provide a stable endpoint for metrics oracle consumers (e.g., BC-NSSMF)
- Support integration calls required by SLA-Agent and Decision Engine

## Observability
- Prometheus: request/latency metrics
- OpenTelemetry: spans for upstream/downstream calls

## Troubleshooting
- If metrics appear empty: verify platform connectivity and the configured endpoint in Helm values.
