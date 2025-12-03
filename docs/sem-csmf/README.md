# Documentação do SEM-CSMF

**Semantic-enhanced Communication Service Management Function**

**Versão:** 3.7.1  
**Fase:** S (SEM-CSMF)  
**Status:** Estabilizado

Este diretório contém toda a documentação do módulo SEM-CSMF do TriSLA.

---

## 📚 Documentação Disponível

### [Guia Completo do SEM-CSMF](SEM_CSMF_COMPLETE_GUIDE.md)

Guia completo que inclui:

- ✅ **Visão Geral** do módulo
- ✅ **Arquitetura** detalhada
- ✅ **Pipeline de Processamento** (Intent → NEST)
- ✅ **Ontologia OWL** (integração e uso)
- ✅ **NLP** (processamento de linguagem natural)
- ✅ **Geração de NEST** (Network Slice Template)
- ✅ **Interfaces** (I-01 HTTP REST, I-02 Kafka)
- ✅ **Persistência** (PostgreSQL)
- ✅ **Exemplos de Uso** (código Python)
- ✅ **Troubleshooting** (soluções para problemas comuns)

### [Documentação da Ontologia](ontology/)

A documentação da ontologia OWL está organizada como subpasta do SEM-CSMF:

- **[Guia de Implementação da Ontologia](ontology/ONTOLOGY_IMPLEMENTATION_GUIDE.md)** — Guia completo da ontologia OWL, classes, propriedades, diagramas Protégé
- **[README da Ontologia](ontology/README.md)** — Índice da documentação da ontologia

---

## 📁 Estrutura do Módulo

```
apps/sem-csmf/
├── src/
│   ├── main.py                 # Aplicação FastAPI
│   ├── intent_processor.py     # Processamento de intents
│   ├── nest_generator.py       # Geração de NEST
│   ├── ontology/               # Ontologia OWL
│   │   ├── trisla.ttl         # Ontologia principal
│   │   ├── loader.py          # Carregador de ontologia
│   │   ├── reasoner.py        # Motor de reasoning
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
- Valida semanticamente usando ontologia OWL
- Processa com NLP para extrair informações
- Gera NEST (Network Slice Template)

### 2. Ontologia OWL

- Ontologia completa em Turtle (`.ttl`)
- Classes, propriedades e indivíduos
- Reasoning semântico com Pellet
- Validação de requisitos SLA

### 3. NLP (Natural Language Processing)

- Extração de tipo de slice (eMBB, URLLC, mMTC)
- Extração de requisitos de SLA
- Processamento de linguagem natural
- Fallback para processamento estruturado

### 4. Geração de NEST

- Conversão de GST para NEST
- Validação contra ontologia
- Persistência em PostgreSQL
- Envio para Decision Engine (I-01)

---

## 🔗 Interfaces

### Interface I-01 (gRPC)

**Tipo:** gRPC  
**Direção:** SEM-CSMF → Decision Engine  
**Payload:** NEST + Metadados

**Documentação:** Ver [Guia Completo](SEM_CSMF_COMPLETE_GUIDE.md#interface-i-01-grpc)

### Interface I-02 (Kafka)

**Tipo:** Kafka  
**Direção:** SEM-CSMF → ML-NSMF  
**Tópico:** `sem-csmf-nests`  
**Payload:** NEST completo

**Documentação:** Ver [Guia Completo](SEM_CSMF_COMPLETE_GUIDE.md#interface-i-02-kafka)

---

## 📖 Guias Rápidos

### Início Rápido

1. **Ler o Guia Completo:** [`SEM_CSMF_COMPLETE_GUIDE.md`](SEM_CSMF_COMPLETE_GUIDE.md)
2. **Entender a Ontologia:** [`ontology/ONTOLOGY_IMPLEMENTATION_GUIDE.md`](ontology/ONTOLOGY_IMPLEMENTATION_GUIDE.md)
3. **Ver Exemplos:** Ver seção de exemplos no guia completo

### Uso da Ontologia

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

### Variáveis de Ambiente

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
- **Decision Engine:** Ver documentação do Decision Engine
- **README do Módulo:** [`../../apps/sem-csmf/README.md`](../../apps/sem-csmf/README.md)

---

## 🎯 Próximos Passos

1. **Ler o Guia Completo** para entender todo o funcionamento
2. **Explorar a Ontologia** no Protégé
3. **Testar Processamento** de intents
4. **Validar Integrações** com outros módulos

---

**Última atualização:** 2025-01-27

