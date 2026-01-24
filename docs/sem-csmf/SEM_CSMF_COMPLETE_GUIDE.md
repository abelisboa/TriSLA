# SEM-CSMF Module Complete Guide

**Version:** 3.5.0  
**Date:** 2025-01-27  
**Module:** Semantic-Enhanced Communication Service Management Function

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Module Architecture](#module-architecture)
3. [Processing Pipeline](#processing-pipeline)
4. [OWL Ontology](#owl-ontology)
5. [NLP (Natural Language Processing)](#nlp-natural-language-processing)
6. [NEST Generation](#nest-generation)
7. [Interfaces](#interfaces)
8. [Persistence](#persistence)
9. [Usage Examples](#usage-examples)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

The **SEM-CSMF (Semantic-Enhanced Communication Service Management Function)** is the module responsible for receiving high-level intents, validating them semantically using an OWL ontology, processing them with NLP, and generating NESTs (Network Slice Templates) for network slice provisioning.

### Objectives

1. **Semantic Interpretation:** Validate intents against an OWL ontology  
2. **NLP Processing:** Extract structured information from natural language  
3. **NEST Generation:** Convert intents into Network Slice Templates  
4. **Integration:** Communicate with the Decision Engine and ML-NSMF  

### Key Features

- **OWL Ontology:** Complete ontology in Turtle format (`.ttl`)  
- **NLP:** Natural language processing using spaCy  
- **Reasoning:** Semantic reasoning engine using Pellet  
- **Persistence:** PostgreSQL for intents and NESTs  
- **Observability:** OpenTelemetry for traces and metrics  

---

## 🏗️ Module Architecture

### Directory Structure

apps/sem-csmf/
├── src/
│ ├── main.py # FastAPI application
│ ├── intent_processor.py # Intent processing
│ ├── nest_generator.py # NEST generation
│ ├── nest_generator_db.py # NEST generation with persistence
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
│ ├── grpc_client_retry.py # gRPC client with retry
│ ├── kafka_producer.py # Kafka producer (I-02)
│ ├── kafka_producer_retry.py # Kafka producer with retry
│ ├── database.py # Database configuration
│ ├── repository.py # Data repository
│ ├── models/ # Pydantic models
│ │ ├── intent.py
│ │ └── nest.py
│ └── models/ # SQLAlchemy models
│ └── db_models.py
├── tests/
├── Dockerfile
├── requirements.txt
└── README.md


### Main Components

1. **IntentProcessor** — Core intent processing component  
2. **OntologyLoader** — OWL ontology loader  
3. **SemanticReasoner** — Semantic reasoning engine  
4. **NLPParser** — Natural language parser  
5. **NESTGenerator** — NEST generator  
6. **DecisionEngineClient** — gRPC client for the Decision Engine  

---

## ⚙️ Processing Pipeline

### End-to-End Flow

┌─────────────────┐
│ Intent Received│ (HTTP REST or gRPC)
│ (Natural │
│ Language or │
│ Structured) │
└────────┬────────┘
│
▼
┌─────────────────┐
│ NLP Parser │ (Extracts slice type and requirements)
└────────┬────────┘
│
▼
┌─────────────────┐
│ Ontology │ (Semantic validation)
│ Parser │
└────────┬────────┘
│
▼
┌─────────────────┐
│ Semantic │ (Semantic matching)
│ Matcher │
└────────┬────────┘
│
▼
┌─────────────────┐
│ NEST Generator │ (Generates Network Slice Template)
└────────┬────────┘
│
├───► I-01 (gRPC) ──► Decision Engine
│
└───► I-02 (Kafka) ──► ML-NSMF


### Detailed Steps

1. **Intent Reception**
   - HTTP REST: `POST /api/v1/intents`
   - gRPC: `ProcessIntent`

2. **NLP Processing** (for natural language)
   - Slice type extraction  
   - SLA requirement extraction  
   - Data normalization  

3. **Semantic Validation**
   - OWL ontology loading  
   - Validation against classes and properties  
   - Semantic reasoning  

4. **NEST Generation**
   - GST-to-NEST conversion  
   - Requirement validation  
   - Persistence in PostgreSQL  

5. **Downstream Dispatch**
   - I-01 (gRPC): Metadata for the Decision Engine  
   - I-02 (Kafka): Complete NEST for ML-NSMF  

---

## 📜 OWL Ontology

### Overview

The OWL ontology is located at `apps/sem-csmf/src/ontology/trisla.ttl` and is dynamically loaded by the module.

**Full Documentation:** [`ontology/ONTOLOGY_IMPLEMENTATION_GUIDE.md`](ontology/ONTOLOGY_IMPLEMENTATION_GUIDE.md)

### Usage in SEM-CSMF

```python
from ontology.loader import OntologyLoader
from ontology.reasoner import SemanticReasoner

# Load ontology
loader = OntologyLoader()
loader.load(apply_reasoning=True)

# Create reasoner
reasoner = SemanticReasoner(loader)
reasoner.initialize()

# Validate requirements
sla_dict = {"latency": "10ms", "throughput": "100Mbps"}
is_valid = reasoner.validate_sla_requirements("URLLC", sla_dict)


Main Classes

Intent — Service intent

SliceType — Slice type (eMBB, URLLC, mMTC)

SLA — Service Level Agreement

SLO — Service Level Objective

Metric — Performance metrics

💬 NLP (Natural Language Processing)
Overview

NLP is used to process natural language intents and extract structured information.

File: apps/sem-csmf/src/nlp/parser.py

Capabilities

Slice Type Extraction

Identifies eMBB, URLLC, mMTC

Uses heuristics and spaCy

SLA Requirement Extraction

Latency

Throughput

Reliability

Jitter

Packet loss

Usage Example

from nlp.parser import NLPParser

parser = NLPParser()

text = "I need a URLLC slice with maximum latency of 10ms"
result = parser.parse_intent_text(text)

# Result:
# {
#   "slice_type": "URLLC",
#   "requirements": {"latency": "10ms"}
# }

🏗️ NEST Generation
Overview

The NEST (Network Slice Template) is generated from a semantically validated intent.

File: apps/sem-csmf/src/nest_generator.py

Process

GST → NEST Conversion

GST (Generic Slice Template) is converted into NEST

Ontology-based validation

Persistence

Stored in PostgreSQL

Metadata recorded

Dispatch

gRPC to Decision Engine (I-01)

Kafka to ML-NSMF (I-02)

Example NEST

{
  "nest_id": "nest-urllc-001",
  "intent_id": "intent-001",
  "slice_type": "URLLC",
  "sla_requirements": {
    "latency": "10ms",
    "throughput": "100Mbps",
    "reliability": 0.99999
  },
  "domains": ["RAN", "Transport", "Core"],
  "created_at": "2025-01-27T10:00:00Z"
}

🔌 Interfaces
Interface I-01 (gRPC)

Type: gRPC
Direction: SEM-CSMF → Decision Engine
Endpoint: decision-engine:50051

Payload:

message NESTMetadata {
  string nest_id = 1;
  string intent_id = 2;
  string tenant_id = 3;
  string service_type = 4;
  map<string, string> sla_requirements = 5;
}

Example:

from grpc_client import DecisionEngineClient

client = DecisionEngineClient()
await client.send_nest_metadata(
    intent_id="intent-001",
    nest_id="nest-urllc-001",
    tenant_id="tenant-001",
    service_type="URLLC",
    sla_requirements={"latency": "10ms"}
)

Interface I-02 (Kafka)

Type: Kafka
Direction: SEM-CSMF → ML-NSMF
Topic: sem-csmf-nests

Payload:

Interface I-02 (Kafka)

Type: Kafka
Direction: SEM-CSMF → ML-NSMF
Topic: sem-csmf-nests

Payload:

{
  "nest_id": "nest-urllc-001",
  "intent_id": "intent-001",
  "slice_type": "URLLC",
  "sla_requirements": {...},
  "timestamp": "2025-01-27T10:00:00Z"
}

💾 Persistence
PostgreSQL

Configuration:

DATABASE_URL=postgresql://user:pass@localhost/trisla


Models:

IntentModel — Stored intents

NESTModel — Generated NESTs

Repository Example:

from repository import IntentRepository

repo = IntentRepository()
intent = await repo.create_intent(intent_data)

💡 Usage Examples
Example 1: Process Structured Intent
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

Example 2: Process Natural Language Intent
intent = Intent(
    intent_id="intent-002",
    sla_requirements=SLARequirements()
)

validated = await processor.validate_semantic(
    intent,
    intent_text="I need a URLLC slice with maximum latency of 10ms"
)

🔧 Troubleshooting
Problem 1: Ontology does not load

Symptom: ImportError: owlready2 is not installed

Solution:

pip install owlready2==0.40

Problem 2: NLP does not work

Symptom: OSError: SpaCy model not found

Solution:

python -m spacy download en_core_web_sm

Problem 3: gRPC connection failure

Symptom: grpc._channel._InactiveRpcError

Solution:

Verify that the Decision Engine is running

Check endpoint DECISION_ENGINE_GRPC

Verify network connectivity

Problem 4: Kafka message not sent

Symptom: kafka.errors.KafkaError

Solution:

Verify that Kafka is running

Check KAFKA_BOOTSTRAP_SERVERS

Verify that the topic exists

📊 Observability
Prometheus Metrics
Metric	Type	Description
sem_csmf_intents_total	Counter	Total processed intents
sem_csmf_processing_duration_seconds	Histogram	Processing time
sem_csmf_ontology_validations_total	Counter	Total ontology validations
sem_csmf_nests_generated_total	Counter	Total generated NESTs
OTLP Traces

Spans:

process_intent — Full intent processing

validate_semantic — Semantic validation

generate_nest — NEST generation

send_i01 — I-01 dispatch (gRPC)

send_i02 — I-02 dispatch (Kafka)

📚 References

Ontology: ontology/ONTOLOGY_IMPLEMENTATION_GUIDE.md

ML-NSMF: ../ml-nsmf/ML_NSMF_COMPLETE_GUIDE.md

Decision Engine: See Decision Engine documentation

Module README: ../../apps/sem-csmf/README.md

🎯 Conclusion

The SEM-CSMF provides intelligent semantic interpretation of intents using OWL ontology and NLP. The module:

✅ Processes intents with semantic validation

✅ Uses OWL ontology for reasoning

✅ Processes natural language with NLP

✅ Generates NESTs for provisioning

✅ Integrates with the Decision Engine and ML-NSMF

✅ Is observable via Prometheus and OpenTelemetry

For more information, refer to:

apps/sem-csmf/src/intent_processor.py — Core processor

apps/sem-csmf/src/ontology/ — OWL ontology

apps/sem-csmf/src/nlp/parser.py — NLP parser

End of Guide
