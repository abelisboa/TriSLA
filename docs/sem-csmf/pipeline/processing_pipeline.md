# SEM-CSMF Processing Flow

## Structured intent submission

1. `POST /api/v1/intents` validates `service_type` and the request body.
2. Missing SLA requirements are filled from the selected service type.
3. The intent is stored through SQLAlchemy.
4. The intent processor validates the requirements and applies semantic fill.
5. A GST object is generated from the validated intent.
6. The NEST generator creates and stores the NEST.
7. A canonical SLA object and request metadata are assembled.
8. The Decision Engine client calls `POST /evaluate`.
9. SEM-CSMF returns an `IntentResponse` containing the NEST identifier and decision data.

## Text interpretation

`POST /api/v1/interpret` parses the supplied text, infers a service type when possible, creates SLA requirements, validates them, and generates GST and NEST objects. This endpoint returns the generated representation without requesting a decision.

## Service-type defaults

The implementation provides defaults when the client omits `sla_requirements`:

- `URLLC`: latency, reliability, and jitter values
- `eMBB`: throughput and reliability values
- `mMTC`: device density and coverage values

## Failure behavior

- Invalid service types return HTTP `400`.
- Missing required text returns HTTP `400`.
- Missing stored intents or NEST objects return HTTP `404`.
- Persistence or processing failures return HTTP `500`.
- A Decision Engine timeout is represented in the returned decision response by the client layer.

## Configuration

| Variable | Purpose | Default |
|---|---|---|
| `DECISION_ENGINE_URL` | Full Decision Engine evaluation URL | in-cluster service `/evaluate` URL |
| `DATABASE_URL` | SQLAlchemy database URL | `sqlite:///./trisla_sem_csmf.db` |
| `HTTP_TIMEOUT` | Decision Engine request timeout in seconds | `10.0` |
| `ENABLE_AUTH` | Require bearer authentication | `false` |
| `ENABLE_RATE_LIMIT` | Enable request rate limiting | `true` |
