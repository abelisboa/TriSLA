# NASP Adapter Architecture

## Responsibilities

The NASP Adapter translates TriSLA requests into platform-facing operations. Its main responsibilities are:

- normalize and instantiate Network Slice Instance specifications;
- create and observe Kubernetes custom resources;
- register accepted SLA identifiers through SEM-CSMF;
- collect core, RAN, and transport metrics;
- run optional domain-binding observations and correlations;
- export Prometheus metrics.

## Components

| Component | Source | Responsibility |
|---|---|---|
| FastAPI application | [`src/main.py`](../../../apps/nasp-adapter/src/main.py) | HTTP routes and startup lifecycle |
| NASP client | [`src/nasp_client.py`](../../../apps/nasp-adapter/src/nasp_client.py) | Core and domain endpoint connectivity |
| NSI controller | [`src/controllers/nsi_controller.py`](../../../apps/nasp-adapter/src/controllers/nsi_controller.py) | Kubernetes Network Slice Instance operations |
| Metrics collector | [`src/metrics_collector.py`](../../../apps/nasp-adapter/src/metrics_collector.py) | Platform and multidomain measurements |
| Action executor | [`src/action_executor.py`](../../../apps/nasp-adapter/src/action_executor.py) | NASP action dispatch |
| Reservation store | [`src/reservation_store.py`](../../../apps/nasp-adapter/src/reservation_store.py) | Capacity reservations and expiry |

## Request path

```text
Portal Backend
    │ POST /api/v1/nsi/instantiate
    ▼
SLA and identifier normalization
    ▼
Readiness and capacity checks
    ▼
Kubernetes NSI resource creation
    ▼
Instantiation response
```

## Deployment

The Helm chart deploys the adapter as a `ClusterIP` service on port `8085`, assigns its service account, mounts the Kubernetes API credentials, and uses `/health` for liveness and readiness checks.
