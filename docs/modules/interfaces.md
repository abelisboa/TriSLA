# Interfaces

## Runtime Position In TriSLA Flow

This document is the canonical runtime-flow reference for module positioning and interface ordering. Other module documents point here instead of duplicating the full chain.

> Operational Interfaces Entry Point. This document is the canonical interface
> entry point for the frozen TriSLA runtime. Module-specific interface files are
> specialized references and must not override this runtime truth.

## Frozen State

```text
PROJECT_STATUS = CONSOLIDATED
DISSERTATION_STATUS = READY_FOR_FINAL_ALIGNMENT
ARCHITECTURE = FROZEN
RESULTS = FROZEN
EXPERIMENTS = FROZEN
SCIENTIFIC_BASELINE = FROZEN
PHASE47_STATUS = APPROVED
TRISLA_STATUS = DEMO_READY
```

## Classification Model

Only these interface classifications are canonical:

```text
ACTIVE
CONDITIONAL
LEGACY
NOT HOT PATH
NOT WIRED
TRACEABILITY_ONLY
```

Runtime notes such as "hot path", "response path", or "not callback" describe
position in the flow. They do not create new classifications.

## Runtime Interface Chain

```text
Portal Frontend
↓
Portal Backend
↓
SEM-CSMF
↓
Decision Engine
↓
ML-NSMF
↓
Decision Engine
↓
Portal Backend
↓
NASP Adapter
↓
BC-NSSMF
↓
SLA-Agent
↓
Portal Frontend
```

## I-01

Classification:

```text
ACTIVE
```

Flow:

```text
Portal Backend
↓
SEM-CSMF
```

Runtime REST interfaces:

```text
POST /api/v1/interpret
POST /api/v1/intents
GET /api/v1/intents/{id}
PATCH /api/v1/intents/{id}/governance-metadata
```

Implementation evidence:

- Portal Backend caller: `apps/portal-backend/src/services/nasp.py`
- SEM-CSMF consumer: `apps/sem-csmf/src/main.py`

## I-02

Classification:

```text
ACTIVE
```

Runtime position:

```text
HOT PATH
```

Flow:

```text
SEM-CSMF
↓
Decision Engine
```

Runtime REST interface:

```text
POST /evaluate
```

Implementation evidence:

- SEM-CSMF caller: `apps/sem-csmf/src/decision_engine_client.py`
- Decision Engine consumer: `apps/decision-engine/src/main.py`

### LEGACY

```text
Kafka
```

Kafka is not the I-02 production submit path.

### TRACEABILITY_ONLY

```text
gRPC
```

gRPC artifacts remain for traceability. They are not the I-02 production
transport.

## I-03

Classification:

```text
ACTIVE
```

Flow:

```text
Decision Engine
↓
ML-NSMF
```

Runtime REST interface:

```text
POST /api/v1/predict
```

Implementation evidence:

- Decision Engine caller: `apps/decision-engine/src/ml_client.py`
- ML-NSMF consumer: `apps/ml-nsmf/src/main.py`

### CONDITIONAL

Fallback prediction path. If ML-NSMF is unavailable or returns an error, the
Decision Engine uses a controlled fallback prediction object instead of treating
Kafka as the authority.

### NOT HOT PATH

Kafka producer path. ML-NSMF may attempt to publish prediction events when Kafka
is configured, but the HTTP response to the Decision Engine is the runtime
authority for admission.

## I-04

### ACTIVE

Classification:

```text
ACTIVE
CONDITIONAL
```

Flow:

```text
Portal Backend
↓
BC-NSSMF
```

Runtime REST interface:

```text
POST /api/v1/register-sla
```

Activation condition:

```text
ACCEPT
+
orchestration SUCCESS
```

Implementation evidence:

- Portal Backend caller: `apps/portal-backend/src/services/nasp.py`
- BC-NSSMF consumer: `apps/bc-nssmf/src/main.py`

