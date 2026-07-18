# SEM-CSMF HTTP Interface

Base port: `8080`.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | Service status |
| `GET` | `/metrics` | Prometheus metrics |
| `POST` | `/api/v1/interpret` | Interpret intent text and generate a NEST |
| `POST` | `/api/v1/intents` | Process an intent and request an admission decision |
| `POST` | `/api/v1/nest` | Accept a NEST identifier and return creation status |
| `POST` | `/api/v1/auth/login` | Return a bearer token for supplied credentials |
| `GET` | `/api/v1/intents/{intent_id}` | Retrieve a stored intent |
| `POST` | `/api/v1/intents/register` | Idempotently register an SLA identifier |
| `GET` | `/api/v1/nests/{nest_id}` | Retrieve a stored NEST |
| `GET` | `/api/v1/slices` | List slices from stored NEST objects |

## Submit an intent

`POST /api/v1/intents` accepts:

```json
{
  "service_type": "URLLC",
  "intent": "Create a low-latency slice",
  "tenant_id": "tenant-001",
  "sla_requirements": {
    "latency": "10ms",
    "reliability": 0.99999,
    "jitter": "5ms"
  },
  "metadata": {}
}
```

`service_type` must be `URLLC`, `eMBB`, or `mMTC`. `intent` is required. The service generates default SLA requirements when `sla_requirements` is omitted.

The response contains `intent_id`, `status`, `nest_id`, `decision`, and `message`. It may also contain reasoning, confidence, affected domains, decision metadata, and processing latency fields.

## Interpret text

`POST /api/v1/interpret` accepts a JSON object with `intent` and optional `tenant_id`. It returns the inferred slice type, generated SLA requirements, NEST identifier, canonical SLA object, and processing latency fields.

## Authentication setting

Request authentication is controlled by `ENABLE_AUTH` and is disabled by default. When enabled, clients pass the bearer token returned by `/api/v1/auth/login`.

The request models are defined in [`models/intent.py`](../../../apps/sem-csmf/src/models/intent.py).
