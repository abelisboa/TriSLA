# SEM-CSMF Examples, Operations, and Reproducibility

> Operational entry: [`docs/modules/sem-csmf.md`](../../modules/sem-csmf.md).
> I-01 contract: [`interfaces/interfaces.md`](../interfaces/interfaces.md).

## 1. Structured Intent Example

```python
from intent_processor import IntentProcessor
from models.intent import Intent, SliceType, SLARequirements

processor = IntentProcessor()

intent = Intent(
    intent_id="intent-001",
    tenant_id="tenant-001",
    service_type=SliceType.URLLC,
    sla_requirements=SLARequirements(
        latency="10ms",
        throughput="100Mbps",
        reliability=0.99999
    )
)

validated = await processor.validate_semantic(intent)
gst = await processor.generate_gst(validated)
```

NEST generation and I-01 dispatch occur in `main.py` (`POST /api/v1/intents`).

## 2. Natural Language Intent Example

```python
from nlp.parser import NLPParser

parser = NLPParser()
text = "I need a URLLC slice with maximum latency of 10ms"
result = parser.parse_intent_text(text)
```

Expected extraction:

```json
{
  "slice_type": "URLLC",
  "requirements": {
    "latency": "10ms"
  }
}
```

## 3. Interface Dispatch Example (I-01 HTTP — Production)

```python
from decision_engine_client import DecisionEngineHTTPClient

client = DecisionEngineHTTPClient()
response = await client.send_nest_metadata(
    intent_id="intent-001",
    nest_id="nest-urllc-001",
    tenant_id="tenant-001",
    service_type="URLLC",
    sla_requirements={"latency": "10ms", "reliability": 0.99999},
    nest_status="generated",
    metadata={"canonical_sla": {}},
    nest=nest_model,  # included when SEM_I01_NEST_TRANSMIT=true
)
```

Do **not** use `grpc_client.DecisionEngineClient` for production integrations.

## 4. Configuration Baseline

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost/trisla_sem_csmf

# Decision Engine (I-01 SSOT — HTTP)
DECISION_ENGINE_URL=http://trisla-decision-engine.trisla.svc.cluster.local:8082/evaluate

# Wave 3A NEST transmission (default true)
SEM_I01_NEST_TRANSMIT=true

# Telemetry / PRB enrichment
PORTAL_PROM_QUERY_URL=http://trisla-portal-backend.trisla.svc.cluster.local:8001/api/v1/prometheus/query
SEM_PRB_PROM_TIMEOUT=3.0

# OpenTelemetry
OTEL_EXPORTER_OTLP_ENDPOINT=http://trisla-otel-collector.trisla.svc.cluster.local:4317

# Legacy (not production hot path)
# DECISION_ENGINE_GRPC=decision-engine:50051
# KAFKA_BOOTSTRAP_SERVERS=kafka:9092
```

## 5. Dependencies (Conceptual Set)

- `fastapi` — API runtime
- `owlready2` — OWL ontology processing
- `spacy` — NLP parsing (optional)
- `sqlalchemy` — persistence
- `opentelemetry` — traces
- `requests` — I-01 HTTP client
- `grpcio`, `kafka-python` — legacy interfaces only

## 6. Test Coverage (repository)

```bash
cd apps/sem-csmf
pytest tests/test_canonical_sla.py
pytest tests/test_i01_nest_transmission.py
pytest tests/test_semantic_resolver.py
```

## 7. Troubleshooting Patterns

1. **Ontology load failure**
   - Symptom: degraded semantic validation
   - Action: verify `trisla_complete.owl` / `trisla.ttl` path and `owlready2` install

2. **NLP model unavailable**
   - Symptom: parser initialization warning
   - Action: install required spaCy model; structured payloads still work

3. **I-01 HTTP failure**
   - Symptom: `503`/`504` from `/api/v1/intents`; DE unreachable
   - Action: verify `DECISION_ENGINE_URL`, DE pod health, network policy

4. **Missing PRB in telemetry**
   - Symptom: `[PRB RESOLUTION] source=none` in SEM logs
   - Action: verify `PORTAL_PROM_QUERY_URL` and Prometheus job availability

5. **Legacy gRPC / Kafka issues**
   - Not applicable to production admission — I-01 HTTP is the only active egress

## 8. Observability Anchors

HTTP middleware metrics (active):

- `trisla_http_requests_total`
- `trisla_http_request_duration_seconds`

Custom SEM counters in `observability/metrics.py` (`trisla_sem_*`) are registered but not incremented on the current hot path.

Representative OTEL spans:

- `interpret_intent`, `process_intent`, `validate_semantic`, `generate_gst`, `generate_nest`, `send_nest_metadata_http`

## 9. Reproducibility Checklist

- Pin operational digest: `sha256:1af16f60f1414a5a630f8792caa6540b52e42d1a4f4da8631069efb2f9bb3b23` (Phase 47)
- Fix ontology version and parser setup for campaign runs
- Preserve end-to-end IDs (`intent_id`, `nest_id`) across logs and I-01 payload
- Record `metadata.canonical_sla` and dispatch timestamps for cross-module analysis
