# NASP Adapter HTTP Interface

Base port: `8085`.

## Service and orchestration

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | Service and core connectivity status |
| `GET` | `/metrics` | Prometheus metrics |
| `GET` | `/api/v1/nasp/metrics` | Collected NASP metrics |
| `GET` | `/api/v1/metrics/multidomain` | RAN, transport, and core measurement view |
| `POST` | `/api/v1/nasp/actions` | Execute a supported NASP action |
| `POST` | `/api/v1/sla/register` | Register an SLA identifier through SEM-CSMF |
| `POST` | `/api/v1/nsi/instantiate` | Create a Network Slice Instance |
| `GET` | `/api/v1/3gpp/gate` | Run the configured readiness check |
| `POST` | `/api/v1/3gpp/gate` | Run the readiness check with SLA parameters |

## Slice-service operations

| Method | Path |
|---|---|
| `GET` | `/api/v1/slice-service-binding/resolve` |
| `POST` | `/api/v1/slice-service-binding/nssf/select` |
| `GET` | `/api/v1/slice-service-binding/nssf/status/{nsi_id}` |
| `POST` | `/api/v1/slice-service-binding/amf/observe` |
| `POST` | `/api/v1/slice-service-binding/smf/observe` |
| `POST` | `/api/v1/slice-service-binding/pdu/correlate` |
| `POST` | `/api/v1/slice-service-binding/upf/observe` |
| `POST` | `/api/v1/slice-service-binding/user-plane/correlate` |
| `POST` | `/api/v1/slice-service-binding/ran/observe` |
| `POST` | `/api/v1/slice-service-binding/access/correlate` |
| `POST` | `/api/v1/slice-service-binding/transport/observe` |
| `POST` | `/api/v1/slice-service-binding/transport/correlate` |
| `GET` | `/api/v1/slice-service-binding/binding/status/{nsi_id}` |

## Instantiate an NSI

The endpoint accepts identifiers in camelCase or snake_case and normalizes them before creating the Kubernetes resource.

```json
{
  "nsi_id": "nsi-001",
  "service_type": "URLLC",
  "tenant_id": "tenant-001",
  "nest_id": "nest-001",
  "nssai": {"sst": 1, "sd": "000001"},
  "sla_requirements": {
    "latency": "10ms",
    "throughput": "100Mbps",
    "reliability": 0.99999
  }
}
```

The adapter generates an RFC 1123-compatible identifier when needed and applies defaults for missing tenant, service profile, and `sst` values.

The endpoint implementation is in [`main.py`](../../../apps/nasp-adapter/src/main.py).
