# BC-NSSMF SLA Lifecycle

## Registration

```text
SLA payload
   │
   ├─ normalize SLO collection
   ├─ derive contract arguments
   ├─ sign and send transaction
   ├─ wait for receipt
   └─ return COMMITTED only when receipt.status = 1
```

Registration accepts supported current payloads and a compatibility payload. Latency, throughput, reliability, and slice information are converted to the integer contract representation when supplied through `sla_requirements`.

## Status changes

The status endpoint maps these public values to the contract representation:

```text
CREATED → ACTIVE → VIOLATED or RENEGOTIATED → CLOSED
```

The API validates the supplied status before sending a transaction. A successful response includes the new status and confirmed transaction information.

## Lookup

`GET /api/v1/get-sla/{sla_id}` reads contract state and returns the customer, service name, status, creation time, and update time. A missing SLA returns `404`.

## Error boundaries

- Invalid payload or unsupported status: `422`.
- Blockchain or signing infrastructure unavailable: `503`.
- Missing SLA: `404`.
- Unexpected processing error: `500`.

## References

- [API implementation](../../../apps/bc-nssmf/src/main.py)
- [Blockchain service](../../../apps/bc-nssmf/src/service.py)
