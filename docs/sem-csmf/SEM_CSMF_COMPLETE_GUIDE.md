# Guia Completo do Módulo SEM-CSMF

**Versão:** 3.5.0  
**Data:** 2025-01-27  
**Módulo:** Semantic-enhanced Communication Service Management Function

---

## 📋 Sumário

1. [Visão Geral](#visão-geral)
2. [Arquitetura do Módulo](#arquitetura-do-módulo)
3. [Pipeline de Processamento](#pipeline-de-processamento)
4. [Ontologia OWL](#ontologia-owl)
5. [NLP (Natural Language Processing)](#nlp-natural-language-processing)
6. [Geração de GST e NEST](#geração-de-gst-e-nest)
7. [Integração com Outros Módulos](#integração-com-outros-módulos)
8. [Interface I-01 (gRPC)](#interface-i-01-grpc)
9. [Interface I-02 (Kafka)](#interface-i-02-kafka)
10. [Persistência de Dados](#persistência-de-dados)
11. [Exemplos de Uso](#exemplos-de-uso)
12. [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral

O **SEM-CSMF (Semantic-enhanced Communication Service Management Function)** é responsável por receber intenções de alto nível (intents) de tenants, validá-las semanticamente usando ontologias OWL, processar linguagem natural (NLP), e gerar templates de network slices (GST e NEST) conforme especificações 3GPP.

### Objetivos

1. **Interpretação Semântica:** Validar intents usando ontologia OWL formal
2. **Processamento NLP:** Extrair informações de texto em linguagem natural
3. **Geração de Templates:** Criar GST (Generic Slice Template) e NEST (Network Slice Template)
4. **Integração:** Comunicar-se com Decision Engine e ML-NSMF via interfaces padronizadas

### Características Principais

- **Ontologia OWL:** Ontologia formal completa (trisla.ttl)
- **NLP:** Processamento de linguagem natural com spaCy
- **Reasoning:** Motor de reasoning semântico (Pellet)
- **Tempo de Resposta:** < 500ms (processamento de intent)
- **Persistência:** PostgreSQL para intents e NESTs

---

## 🏗️ Arquitetura do Módulo

### Estrutura de Diretórios

```
apps/sem-csmf/
├── src/
│   ├── main.py                 # Aplicação FastAPI
│   ├── intent_processor.py     # Processador de intents
│   ├── nest_generator.py       # Gerador de NEST
│   ├── nest_generator_db.py    # Gerador com persistência
│   ├── grpc_server.py          # Servidor gRPC (I-01)
│   ├── grpc_client.py          # Cliente gRPC (I-01)
│   ├── kafka_producer.py       # Producer Kafka (I-02)
│   ├── database.py             # Configuração PostgreSQL
│   ├── repository.py           # Repositório de dados
│   ├── ontology/
│   │   ├── trisla.ttl          # Ontologia OWL completa
│   │   ├── loader.py           # Carregador de ontologia
│   │   ├── parser.py           # Parser de ontologia
│   │   ├── matcher.py          # Matcher semântico
│   │   └── reasoner.py         # Motor de reasoning
│   ├── nlp/
│   │   └── parser.py           # Parser NLP
│   ├── models/
│   │   ├── intent.py           # Modelos de intent
│   │   ├── nest.py             # Modelos de NEST
│   │   └── db_models.py        # Modelos de banco de dados
│   └── proto/
│       └── proto/
│           ├── i01_interface_pb2.py
│           └── i01_interface_pb2_grpc.py
├── tests/
├── Dockerfile
├── requirements.txt
└── README.md
```

### Componentes Principais

1. **IntentProcessor** — Processador principal de intents
2. **OntologyParser** — Parser de ontologia OWL
3. **SemanticMatcher** — Matcher semântico
4. **SemanticReasoner** — Motor de reasoning
5. **NLPParser** — Parser de linguagem natural
6. **NESTGenerator** — Gerador de NEST
7. **IntentRepository** — Repositório de intents
8. **NESTRepository** — Repositório de NESTs

---

## ⚙️ Pipeline de Processamento

### Fluxo Completo

```
┌─────────────────┐
│  Intent Recebido│  (via REST API ou gRPC)
│  (Tenant)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  NLP Processing │  (opcional, se texto fornecido)
│  (spaCy)        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Ontology Parse │  (validação semântica OWL)
│  (trisla.ttl)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Semantic Match │  (reasoning semântico)
│  (Pellet)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  GST Generation │  (Generic Slice Template)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  NEST Generation│  (Network Slice Template)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Persistência   │  (PostgreSQL)
└────────┬────────┘
         │
         ├───I-01 (gRPC)──> Decision Engine
         └───I-02 (Kafka)──> ML-NSMF
```

### Etapas Detalhadas

1. **Recepção de Intent**
   - REST API: `POST /api/v1/intents`
   - gRPC: `IntentService.CreateIntent`
   - Persistência imediata no PostgreSQL

2. **Processamento NLP (Opcional)**
   - Se `intent_text` fornecido, processar com spaCy
   - Extrair: `slice_type`, `latency`, `throughput`, `reliability`, etc.
   - Atualizar intent com informações extraídas

3. **Validação Semântica (Ontologia)**
   - Carregar ontologia OWL (`trisla.ttl`)
   - Aplicar reasoning (Pellet)
   - Validar requisitos contra ontologia
   - Inferir tipo de slice se necessário

4. **Match Semântico**
   - Comparar intent com indivíduos da ontologia
   - Validar conformidade com 3GPP
   - Gerar representação ontológica

5. **Geração de GST**
   - Criar Generic Slice Template
   - Mapear requisitos para template 3GPP
   - Validar template gerado

6. **Geração de NEST**
   - Criar Network Slice Template
   - Gerar network slices (RAN, Transport, Core)
   - Calcular recursos necessários

7. **Persistência**
   - Salvar intent no banco
   - Salvar NEST no banco
   - Criar relacionamentos

8. **Integração**
   - Enviar metadados via gRPC (I-01) para Decision Engine
   - Enviar NEST via Kafka (I-02) para ML-NSMF

---

## 📜 Ontologia OWL

### Visão Geral

A ontologia TriSLA está localizada em `apps/sem-csmf/src/ontology/trisla.ttl` e é uma ontologia OWL 2.0 completa que modela o domínio de Network Slicing.

**Documentação Completa:** [`ontology/ONTOLOGY_IMPLEMENTATION_GUIDE.md`](ontology/ONTOLOGY_IMPLEMENTATION_GUIDE.md)

### Componentes da Ontologia

1. **Classes:**
   - `Intent`, `UseCaseIntent`, `SliceRequest`
   - `Slice`, `eMBB_Slice`, `URLLC_Slice`, `mMTC_Slice`
   - `SLA`, `SLO`, `SLI`, `Metric`
   - `Domain`, `RAN`, `Transport`, `Core`
   - `GSTTemplate`, `NESTTemplate`
   - `Decision`, `RiskAssessment`
   - `MLModel`, `Prediction`, `Explanation`

2. **Propriedades:**
   - Object Properties (11 propriedades)
   - Data Properties (12 propriedades)

3. **Indivíduos:**
   - `RAN_Domain`, `Transport_Domain`, `Core_Domain`
   - `eMBB_Type`, `URLLC_Type`, `mMTC_Type`
   - `RemoteSurgery`, `XR`, `IoTMassive`

### Uso no SEM-CSMF

```python
from ontology.loader import OntologyLoader
from ontology.parser import OntologyParser
from ontology.reasoner import SemanticReasoner

# Carregar ontologia
loader = OntologyLoader()
loader.load(apply_reasoning=True)

# Parse de intent
parser = OntologyParser()
ontology_result = await parser.parse_intent(intent)

# Reasoning
reasoner = SemanticReasoner(loader)
reasoner.initialize()
inferred_type = reasoner.infer_slice_type(sla_dict)
```

---

## 💬 NLP (Natural Language Processing)

### Visão Geral

O módulo NLP permite processar intents em linguagem natural, extraindo automaticamente informações como tipo de slice e requisitos de SLA.

**Arquivo:** `apps/sem-csmf/src/nlp/parser.py`

### Funcionalidades

1. **Extração de Tipo de Slice:**
   - Identifica "URLLC", "eMBB", "mMTC" no texto
   - Usa heurísticas e spaCy

2. **Extração de Requisitos SLA:**
   - Latência: "latência máxima de 10ms"
   - Throughput: "throughput de 1Gbps"
   - Confiabilidade: "confiabilidade de 99.999%"

3. **Fallback:**
   - Se spaCy não disponível, usa mock parser
   - Funcionalidade básica mantida

### Exemplo de Uso

```python
from nlp.parser import NLPParser

parser = NLPParser()

text = "Preciso de um slice URLLC com latência máxima de 10ms e confiabilidade de 99.999%"
result = parser.parse_intent_text(text)

# Resultado:
# {
#     "slice_type": "URLLC",
#     "requirements": {
#         "latency": "10ms",
#         "reliability": 0.99999
#     }
# }
```

---

## 🏭 Geração de GST e NEST

### GST (Generic Slice Template)

**Geração:** `IntentProcessor.generate_gst()`

**Estrutura:**
```python
{
    "gst_id": "gst-001",
    "intent_id": "intent-001",
    "slice_type": "URLLC",
    "template": {
        "slice_type": "URLLC",
        "latency": "10ms",
        "throughput": "100Mbps",
        "reliability": 0.99999
    },
    "metadata": {}
}
```

### NEST (Network Slice Template)

**Geração:** `NESTGenerator.generate_nest()`

**Estrutura:**
```python
{
    "nest_id": "nest-001",
    "intent_id": "intent-001",
    "status": "GENERATED",
    "network_slices": [
        {
            "slice_id": "slice-001",
            "slice_type": "URLLC",
            "resources": {...},
            "status": "GENERATED"
        }
    ],
    "gst_id": "gst-001",
    "metadata": {}
}
```

---

## 🔌 Integração com Outros Módulos

### 1. Decision Engine (Interface I-01)

**Tipo:** gRPC  
**Endpoint:** `localhost:50051` (configurável)  
**Serviço:** `DecisionEngineService`

**Código:**
```python
from grpc_client import DecisionEngineClient

client = DecisionEngineClient()
await client.send_nest_metadata(
    intent_id="intent-001",
    nest_id="nest-001",
    tenant_id="tenant-001",
    service_type="URLLC"
)
```

### 2. ML-NSMF (Interface I-02)

**Tipo:** Kafka  
**Tópico:** `sem-csmf-nests`  
**Payload:** NEST completo

**Código:**
```python
from kafka_producer import NESTProducer

producer = NESTProducer()
await producer.send_nest(nest)
```

### 3. PostgreSQL

**Tipo:** Banco de Dados Relacional  
**Função:** Persistência de intents e NESTs

**Modelos:**
- `IntentModel` — Intents persistidos
- `NESTModel` — NESTs persistidos

---

## 📡 Interface I-01 (gRPC)

### Servidor gRPC

**Arquivo:** `apps/sem-csmf/src/grpc_server.py`

**Serviço:** `IntentService`

**Métodos:**
- `CreateIntent` — Criar intent
- `GetIntent` — Consultar intent
- `ListIntents` — Listar intents

### Cliente gRPC

**Arquivo:** `apps/sem-csmf/src/grpc_client.py`

**Classe:** `DecisionEngineClient`

**Métodos:**
- `send_nest_metadata()` — Enviar metadados de NEST

---

## 📡 Interface I-02 (Kafka)

### Producer Kafka

**Arquivo:** `apps/sem-csmf/src/kafka_producer.py`

**Tópico:** `sem-csmf-nests`

**Schema da Mensagem:**
```json
{
  "nest_id": "nest-001",
  "intent_id": "intent-001",
  "network_slices": [...],
  "metadata": {...},
  "timestamp": "2025-01-27T10:00:00Z"
}
```

---

## 💾 Persistência de Dados

### PostgreSQL

**Configuração:** `apps/sem-csmf/src/database.py`

**Modelos:**
- `IntentModel` — Tabela de intents
- `NESTModel` — Tabela de NESTs

**Repositórios:**
- `IntentRepository` — Operações CRUD de intents
- `NESTRepository` — Operações CRUD de NESTs

### Exemplo de Uso

```python
from database import get_db
from repository import IntentRepository

db = next(get_db())
repo = IntentRepository(db)

# Criar intent
intent = repo.create(intent_data)

# Consultar intent
intent = repo.get_by_id("intent-001")

# Listar intents
intents = repo.list(skip=0, limit=10)
```

---

## 💡 Exemplos de Uso

### Exemplo 1: Criar Intent via REST API

```bash
curl -X POST http://localhost:8080/api/v1/intents \
  -H "Content-Type: application/json" \
  -d '{
    "intent_id": "intent-001",
    "tenant_id": "tenant-001",
    "service_type": "URLLC",
    "sla_requirements": {
      "latency": "10ms",
      "throughput": "100Mbps",
      "reliability": 0.99999
    }
  }'
```

### Exemplo 2: Criar Intent com NLP

```python
from models.intent import Intent, SLARequirements, SliceType

intent = Intent(
    intent_id="intent-002",
    tenant_id="tenant-002",
    service_type=None,  # Será inferido pelo NLP
    sla_requirements=SLARequirements()
)

# Processar com NLP
intent_text = "Preciso de um slice URLLC com latência máxima de 10ms"
validated = await intent_processor.validate_semantic(intent, intent_text=intent_text)
```

### Exemplo 3: Consultar Intent

```python
from repository import IntentRepository

repo = IntentRepository(db)
intent = repo.get_by_id("intent-001")
```

### Exemplo 4: Gerar NEST

```python
from nest_generator import NESTGenerator

generator = NESTGenerator()
nest = await generator.generate_nest(gst)
```

---

## 🔧 Troubleshooting

### Problema 1: Ontologia não carrega

**Sintoma:** `ImportError: owlready2 is not installed`

**Solução:**
```bash
pip install owlready2==0.40
```

### Problema 2: NLP não funciona

**Sintoma:** `OSError: Can't find model 'en_core_web_sm'`

**Solução:**
```bash
python -m spacy download en_core_web_sm
```

### Problema 3: PostgreSQL não conecta

**Sintoma:** `sqlalchemy.exc.OperationalError`

**Solução:**
```bash
# Verificar variáveis de ambiente
echo $DATABASE_URL

# Verificar se PostgreSQL está rodando
docker ps | grep postgres
```

### Problema 4: gRPC não conecta

**Sintoma:** `grpc.RpcError: StatusCode.UNAVAILABLE`

**Solução:**
```bash
# Verificar se Decision Engine está rodando
curl http://localhost:8082/health

# Verificar endpoint gRPC
echo $DECISION_ENGINE_GRPC
```

---

## 📊 Observabilidade

### Métricas Prometheus

| Métrica | Tipo | Descrição |
|---------|------|-----------|
| `sem_csmf_intents_total` | Counter | Total de intents processados |
| `sem_csmf_processing_duration_seconds` | Histogram | Tempo de processamento |
| `sem_csmf_ontology_validations_total` | Counter | Total de validações ontológicas |
| `sem_csmf_nlp_processed_total` | Counter | Total de textos NLP processados |
| `sem_csmf_nests_generated_total` | Counter | Total de NESTs gerados |

### Traces OTLP

**Spans:**
- `process_intent` — Processamento completo de intent
- `validate_semantic` — Validação semântica
- `parse_intent_ontology` — Parse de ontologia
- `parse_intent_text_nlp` — Parse NLP
- `generate_gst` — Geração de GST
- `generate_nest` — Geração de NEST
- `send_nest_metadata` — Envio via gRPC
- `send_nest_kafka` — Envio via Kafka

---

## 📚 Referências

- **OWL 2.0:** https://www.w3.org/TR/owl2-overview/
- **spaCy:** https://spacy.io/
- **owlready2:** https://owlready2.readthedocs.io/
- **3GPP TS 28.541:** Management and orchestration; 5G Network Resource Model (NRM)
- **gRPC:** https://grpc.io/
- **Kafka Python:** https://kafka-python.readthedocs.io/

---

## 🎯 Conclusão

O SEM-CSMF fornece interpretação semântica inteligente de intents usando ontologias OWL, NLP e geração automática de templates. O módulo:

- ✅ **Valida semanticamente** intents usando ontologia OWL
- ✅ **Processa linguagem natural** usando spaCy
- ✅ **Gera templates** GST e NEST conforme 3GPP
- ✅ **Integra-se** com Decision Engine e ML-NSMF
- ✅ **Persiste dados** em PostgreSQL
- ✅ **Observável** via Prometheus e OpenTelemetry

Para mais informações, consulte:
- `apps/sem-csmf/src/intent_processor.py` — Processador principal
- `apps/sem-csmf/src/ontology/` — Ontologia OWL
- `apps/sem-csmf/src/nlp/parser.py` — Parser NLP
- [`ontology/ONTOLOGY_IMPLEMENTATION_GUIDE.md`](ontology/ONTOLOGY_IMPLEMENTATION_GUIDE.md) — Guia da ontologia

---

**Fim do Guia**