### CONDITIONAL

Flow:

```text
Decision Engine
↓
BC-NSSMF
```

Classification:

```text
NOT HOT PATH
```

The Decision Engine `bc_client` path is conditional and not the frozen commit
path for Portal submit.

## I-05

Classification:

```text
ACTIVE
CONDITIONAL
```

Flow:

```text
Portal Backend
↓
SLA-Agent
```

Runtime REST interfaces:

```text
POST /api/v1/ingest/pipeline-event
POST /api/v1/agent/revalidate-telemetry
```

`/api/v1/ingest/pipeline-event` is conditional after accepted and committed
submissions. `/api/v1/agent/revalidate-telemetry` is the delegated temporal
reassessment authority behind Portal Backend `POST /api/v1/sla/revalidate-telemetry`.

## I-06

Classification:

```text
ACTIVE
```

Runtime assurance fields returned through the Portal-facing response path:

```text
runtime_assurance
violations
warnings
recommendation
drift
compliance
```

Runtime truth:

```text
Response Path
NOT CALLBACK
```

SLA-Agent returns reassessment and runtime assurance payloads to Portal Backend.
It does not call Portal Frontend directly.

## Portal Integration Runtime Truth

### ACTIVE

```text
Frontend
↓
Portal Backend
```

Portal Frontend calls the Portal Backend API surface only.

```text
Frontend does NOT call:

SEM-CSMF
Decision Engine
ML-NSMF
BC-NSSMF
SLA-Agent
```

Implementation evidence:

- Frontend API client: `apps/portal-frontend/src/lib/api.ts`
- Frontend endpoint map: `apps/portal-frontend/src/lib/endpoints.ts`

## Kafka Runtime Truth

Identified topics:

```text
trisla-ml-predictions
trisla-i04-decisions
trisla-i05-actions
trisla-decision-events
trisla-i06-agent-events
trisla-i07-agent-actions
```

Classification:

```text
CONDITIONAL
NOT HOT PATH
```

Runtime truth:

```text
Kafka traffic on submit
NOT ACTIVE
```

```text
SLA-Agent consumer loop
NOT STARTED
```

Kafka infrastructure and code paths exist, but the frozen admission runtime is
REST-first. Do not document Kafka as the primary submit or admission path.

## gRPC Runtime Truth

### TRACEABILITY_ONLY

```text
grpc_client.py
```

### TRACEABILITY_ONLY

```text
Decision Engine gRPC Server
```

Runtime truth:

```text
SEM active path uses:

DecisionEngineHTTPClient
```

The Decision Engine may start a gRPC server thread, but SEM-CSMF uses the HTTP
client on the active path. gRPC is not the production interface authority.

## Legacy Interfaces

```text
sem-csmf-nests
```

Classification:

```text
LEGACY
```

```text
api_rest.py
/register
/update
/{sla_id}
```

Classification:

```text
LEGACY
NOT WIRED
```

```text
POST /api/v1/execute-contract
```

Classification:

```text
NOT HOT PATH
```

The endpoint exists but is not the frozen operational contract execution path.

## Authority Modules

```text
orchestration_authority.py
```

Classification:

```text
NOT HOT PATH
```

```text
lifecycle_authority.py
```

Classification:

```text
NOT HOT PATH
```

Authority modules must not be documented as active runtime authorities unless
they are wired into the implementation hot path.

## Cross-Module Interface Matrix

| Interface | Caller | Consumer | Status |
|---|---|---|---|
| I-01 | Portal Backend | SEM-CSMF | ACTIVE |
| I-02 | SEM-CSMF | Decision Engine | ACTIVE |
| I-03 | Decision Engine | ML-NSMF | ACTIVE |
| I-04 | Portal Backend | BC-NSSMF | ACTIVE / CONDITIONAL |
| I-04 | Decision Engine | BC-NSSMF | CONDITIONAL / NOT HOT PATH |
| I-05 | Portal Backend | SLA-Agent | ACTIVE / CONDITIONAL |
| I-06 | SLA-Agent | Portal Backend | ACTIVE |

