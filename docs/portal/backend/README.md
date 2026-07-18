# Portal Backend API

Base port: `8001`. The deployed NodePort is `32002`.

## Service and health

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/` | Service name, version, and status |
| `GET` | `/health` | Backend health |
| `GET` | `/api/v1/health` | Versioned backend health |
| `GET` | `/api/v1/health/global` | Reachability summary for platform services |
| `GET` | `/nasp/diagnostics` | Per-service connectivity details |
| `GET` | `/metrics` | Prometheus metrics |

## SLA operations

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/v1/sla/interpret` | Interpret free-form SLA text through SEM-CSMF |
| `POST` | `/api/v1/sla/submit` | Submit a structured SLA and return the admission result |
| `GET` | `/api/v1/sla/status/{sla_id}` | Retrieve SLA status and runtime fields |
| `GET` | `/api/v1/sla/metrics/{sla_id}` | Retrieve SLA metrics |
| `POST` | `/api/v1/sla/revalidate-telemetry` | Collect a new telemetry snapshot and compare it with a reference |

Interpret request:

```json
{
  "intent_text": "Create a low-latency slice",
  "tenant_id": "tenant-001"
}
```

Submit request:

```json
{
  "template_id": "URLLC",
  "tenant_id": "tenant-001",
  "form_values": {
    "service_type": "URLLC",
    "latency": "10ms",
    "reliability": 0.99999
  },
  "metadata": {}
}
```

## Module and telemetry operations

| Method | Path |
|---|---|
| `GET` | `/api/v1/modules/` |
| `GET` | `/api/v1/modules/{module}` |
| `GET` | `/api/v1/modules/{module}/metrics` |
| `GET` | `/api/v1/modules/{module}/status` |
| `GET` | `/api/v1/interfaces/ran-i1/metrics` |
| `GET` | `/api/v1/interfaces/tn-i1/metrics` |
| `GET` | `/api/v1/interfaces/cn-i1/metrics` |
| `GET` | `/api/v1/prometheus/` |
| `GET` | `/api/v1/prometheus/query` |
| `GET` | `/api/v1/prometheus/query_range` |
| `GET` | `/api/v1/prometheus/summary` |
| `GET` | `/api/v1/prometheus/targets` |

## Configuration

| Variable | Default service |
|---|---|
| `SEM_CSMF_URL` | `http://trisla-sem-csmf:8080` |
| `ML_NSMF_URL` | `http://trisla-ml-nsmf:8081` |
| `DECISION_ENGINE_URL` | `http://trisla-decision-engine:8082` |
| `BC_NSSMF_URL` | `http://trisla-bc-nssmf:8083` |
| `SLA_AGENT_URL` | `http://trisla-sla-agent-layer:8084` |
| `PROMETHEUS_URL` | `http://prometheus-operated.monitoring:9090` |

The route and schema implementations are in [`main.py`](../../../apps/portal-backend/src/main.py), [`routers/sla.py`](../../../apps/portal-backend/src/routers/sla.py), and [`schemas/sla.py`](../../../apps/portal-backend/src/schemas/sla.py).
