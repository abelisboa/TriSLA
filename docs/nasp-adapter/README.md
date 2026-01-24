# NASP Adapter

The NASP Adapter is the integration boundary layer between TriSLA and the NASP (Network Automation and Service Platform) environment. It provides a stable, normalized API for retrieving platform metrics and executing platform-specific actions across federated network domains (RAN, Transport, Core).

## Purpose

The NASP Adapter exists to:

1. **Normalize Platform Metrics**: Collect and normalize real-time infrastructure metrics from NASP platform services (RAN, Transport, Core) into a consistent format for TriSLA consumption
2. **Execute Platform Actions**: Invoke control-plane actions on NASP services when required by SLA lifecycle management
3. **Manage Network Slice Instances**: Create and monitor Network Slice Instances (NSI) as Kubernetes Custom Resources
4. **Provide Stable Interface**: Decouple TriSLA modules from NASP platform implementation details, enabling portability and testability

## What It Does NOT Do

- **Does not make admission decisions** (Decision Engine responsibility)
- **Does not process semantic intent** (SEM-CSMF responsibility)
- **Does not perform ML predictions** (ML-NSMF responsibility)
- **Does not orchestrate SLA lifecycle** (SLA-Agent responsibility)
- **Does not register on-chain** (BC-NSSMF responsibility)

## Role in TriSLA

The NASP Adapter acts as a **boundary service** in the TriSLA control loop:

- **Input**: Requests for metrics or actions from SLA-Agent, Decision Engine, or BC-NSSMF
- **Output**: Normalized metrics and action execution results
- **Protocol**: REST API (HTTP/HTTPS)
- **Integration**: Interfaces with real NASP platform services (srsenb, open5gs UPF/AMF/SMF)

## Key Components

- **NASPClient**: HTTP client for querying NASP platform endpoints
- **MetricsCollector**: Aggregates metrics from RAN, Transport, and Core domains
- **ActionExecutor**: Executes platform actions (e.g., slice activation)
- **NSIController**: Manages Network Slice Instances as Kubernetes CRDs
- **NSIWatchController**: Monitors NSI lifecycle transitions and creates Kubernetes resources

## Public Endpoints

-  — Health check endpoint
-  — Retrieve normalized platform metrics
-  — Execute platform action
-  — Create a Network Slice Instance

## Deployment

The NASP Adapter is deployed via Helm as part of the TriSLA chart:



Configuration is provided through Helm values under  section in .

## Observability

- **Prometheus metrics**: Request counts, latency histograms
- **OpenTelemetry traces**: Spans for upstream/downstream calls to NASP platform
- **Logs**: Structured logging for metrics collection, action execution, and NSI lifecycle events

## Documentation

- **[Complete Guide](NASP_ADAPTER_COMPLETE_GUIDE.md)** — Comprehensive technical documentation
- **[Architecture Overview](../../ARCHITECTURE.md)** — System-level architecture
- **[Deployment Guide](../../DEPLOYMENT.md)** — Deployment procedures

## Implementation Basis

This documentation is based on the real TriSLA implementation in  and deployment configuration in .