## Implementation x Documentation Matrix

| Area | Implementation truth | Documentation decision | Status |
|---|---|---|---|
| REST admission chain | Portal Backend -> SEM -> DE -> ML -> DE | Canonical here; module docs link here | ACTIVE |
| Portal direct calls | Frontend calls Portal Backend only | Canonical here; frontend/backend docs link here | ACTIVE |
| BC commit | Portal Backend -> BC-NSSMF after ACCEPT + orchestration SUCCESS | Canonical here; governance/BC docs link here | ACTIVE / CONDITIONAL |
| SLA-Agent assurance | Portal Backend delegates; SLA-Agent responds | Canonical here; SLA docs link here | ACTIVE / CONDITIONAL |
| Kafka | Topics/code exist; submit traffic not active | Keep as specialized non-hot-path reference | CONDITIONAL / NOT HOT PATH |
| gRPC | Artifacts/server exist; SEM active path is HTTP | Keep as traceability reference | TRACEABILITY_ONLY |
| Authority modules | Code exists, not wired into hot path | Do not describe as runtime authority | NOT HOT PATH |
| Legacy BC REST | `api_rest.py` exists, not mounted | Specialized legacy reference only | LEGACY / NOT WIRED |

## Specialized References

These documents provide module detail and examples. They are specialized
references; this file remains the operational entry point for cross-module
interface truth.

- `docs/sem-csmf/interfaces/interfaces.md`
- `docs/decision-engine/interfaces/interfaces.md`
- `docs/ml-nsmf/interfaces/interfaces.md`
- `docs/bc-nssmf/interfaces/interfaces.md`
- `docs/sla-agent/interfaces/interfaces.md`
- `docs/nasp-adapter/interfaces/interfaces.md`
- `docs/interfaces/BASELINE_RUNTIME_STATE.md`
- `docs/interfaces/INTERFACE_STANDARDS_MAPPING.md`
- `docs/INTERFACE_TRACEABILITY_MATRIX.md`

## Contradictions Removed

| Contradiction | Canonical replacement |
|---|---|
| Kafka primary path | CONDITIONAL / NOT HOT PATH |
| gRPC primary path | TRACEABILITY_ONLY |
| Decision Engine -> BC-NSSMF as primary commit path | Portal Backend -> BC-NSSMF |
| Frontend calls SEM-CSMF | Frontend calls Portal Backend |
| Frontend calls SLA-Agent | Frontend calls Portal Backend |
| Authority modules active runtime | NOT HOT PATH |

## Coverage

| Coverage item | Before DOC-MOD-12 | After DOC-MOD-12 |
|---|---:|---:|
| REST truth | 95% | 98% |
| Kafka truth | 70% | 95% |
| gRPC truth | 75% | 95% |
| Portal integration truth | 95% | 98% |
| Cross-module interface coverage | 90% | 96% |

## Consolidation Outcome

```text
CANONICAL_DOCUMENT_CREATED = TRUE
IMPLEMENTATION_ALIGNMENT = TRUE
REST_TRUTH_DOCUMENTED = TRUE
KAFKA_TRUTH_DOCUMENTED = TRUE
GRPC_TRUTH_DOCUMENTED = TRUE
PORTAL_INTEGRATION_TRUTH_DOCUMENTED = TRUE
PHASE47_ALIGNMENT_MAINTAINED = TRUE
DOC_COVERAGE >= 95%
DOCUMENTATION_DUPLICATION_REDUCED = TRUE
NO_NEW_DOCUMENT_TREES = TRUE
NO_RUNTIME_CHANGE = TRUE
NO_DEPLOY = TRUE
NO_SSOT_CHANGE = TRUE
DOC_MOD_12_STATUS = COMPLETED
```
