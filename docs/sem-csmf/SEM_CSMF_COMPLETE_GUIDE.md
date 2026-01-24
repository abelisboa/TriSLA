# Guia Completo of Módulo SEM-CSMF

**Versão:** 3.5.0  
**Data:** 2025-01-27  
**Módulo:** Semantic-enhanced Communication Service Management Function

---

## 📋 Sumário

1. [Visão Geral](#visão-geral)
2. [Arquitetura of Módulo](#arquitetura-do-módulo)
3. [Pipeline de Processamento](#pipeline-de-processamento)
4. [Ontologia OWL](#ontologia-owl)
5. [NLP (Natural Language Processing)](#nlp-natural-language-processing)
6. [Geração de NEST](#geração-de-nest)
7. [Interfaces](#interfaces)
8. [Persistência](#persistência)
9. [Exemplos de Uso](#exemplos-de-uso)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral

O **SEM-CSMF (Semantic-enhanced Communication Service Management Function)** é o módulo responsável por receber intents de alto nível, validá-los semanticamente usando uma ontologia OWL, processá-los com NLP e gerar NESTs (Network Slice Templates) for provisionamento de network slices.

### Objetivos

1. **Interpretação Semântica:** Validar intents contra ontologia OWL
2. **Processamento NLP:** Extrair informações de linguagem natural
3. **Geração de NEST:** Converter intents in Network Slice Templates
4. **Integração:** Comunicar-se com Decision Engine e ML-NSMF

### Características Principais

- **Ontologia OWL:** Ontologia completa in Turtle (`.ttl`)
- **NLP:** Processamento de linguagem natural com spaCy
- **Reasoning:** Motor de reasoning semântico com Pellet
- **Persistência:** PostgreSQL for intents e NESTs
- **Observabilidade:** OpenTelemetry for traces e métricas

---

## 🏗️ Arquitetura of Módulo

### Estrutura de Diretórios

```
apps/sem-csmf/
├── src/
│   ├── main.py                 # Aplicação FastAPI
│   ├── intent_processor.py     # Processamento de intents
│   ├── nest_generator.py       # Geração de NEST
│   ├── nest_generator_db.py    # Geração com persistência
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
│   ├── grpc_client_retry.py    # Cliente com retry
│   ├── kafka_producer.py       # Producer Kafka (I-02)
│   ├── kafka_producer_retry.py # Producer com retry
│   ├── database.py             # Configuração of banco
│   ├── repository.py           # Repositório de dados
│   ├── models/                 # Modelos Pydantic
│   │   ├── intent.py
│   │   └── nest.py
│   └── models/                 # Modelos SQLAlchemy
│       └── db_models.py
├── tests/
├── Dockerfile
├── requirements.txt
└── README.md
```

### Componentes Principais

1. **IntentProcessor** — Processador principal de intents
2. **OntologyLoader** — Carregador de ontologia OWL
3. **SemanticReasoner** — Motor de reasoning semântico
4. **NLPParser** — Parser de linguagem natural
5. **NESTGenerator** — Gerador de NESTs
6. **DecisionEngineClient** — Cliente gRPC for Decision Engine

---

## ⚙️ Pipeline de Processamento

### Fluxo Completo

```
┌─────────────────┐
│  Intent Recebido│  (HTTP REST ou gRPC)
│  (Linguagem     │
│   Natural ou    │
│   Estruturado)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  NLP Parser     │  (Extrai tipo de slice e requisitos)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Ontology       │  (Valida semanticamente)
│  Parser         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Semantic       │  (Match semântico)
│  Matcher        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  NEST Generator │  (Gera Network Slice Template)
└────────┬────────┘
         │
         ├───► I-01 (gRPC) ──► Decision Engine
         │
         └───► I-02 (Kafka) ──► ML-NSMF
```

### Etapas Detalhadas

1. **Recepção de Intent**
   - HTTP REST: `POST /api/v1/intents`
   - gRPC: `ProcessIntent`

2. **Processamento NLP** (se linguagem natural)
   - Extração de tipo de slice
   - Extração de requisitos de SLA
   - Normalização de dados

3. **Validação Semântica**
   - Carregamento of ontologia OWL
   - Validação contra classes e propriedades
   - Reasoning semântico

4. **Geração de NEST**
   - Conversão de GST for NEST
   - Validação de requisitos
   - Persistência in PostgreSQL

5. **Envio for Módulos Downstream**
   - I-01 (gRPC): Metadados for Decision Engine
   - I-02 (Kafka): NEST completo for ML-NSMF

---

## 📜 Ontologia OWL

### Visão Geral

A ontologia OWL está localizada in `apps/sem-csmf/src/ontology/trisla.ttl` e é carregada dinamicamente pelo módulo.

**Documentação Completa:** [`ontology/ONTOLOGY_IMPLEMENTATION_GUIDE.md`](ontology/ONTOLOGY_IMPLEMENTATION_GUIDE.md)

### Uso no SEM-CSMF

```python
from ontology.loader import OntologyLoader
from ontology.reasoner import SemanticReasoner

# Carregar ontologia
loader = OntologyLoader()
loader.load(apply_reasoning=True)

# Criar reasoner
reasoner = SemanticReasoner(loader)
reasoner.initialize()

# Validar requisitos
sla_dict = {"latency": "10ms", "throughput": "100Mbps"}
is_valid = reasoner.validate_sla_requirements("URLLC", sla_dict)
```

### Classes Principais

- **Intent** — Intenção de serviço
- **SliceType** — Tipo de slice (eMBB, URLLC, mMTC)
- **SLA** — Service Level Agreement
- **SLO** — Service Level Objective
- **Metric** — Métricas de performance

---

## 💬 NLP (Natural Language Processing)

### Visão Geral

O NLP é usado for processar intents in linguagem natural e extrair informações estruturadas.

**Arquivo:** `apps/sem-csmf/src/nlp/parser.py`

### Funcionalidades

1. **Extração de Tipo de Slice**
   - Identifica eMBB, URLLC, mMTC
   - Usa heurísticas e spaCy

2. **Extração de Requisitos SLA**
   - Latência
   - Throughput
   - Confiabilidade
   - Jitter
   - Perda de pacotes

### Exemplo de Uso

```python
from nlp.parser import NLPParser

parser = NLPParser()

text = "Preciso de um slice URLLC com latência máxima de 10ms"
result = parser.parse_intent_text(text)

# Resultado:
# {
#   "slice_type": "URLLC",
#   "requirements": {"latency": "10ms"}
# }
```

---

## 🏗️ Geração de NEST

### Visão Geral

O NEST (Network Slice Template) é gerado a partir of intent validado semanticamente.

**Arquivo:** `apps/sem-csmf/src/nest_generator.py`

### Processo

1. **Conversão GST → NEST**
   - GST (Generic Slice Template) é convertido for NEST
   - Validação contra ontologia

2. **Persistência**
   - Salvo in PostgreSQL
   - Metadados armazenados

3. **Envio**
   - gRPC for Decision Engine (I-01)
   - Kafka for ML-NSMF (I-02)

### Exemplo de NEST

```json
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
```

---

## 🔌 Interfaces

### Interface I-01 (gRPC)

**Tipo:** gRPC  
**Direção:** SEM-CSMF → Decision Engine  
**Endpoint:** `decision-engine:50051`

**Payload:**
```protobuf
message NESTMetadata {
  string nest_id = 1;
  string intent_id = 2;
  string tenant_id = 3;
  string service_type = 4;
  map<string, string> sla_requirements = 5;
}
```

**Código:**
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

### Interface I-02 (Kafka)

**Tipo:** Kafka  
**Direção:** SEM-CSMF → ML-NSMF  
**Tópico:** `sem-csmf-nests`

**Payload:**
```json
{
  "nest_id": "nest-urllc-001",
  "intent_id": "intent-001",
  "slice_type": "URLLC",
  "sla_requirements": {...},
  "timestamp": "2025-01-27T10:00:00Z"
}
```

**Código:**
```python
from kafka_producer import NESTProducer

producer = NESTProducer()
await producer.send_nest(nest_data)
```

---

## 💾 Persistência

### PostgreSQL

**Configuração:**
```python
DATABASE_URL=postgresql://user:pass@localhost/trisla
```

**Modelos:**
- `IntentModel` — Intents armazenados
- `NESTModel` — NESTs gerados

**Repositório:**
```python
from repository import IntentRepository

repo = IntentRepository()
intent = await repo.create_intent(intent_data)
```

---

## 💡 Exemplos de Uso

### Exemplo 1: Processar Intent Estruturado

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

### Exemplo 2: Processar Intent in Linguagem Natural

```python
intent = Intent(
    intent_id="intent-002",
    sla_requirements=SLARequirements()
)

# Processar com NLP
validated = await processor.validate_semantic(
    intent,
    intent_text="Preciso de um slice URLLC com latência máxima de 10ms"
)
```

### Exemplo 3: Consultar Ontologia

```python
from ontology.loader import OntologyLoader

loader = OntologyLoader()
loader.load()

# Consultar classe
slice_type = loader.get_class("URLLC_Slice")

# Consultar indivíduo
individual = loader.get_individual("URLLC_Type")

# Query SPARQL
query = """
PREFIX : <http://trisla.org/ontology#>
SELECT ?sliceType ?latency
WHERE {
    ?sliceType a :SliceType .
    ?sliceType :hasLatency ?latency .
}
"""
results = loader.query(query)
```

---

## 🔧 Troubleshooting

### Problema 1: Ontologia não carrega

**Sintoma:** `ImportError: owlready2 is not installed`

**solution:**
```bash
pip install owlready2==0.40
```

### Problema 2: NLP não funciona

**Sintoma:** `OSError: SpaCy model not found`

**solution:**
```bash
python -m spacy download en_core_web_sm
```

### Problema 3: gRPC não conecta

**Sintoma:** `grpc._channel._InactiveRpcError`

**solution:**
- Verificar se Decision Engine está rodando
- Verificar endpoint: `DECISION_ENGINE_GRPC`
- Verificar conectividade de rede

### Problema 4: Kafka não envia

**Sintoma:** `kafka.errors.KafkaError`

**solution:**
- Verificar se Kafka está rodando
- Verificar `KAFKA_BOOTSTRAP_SERVERS`
- Verificar tópico existe

---

## 📊 Observabilidade

### Métricas Prometheus

| Métrica | Tipo | Descrição |
|---------|------|-----------|
| `sem_csmf_intents_total` | Counter | Total de intents processados |
| `sem_csmf_processing_duration_seconds` | Histogram | Tempo de processamento |
| `sem_csmf_ontology_validations_total` | Counter | Total de validações ontológicas |
| `sem_csmf_nests_generated_total` | Counter | Total de NESTs gerados |

### Traces OTLP

**Spans:**
- `process_intent` — Processamento completo
- `validate_semantic` — Validação semântica
- `generate_nest` — Geração de NEST
- `send_i01` — Envio I-01 (gRPC)
- `send_i02` — Envio I-02 (Kafka)

---

## 📚 Referências

- **Ontologia:** [`ontology/ONTOLOGY_IMPLEMENTATION_GUIDE.md`](ontology/ONTOLOGY_IMPLEMENTATION_GUIDE.md)
- **ML-NSMF:** [`../ml-nsmf/ML_NSMF_COMPLETE_GUIDE.md`](../ml-nsmf/ML_NSMF_COMPLETE_GUIDE.md)
- **Decision Engine:** Ver documentação of Decision Engine
- **README of Módulo:** [`../../apps/sem-csmf/README.md`](../../apps/sem-csmf/README.md)

---

## 🎯 Conclusão

O SEM-CSMF fornece interpretação semântica inteligente de intents usando ontologia OWL e NLP. O módulo:

- ✅ **Processa intents** com validação semântica
- ✅ **Usa ontologia OWL** for reasoning
- ✅ **Processa linguagem natural** com NLP
- ✅ **Gera NESTs** for provisionamento
- ✅ **Integra-se** com Decision Engine e ML-NSMF
- ✅ **Observável** via Prometheus e OpenTelemetry

Para mais informações, consulte:
- `apps/sem-csmf/src/intent_processor.py` — Processador principal
- `apps/sem-csmf/src/ontology/` — Ontologia OWL
- `apps/sem-csmf/src/nlp/parser.py` — Parser NLP

---

**Fim of Guia**

