# Portal Backend

**Role.** Public entry point for SLA submission. It validates request schemas and forwards them to the TriSLA decision pipeline.

## Purpose and Responsibilities
- Accept user-facing SLA requests (template + form values)
- Validate request schemas and required fields
- Provide consistent correlation fields for tracing (intent_id)
- Forward validated requests to Decision Engine pipeline
- Return the decision response to the UI
- Handle authentication and authorization (if enabled)

## What the Module Does Not Do
- Does not make admission decisions (delegated to Decision Engine)
- Does not process semantic intent (delegated to SEM-CSMF)
- Does not perform ML predictions (delegated to ML-NSMF)
- Does not manage SLA lifecycle (delegated to SLA-Agent)

## Architecture Overview

The Portal Backend is a REST API service that acts as the public gateway:
- **Input**: HTTP POST requests with SLA request payloads
- **Output**: HTTP responses with decision outcomes
- **Protocol**: REST API (HTTP/HTTPS)

## Interfaces

### REST API Endpoints

-  — Submit a new SLA request
-  — Retrieve SLA request status
-  — Retrieve decision outcome
-  — Health check endpoint
-  — Readiness check endpoint

### Request Format

```json
{
  template_id: urllc-v1,
  requirements: {
    latency_ms: 10,
    throughput_mbps: 100,
    reliability: 0.999
  },
  metadata: {
    submitted_by: user@example.com,
    priority: high
  }
}
```

### Response Format

```json
{
  intent_id: intent-12345,
  decision: ACCEPT,
  confidence: 0.95,
  justification: All thresholds met,
  timestamp: 2024-01-24T12:00:00Z
}
```

## Configuration

### Environment Variables
- : Decision Engine service URL
- : Kafka broker addresses (for event emission)
- : JWT secret for authentication (if enabled)
- : Allowed CORS origins (comma-separated)

### Helm Configuration
The Portal Backend is deployed as part of the TriSLA Helm chart under  section in .

## Deployment Method

The Portal Backend is deployed via Helm:
```bash
helm upgrade --install trisla ./helm/trisla -n trisla -f ./helm/trisla/values.yaml
```

## Runtime Behavior

1. Receives SLA submission request from Portal Frontend
2. Validates request schema and required fields
3. Generates correlation identifier (intent_id)
4. Forwards request to Decision Engine pipeline
5. Waits for decision response
6. Returns decision outcome to Portal Frontend

## Observability Hooks

- **Prometheus metrics**: 
  - : Total API requests
  - : Request latency histogram
  - : Error counter
- **OpenTelemetry traces**: End-to-end spans from submission to decision response

## Known Issues & Resolved Errors

### Issue: ERR_NAME_NOT_RESOLVED in browser
**Symptom**: Frontend cannot reach backend  
**Resolution**: Validate NodePort, DNS resolution, and the configured backend base URL in the frontend environment configuration

### Issue: Decision Engine connection fails
**Symptom**: Backend cannot forward requests to Decision Engine  
**Resolution**: Verify  configuration and service discovery

## Integration with Other TriSLA Modules

- **Decision Engine**: Forwards SLA requests and receives decision outcomes
- **Portal Frontend**: Receives user submissions and returns decision results
- **Kafka**: Emits submission events (if configured)
- **Observability**: Emits metrics and traces

## Troubleshooting

-  in browser: validate NodePort, DNS resolution, and the configured backend base URL in the frontend
- If requests fail: verify Decision Engine connectivity and service discovery
