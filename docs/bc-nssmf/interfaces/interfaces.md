# BC-NSSMF Interfaces

Base service address inside the cluster:

```text
http://trisla-bc-nssmf:8083
```

## Service endpoints

| Method | Path | Request | Success behavior |
|---|---|---|---|
| `GET` | `/health` | None | Reports service mode and RPC connectivity |
| `GET` | `/health/ready` | None | Confirms RPC and signing-account readiness |
| `GET` | `/metrics` | None | Returns Prometheus text format |
| `POST` | `/api/v1/register-sla` | JSON object | Returns commit status, transaction hash, block number, and identifiers |
| `POST` | `/api/v1/update-sla-status` | `sla_id`, `status` | Commits a supported status transition |
| `GET` | `/api/v1/get-sla/{sla_id}` | Numeric path parameter | Returns stored customer, service, status, and timestamps |
| `POST` | `/api/v1/execute-contract` | `operation`, optional `function` and `args` | Validates `DEPLOY` or `EXECUTE` and returns the current operation result |

Supported status strings for `/api/v1/update-sla-status` are `CREATED`, `ACTIVE`, `VIOLATED`, `RENEGOTIATED`, and `CLOSED`.

`/api/v1/register-sla` accepts the current `slo_set` or `sla_requirements` forms and the compatibility `slos` form. An empty or invalid SLO collection is rejected.

## Read-only checks

```bash
curl http://trisla-bc-nssmf:8083/health
curl http://trisla-bc-nssmf:8083/health/ready
```

OpenAPI is available from `/openapi.json` when the service is reachable.

## Source

- [FastAPI implementation](../../../apps/bc-nssmf/src/main.py)
- [Request models](../../../apps/bc-nssmf/src/models.py)
