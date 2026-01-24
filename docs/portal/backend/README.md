# Portal Backend

**IMPORTANT**: The Portal Backend is a REST API service, not a UI component. It acts as an API orchestration and mediation layer between users (via Portal Frontend) and the TriSLA control plane.

## Purpose

The Portal Backend exists to:

1. **Accept User Requests**: Receive SLA submission requests from Portal Frontend or direct API clients
2. **Validate and Normalize**: Validate request schemas and normalize payloads before forwarding to TriSLA modules
3. **Orchestrate TriSLA Pipeline**: Coordinate the end-to-end SLA evaluation flow (SEM-CSMF → ML-NSMF → Decision Engine → BC-NSSMF)
4. **Provide Correlation**: Generate and propagate correlation identifiers (, ) for end-to-end tracing
5. **Return Standardized Responses**: Format decision outcomes and lifecycle status in a consistent API contract

## What It Does NOT Do

- **Does not implement business logic** (delegated to SEM-CSMF, ML-NSMF, Decision Engine)
- **Does not make admission decisions** (Decision Engine responsibility)
- **Does not process semantic intent** (SEM-CSMF responsibility)
- **Does not perform ML predictions** (ML-NSMF responsibility)
- **Does not manage SLA lifecycle** (SLA-Agent responsibility)
- **Does not register on-chain** (BC-NSSMF responsibility)
- **Does not render UI** (Portal Frontend responsibility)

## Role in TriSLA

The Portal Backend acts as a **public API gateway** in the TriSLA architecture:

- **Input**: HTTP POST requests with SLA request payloads from Portal Frontend
- **Output**: HTTP responses with decision outcomes, status, and metrics
- **Protocol**: REST API (HTTP/HTTPS)
- **Integration**: Orchestrates calls to SEM-CSMF, ML-NSMF, Decision Engine, BC-NSSMF via internal service layer

## Key Components

- **REST API Layer**: FastAPI application exposing  endpoints
- **Validation Layer**: Request schema validation using Pydantic models
- **NASPService**: Internal service that orchestrates calls to TriSLA modules
- **Error Mapping**: Normalizes errors from upstream modules into standardized error responses
- **Correlation ID Management**: Generates and propagates  and  for tracing

## Public Endpoints

-  — Interpret SLA intent (SEM-CSMF only)
-  — Submit SLA request (full pipeline)
-  — Retrieve SLA request status
-  — Retrieve SLA metrics
-  — Health check endpoint

## Deployment

The Portal Backend is deployed via Helm as part of the TriSLA Portal chart:



Configuration is provided through Helm values under  section in .

## Observability

- **Prometheus metrics**: Request counts, latency histograms, error counters
- **OpenTelemetry traces**: End-to-end spans from submission to decision response
- **Logs**: Structured logging for request validation, module calls, and error handling

## Documentation

- **[Complete Guide](PORTAL_BACKEND_COMPLETE_GUIDE.md)** — Comprehensive technical documentation
- **[Architecture Overview](../../ARCHITECTURE.md)** — System-level architecture
- **[Deployment Guide](../../DEPLOYMENT.md)** — Deployment procedures

## Implementation Basis

This documentation is based on the real TriSLA implementation in  and deployment configuration in .
