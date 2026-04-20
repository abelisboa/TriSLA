# SEM-CSMF Examples, Operations, and Reproducibility

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
nest = await processor.generate_nest(validated)
```

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

## 3. Interface Dispatch Example (I-01)

```python
from grpc_client import DecisionEngineClient

client = DecisionEngineClient()
await client.send_nest_metadata(
    intent_id="intent-001",
    nest_id="nest-urllc-001",
    tenant_id="tenant-001",
    service_type="URLLC",
    sla_requirements={"latency": "10ms"}
)
```

## 4. Configuration Baseline

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost/trisla

# gRPC
DECISION_ENGINE_GRPC=decision-engine:50051

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9092

# OpenTelemetry
OTLP_ENDPOINT=http://otlp-collector:4317
```

## 5. Dependencies (Conceptual Set)

- `fastapi` - API runtime
- `owlready2` - OWL ontology processing
- `spacy` - NLP parsing
- `rdflib` - RDF/OWL operations
- `grpcio` - gRPC integration
- `kafka-python` - Kafka producer
- `sqlalchemy` - persistence layer
- `opentelemetry` - traces and metrics

## 6. Suggested Test Coverage

Unit-level:

```bash
pytest tests/unit/test_sem_csmf.py
pytest tests/unit/test_ontology_parser.py
pytest tests/unit/test_nlp_parser.py
```

Integration-level:

```bash
pytest tests/integration/test_interfaces.py
pytest tests/integration/test_grpc_communication.py
```

## 7. Troubleshooting Patterns

1. **Ontology load failure**
   - Symptom: ontology package import/runtime errors
   - Action: verify ontology dependencies and ontology file path

2. **NLP model unavailable**
   - Symptom: parser initialization error
   - Action: install required spaCy model

3. **gRPC communication failure**
   - Symptom: inactive RPC channel
   - Action: validate Decision Engine endpoint and network path

4. **Kafka publish failure**
   - Symptom: producer/broker errors
   - Action: verify broker reachability and topic provisioning

## 8. Observability Anchors

Representative metrics:

- `sem_csmf_intents_total`
- `sem_csmf_processing_duration_seconds`
- `sem_csmf_ontology_validations_total`
- `sem_csmf_nests_generated_total`

Representative tracing spans:

- `process_intent`
- `validate_semantic`
- `generate_nest`
- `send_i01`
- `send_i02`

## 9. Reproducibility Checklist

- Fix ontology version and parser setup for campaign runs
- Preserve end-to-end IDs (`intent_id`, `nest_id`) across logs and events
- Store validated intent representation and generated NEST
- Record dispatch timestamps for cross-module analysis
