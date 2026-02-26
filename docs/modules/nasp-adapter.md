# NASP Adapter

**Role.** NASP Adapter is the integration layer between TriSLA and the NASP (Network Automation and Service Platform) environment. It exposes a stable API for retrieving platform metrics and, when applicable, invoking platform-specific actions.

## Responsibilities
- Normalize and expose platform metrics to TriSLA modules (Decision Engine, BC-NSSMF)
- Provide a stable endpoint for metrics oracle consumers (e.g., BC-NSSMF smart contracts)
- Support integration calls required by SLA-Agent and Decision Engine
- Translate between TriSLA internal formats and NASP platform formats

## Architecture Overview

The NASP Adapter acts as a boundary service:
- **Input**: NASP platform metrics and state
- **Output**: Normalized metrics and platform action invocations
- **Protocol**: REST API (HTTP/HTTPS)

## Interfaces

### REST API Endpoints

-  — Retrieve normalized platform metrics
-  — Retrieve specific metric
-  — Invoke platform action (if supported)
-  — Health check endpoint

### Metrics Format

Metrics are returned in a normalized JSON format:
```json
{
  cpu_utilization: 0.65,
  memory_available: 0.40,
  disk_available: 0.80,
  network_latency_ms: 12.5,
  timestamp: 2024-01-24T12:00:00Z
}
```

## Configuration

### Environment Variables
- : Base URL of NASP platform API
- : Authentication token (if required)
- : Metrics refresh interval in seconds (default: 30)
- : Request timeout (default: 10)

### Helm Configuration
The NASP Adapter is deployed as part of the TriSLA Helm chart under  section in .

## Deployment Method

The NASP Adapter is deployed via Helm:
```bash
helm upgrade --install trisla ./helm/trisla -n trisla -f ./helm/trisla/values.yaml
```

Configuration is provided through Helm values, including NASP endpoint and authentication.

## Runtime Behavior

1. Periodically queries NASP platform for metrics
2. Normalizes metrics to TriSLA format
3. Exposes metrics via REST API
4. Handles platform action invocations when requested

## Observability Hooks

- **Prometheus metrics**: 
  - : Total API requests
  - : Request latency histogram
  - : Metrics refresh counter
- **OpenTelemetry traces**: Spans for upstream/downstream calls to NASP platform

## Known Issues & Resolved Errors

### Issue: Metrics appear empty
**Symptom**: API returns empty or null metrics  
**Resolution**: Verify platform connectivity, endpoint configuration, and authentication token in Helm values

### Issue: Timeout errors
**Symptom**: Requests to NASP platform timeout  
**Resolution**: Increase  or verify network connectivity to NASP endpoint

## Integration with Other TriSLA Modules

- **Decision Engine**: Provides normalized metrics for admission decisions
- **BC-NSSMF**: Serves as metrics oracle for smart contract validation
- **SLA-Agent**: Supports platform action invocations for lifecycle management

## Troubleshooting

- If metrics appear empty: verify platform connectivity and the configured endpoint in Helm values
- If authentication fails: verify  configuration
- If requests timeout: check network connectivity and increase timeout values
