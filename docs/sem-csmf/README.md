# SEM-CSMF Documentation

**Semantic-enhanced Communication Service Management Function**

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
- ✅ **OWL Ontology** (integration e uso)
- ✅ **NLP** (processamento de linguagem natural)
- ✅ **NEST Generation** (Network Slice Template)
- ✅ **Interfaces** (I-01 HTTP REST, I-02 Kafka)
- ✅ **Persistence** (PostgreSQL)
- ✅ **Usage Examples** (Python code)
- ✅ **Troubleshooting** (solutions for common issues)

### [Ontology Documentation](ontology/)

The OWL ontology documentation is organized as a subfolder of SEM-CSMF:

- **[Ontology Implementation Guide](ontology/ONTOLOGY_IMPLEMENTATION_GUIDE.md)** — Complete guide of ontologia OWL, classes, propriedades, diagramas Protégé
- **[Ontology README](ontology/README.md)** — Index of documentação of ontologia

---

## 📁 Module Structure

```
apps/sem-csmf/
├── src/
│   ├── main.py                 # FastAPI Application
│   ├── intent_processor.py     # Intent Processing
│   ├── nest_generator.py       # NEST Generation
│   ├── ontology/               # OWL Ontology
│   │   ├── trisla.ttl         # Main Ontology
│   │   ├── loader.py          # Ontology Loader
│   │   ├── reasoner.py        # Reasoning Engine
│   │   ├── parser.py          # Parser de intents
│   │   └── matcher.py         # Matcher semântico
│   ├── nlp/                    # Processamento de linguagem natural
│   │   └── parser.py          # Parser NLP
│   ├── grpc_server.py          # Servidor gRPC (I-01)
│   ├── grpc_client.py          # Cliente gRPC
│   └── models/                 # Modelos Pydantic
│       ├── intent.py
│       └── nest.py
├── tests/
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## 🎯 Funcionalidades Principais

### 1. Processamento de Intents

- Recebe intents de alto nível (linguagem natural ou estruturado)
- validates semanticamente usando ontologia OWL
- Processa com NLP for extrair informações
- Gera NEST (Network Slice Template)

### 2. Ontologia OWL

- Ontologia completa in Turtle (`.ttl`)
- Classes, propriedades e indivíduos
- Reasoning semântico com Pellet
- validation de requisitos SLA

### 3. NLP (Natural Language Processing)

- Extração de tipo de slice (eMBB, URLLC, mMTC)
- Extração de requisitos de SLA
- Processamento de linguagem natural
- Fallback for processamento estruturado

### 4. Geração de NEST

- Conversão de GST for NEST
- validation contra ontologia
- Persistência in PostgreSQL
- Envio for Decision Engine (I-01)

---

## 🔗 Interfaces

### Interface I-01 (gRPC)

**Tipo:** gRPC  
**Direção:** SEM-CSMF → Decision Engine  
**Payload:** NEST + Metadados

**Documentação:** Ver [guide Completo](SEM_CSMF_COMPLETE_GUIDE.md#interface-i-01-grpc)

### Interface I-02 (Kafka)

**Tipo:** Kafka  
**Direção:** SEM-CSMF → ML-NSMF  
**topic:** `sem-csmf-nests`  
**Payload:** NEST completo

**Documentação:** Ver [guide Completo](SEM_CSMF_COMPLETE_GUIDE.md#interface-i-02-kafka)

---

## 📖 Guias Rápidos

### Início Rápido

1. **Ler o guide Completo:** [`SEM_CSMF_COMPLETE_GUIDE.md`](SEM_CSMF_COMPLETE_GUIDE.md)
2. **Entender a Ontologia:** [`ontology/ONTOLOGY_IMPLEMENTATION_GUIDE.md`](ontology/ONTOLOGY_IMPLEMENTATION_GUIDE.md)
3. **Ver Exemplos:** Ver section de exemplos no guide completo

### Uso of Ontologia

1. **Abrir no Protégé:** `apps/sem-csmf/src/ontology/trisla.ttl`
2. **Validar:** `Reasoner` → `Check consistency`
3. **Exportar Diagramas:** `Window` → `Views` → `Class hierarchy (graph)`

### Processamento de Intents

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
```

---

## 🔧 Configuração

### variables de environment

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/trisla

# gRPC
DECISION_ENGINE_GRPC=decision-engine:50051

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9092

# OpenTelemetry
OTLP_ENDPOINT=http://otlp-collector:4317
```

### Dependências

Ver `apps/sem-csmf/requirements.txt`:

- `fastapi` — Framework web
- `owlready2` — Ontologia OWL
- `spacy` — NLP
- `rdflib` — RDF/OWL
- `grpcio` — gRPC
- `kafka-python` — Kafka
- `sqlalchemy` — ORM
- `opentelemetry` — Observabilidade

---

## 🧪 Testes

### Testes Unitários

```bash
pytest tests/unit/test_sem_csmf.py
pytest tests/unit/test_ontology_parser.py
pytest tests/unit/test_nlp_parser.py
```

### Testes de Integração

```bash
pytest tests/integration/test_interfaces.py
pytest tests/integration/test_grpc_communication.py
```

---

## 📚 Referências

- **Ontologia OWL:** [`ontology/ONTOLOGY_IMPLEMENTATION_GUIDE.md`](ontology/ONTOLOGY_IMPLEMENTATION_GUIDE.md)
- **ML-NSMF:** [`../ml-nsmf/ML_NSMF_COMPLETE_GUIDE.md`](../ml-nsmf/ML_NSMF_COMPLETE_GUIDE.md)
- **Decision Engine:** Ver documentação of Decision Engine
- **README of Módulo:** [`../../apps/sem-csmf/README.md`](../../apps/sem-csmf/README.md)

---

## 🎯 Próximos Passos

1. **Ler o guide Completo** for entender todo o funcionamento
2. **Explorar a Ontologia** no Protégé
3. **Testar Processamento** de intents
4. **Validar Integrações** com outros módulos

---

**Última atualização:** 2025-01-27

