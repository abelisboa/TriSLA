# SEM-CSMF Documentation

**Semantic-Enhanced Communication Service Management Function**

**Version:** 3.7.1  
**Phase:** S (SEM-CSMF)  
**Status:** Stabilized

This directory contains all documentation for the SEM-CSMF module of TriSLA.

---

## 📚 Available Documentation

### [SEM-CSMF Complete Guide](SEM_CSMF_COMPLETE_GUIDE.md)

Complete guide that includes:

- ✅ **Overview** of the module  
- ✅ **Architecture** details  
- ✅ **Processing Pipeline** (Intent → NEST)  
- ✅ **OWL Ontology** (integration and usage)  
- ✅ **NLP** (natural language processing)  
- ✅ **NEST Generation** (Network Slice Template)  
- ✅ **Interfaces** (I-01 gRPC, I-02 Kafka)  
- ✅ **Persistence** (PostgreSQL)  
- ✅ **Usage Examples** (Python code)  
- ✅ **Troubleshooting** (solutions for common issues)  

### [Ontology Documentation](ontology/)

The OWL ontology documentation is organized as a subfolder of SEM-CSMF:

- **[Ontology Implementation Guide](ontology/ONTOLOGY_IMPLEMENTATION_GUIDE.md)** — Complete guide to the OWL ontology, including classes, properties, and Protégé diagrams  
- **[Ontology README](ontology/README.md)** — Index of the ontology documentation  

---

## 📁 Module Structure

apps/sem-csmf/
├── src/
│ ├── main.py # FastAPI application
│ ├── intent_processor.py # Intent processing
│ ├── nest_generator.py # NEST generation
│ ├── ontology/ # OWL ontology
│ │ ├── trisla.ttl # Main ontology
│ │ ├── loader.py # Ontology loader
│ │ ├── reasoner.py # Reasoning engine
│ │ ├── parser.py # Intent parser
│ │ └── matcher.py # Semantic matcher
│ ├── nlp/ # Natural language processing
│ │ └── parser.py # NLP parser
│ ├── grpc_server.py # gRPC server (I-01)
│ ├── grpc_client.py # gRPC client
│ └── models/ # Pydantic models
│ ├── intent.py
│ └── nest.py
├── tests/
├── Dockerfile
├── requirements.txt
└── README.md


---

## 🎯 Main Capabilities

### 1. Intent Processing

- Receives high-level intents (natural language or structured)
- Performs semantic validation using an OWL ontology
- Processes intents with NLP to extract information
- Generates NESTs (Network Slice Templates)

### 2. OWL Ontology

- Complete ontology in Turtle format (`.ttl`)
- Classes, properties, and individuals
- Semantic reasoning using Pellet
- SLA requirement validation

### 3. NLP (Natural Language Processing)

- Slice type extraction (eMBB, URLLC, mMTC)
- SLA requirement extraction
- Natural language processing
- Fallback to structured processing when needed

### 4. NEST Generation

- GST-to-NEST conversion
- Ontology-based validation
- Persistence in PostgreSQL
- Dispatch to the Decision Engine (I-01)

---

## 🔗 Interfaces

### Interface I-01 (gRPC)

**Type:** gRPC  
**Direction:** SEM-CSMF → Decision Engine  
**Payload:** NEST + Metadata  

**Documentation:** See the [Complete Guide](SEM_CSMF_COMPLETE_GUIDE.md#interface-i-01-grpc)

### Interface I-02 (Kafka)

**Type:** Kafka  
**Direction:** SEM-CSMF → ML-NSMF  
**Topic:** `sem-csmf-nests`  
**Payload:** Complete NEST  

**Documentation:** See the [Complete Guide](SEM_CSMF_COMPLETE_GUIDE.md#interface-i-02-kafka)

---

## 📖 Quick Guides

### Quick Start

1. **Read the Complete Guide:** [`SEM_CSMF_COMPLETE_GUIDE.md`](SEM_CSMF_COMPLETE_GUIDE.md)  
2. **Understand the Ontology:** [`ontology/ONTOLOGY_IMPLEMENTATION_GUIDE.md`](ontology/ONTOLOGY_IMPLEMENTATION_GUIDE.md)  
3. **Review Examples:** See the examples section in the complete guide  

### Ontology Usage

1. **Open in Protégé:** `apps/sem-csmf/src/ontology/trisla.ttl`  
2. **Validate Consistency:** `Reasoner` → `Check consistency`  
3. **Export Diagrams:** `Window` → `Views` → `Class hierarchy (graph)`  

### Intent Processing

```python
from intent_processor import IntentProcessor
from models.intent import Intent, SliceType, SLARequirements

processor = IntentProcessor()

intent = Intent(
    intent_id="intent-001",
    service_type=SliceType.URLLC,
    sla_requirements=SLARequirements(latency="10ms", reliability=0.99999)
)

validated = await processor.validate_semantic(intent)

🔧 Configuration
Environment Variables
# Database
DATABASE_URL=postgresql://user:pass@localhost/trisla

# gRPC
DECISION_ENGINE_GRPC=decision-engine:50051

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9092

# OpenTelemetry
OTLP_ENDPOINT=http://otlp-collector:4317

Dependencies

See apps/sem-csmf/requirements.txt:

fastapi — Web framework

owlready2 — OWL ontology

spacy — NLP

rdflib — RDF/OWL

grpcio — gRPC

kafka-python — Kafka

sqlalchemy — ORM

opentelemetry — Observability

🧪 Tests
Unit Tests
pytest tests/unit/test_sem_csmf.py
pytest tests/unit/test_ontology_parser.py
pytest tests/unit/test_nlp_parser.py

Integration Tests
pytest tests/integration/test_interfaces.py
pytest tests/integration/test_grpc_communication.py

📚 References

OWL Ontology: ontology/ONTOLOGY_IMPLEMENTATION_GUIDE.md

ML-NSMF: ../ml-nsmf/ML_NSMF_COMPLETE_GUIDE.md

Decision Engine: See Decision Engine documentation

Module README: ../../apps/sem-csmf/README.md

🎯 Next Steps

Read the Complete Guide to understand the full workflow

Explore the Ontology in Protégé

Test Intent Processing

Validate Integrations with other modules

Last updated: 2025-01-27
