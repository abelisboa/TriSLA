## NASP Integration (SSOT)

Source of truth:

- `apps/nasp-adapter/src/main.py`
- `apps/nasp-adapter/src/metrics_collector.py`
- `apps/portal-backend/src/services/nasp.py`
- Helm runtime values in `helm/trisla/*`

### Adapter role in the real runtime

NASP Adapter is responsible for:

- real telemetry exposure: `GET /api/v1/nasp/metrics`
- multidomain schema exposure: `GET /api/v1/metrics/multidomain`
- action execution: `POST /api/v1/nasp/actions`
- NSI orchestration: `POST /api/v1/nsi/instantiate`
- SLA registration relay: `POST /api/v1/sla/register`
- 3GPP gate validation: `GET/POST /api/v1/3gpp/gate`

### Real integration path

1. Portal submission reaches semantic/decision path.
2. On `ACCEPT`, Portal calls NASP Adapter instantiation endpoint.
3. Adapter enforces optional 3GPP gate and optional capacity accounting.
4. Adapter creates NSI via Kubernetes/CRD controller.
5. Result propagates to blockchain registration and SLA-Agent lifecycle ingestion.

### Helm/runtime parameters used by behavior

- `naspAdapter.prometheusUrl`
- `naspAdapter.capacityAccounting.*`
- `naspAdapter.gate3gpp.*`
- environment flags such as `GATE_3GPP_ENABLED`, `CAPACITY_ACCOUNTING_ENABLED`

These parameters alter runtime control branches and must be fixed in
reproducibility experiments.
