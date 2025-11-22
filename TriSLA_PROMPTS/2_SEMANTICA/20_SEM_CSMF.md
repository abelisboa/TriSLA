# 20 – Implementação Completa do Módulo SEM-CSMF  

**TriSLA – Semantic CSMF (SEM-CSMF) com Ontologia OWL, Reasoning e PLN**

---

## 🎯 Objetivo Geral

Implementar o módulo **SEM-CSMF (Semantic Communication Service Management Function)** que converte intenções de serviço em linguagem natural (LN) ou JSON estruturado em **NEST (Network Slice Template)** conforme modelo 3GPP, utilizando:

- **Ontologia OWL** desenvolvida em Protégé
- **Reasoning** semântico (RDFLib, OWLReady2)
- **Processamento de Linguagem Natural (PLN)** para parsing de intenções
- **Pipeline completo:** Intent → Ontology → GST → NEST → Subset
- **Interface I-01** (gRPC) para comunicação com Decision Engine

---

## 📋 Requisitos Funcionais

### 1. Recepção de Intenções

- Aceitar intenções em **linguagem natural** (ex: "Preciso de um slice URLLC com latência < 10ms")
- Aceitar intenções em **JSON estruturado** (conforme schema definido)
- Validar sintaxe e semântica da intenção
- Suportar três tipos de slice: **eMBB**, **URLLC**, **mMTC**

### 2. Processamento Semântico

- **Carregar ontologia OWL** (arquivo `.owl` ou `.ttl`)
- **Mapear intenção** para classes e propriedades da ontologia
- **Aplicar reasoning** para inferir requisitos implícitos
- **Validar conformidade** com modelo 3GPP TS 28.541

### 3. Geração de NEST

- Converter ontologia validada em **GST (Generic Slice Template)**
- Gerar **NEST (Network Slice Template)** conforme 3GPP
- Extrair **Subsets** (RAN, Transport, Core)
- Gerar **metadados** para Decision Engine

### 4. Interface I-01 (gRPC)

- **Endpoint gRPC** para receber intenções
- **Endpoint gRPC** para enviar NEST e metadados ao Decision Engine
- **Validação de payloads** conforme protobuf
- **Retry logic** para comunicação resiliente

---

## 🏗️ Arquitetura do Módulo

```
apps/sem-csmf/
├── src/
│   ├── main.py                 # FastAPI application
│   ├── models/
│   │   ├── intent.py           # Modelos de intenção
│   │   ├── nest.py             # Modelos NEST 3GPP
│   │   └── db_models.py        # SQLAlchemy models
│   ├── ontology/
│   │   ├── trisla_ontology.owl # Ontologia OWL (Protégé)
│   │   ├── loader.py           # Carregador de ontologia
│   │   └── reasoner.py          # Motor de reasoning
│   ├── nlp/
│   │   ├── parser.py           # Parser de linguagem natural
│   │   ├── intent_extractor.py # Extração de requisitos
│   │   └── validators.py       # Validadores semânticos
│   ├── pipeline/
│   │   ├── intent_processor.py # Processador de intenções
│   │   ├── ontology_mapper.py  # Mapeamento para ontologia
│   │   ├── gst_generator.py     # Gerador de GST
│   │   ├── nest_generator.py   # Gerador de NEST
│   │   └── subset_extractor.py # Extrator de subsets
│   ├── grpc/
│   │   ├── service.py          # Serviço gRPC I-01
│   │   ├── client.py           # Cliente gRPC para Decision Engine
│   │   └── protos/             # Arquivos .proto
│   ├── database/
│   │   ├── connection.py       # Conexão PostgreSQL
│   │   └── migrations/         # Alembic migrations
│   ├── observability/
│   │   ├── otlp_exporter.py    # Exportador OTLP
│   │   └── metrics.py          # Métricas Prometheus
│   └── auth.py                 # Autenticação JWT
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## 🔧 Implementação Técnica

### 1. Ontologia OWL

**Arquivo:** `apps/sem-csmf/src/ontology/trisla_ontology.owl`

**Classes principais:**
- `NetworkSlice` (classe raiz)
- `eMBB_Slice`, `URLLC_Slice`, `mMTC_Slice` (subclasses)
- `SliceRequirement` (requisitos)
- `QoSProfile` (perfil de qualidade)
- `ResourceAllocation` (alocação de recursos)

**Propriedades:**
- `hasLatency` (latência máxima)
- `hasThroughput` (throughput mínimo)
- `hasReliability` (confiabilidade)
- `hasCoverage` (cobertura)
- `hasDeviceDensity` (densidade de dispositivos)

**Desenvolvimento:**
- Criar ontologia em **Protégé**
- Exportar para formato OWL 2.0
- Validar com **Pellet** ou **HermiT** reasoner

### 2. Carregamento e Reasoning

**Bibliotecas:**
- `rdflib` - Manipulação de RDF/OWL
- `owlready2` - Acesso orientado a objetos à ontologia
- `sparqlwrapper` - Queries SPARQL

**Código exemplo:**
```python
from owlready2 import *

# Carregar ontologia
onto = get_ontology("trisla_ontology.owl").load()

# Aplicar reasoning
with onto:
    sync_reasoner_pellet()

# Consultar classes
urllc_slice = onto.URLLC_Slice
```

### 3. Processamento de Linguagem Natural

**Bibliotecas:**
- `spaCy` ou `NLTK` - Processamento de texto
- `transformers` (opcional) - Modelos BERT para NER

**Pipeline NLP:**
1. **Tokenização** e **POS tagging**
2. **Named Entity Recognition (NER)** para extrair requisitos
3. **Dependency parsing** para relações
4. **Mapeamento** para classes da ontologia

### 4. Geração de NEST

**Conformidade:** 3GPP TS 28.541

**Estrutura NEST:**
```json
{
  "nestId": "string",
  "sliceType": "eMBB|URLLC|mMTC",
  "gst": {
    "sst": "integer",
    "sd": "string"
  },
  "subsets": {
    "ran": {...},
    "transport": {...},
    "core": {...}
  },
  "qosProfile": {...},
  "metadata": {...}
}
```

### 5. Interface gRPC I-01

**Arquivo proto:**
```protobuf
syntax = "proto3";

service SEMCSMFService {
  rpc ProcessIntent(IntentRequest) returns (NESTResponse);
  rpc GetNEST(NESTRequest) returns (NESTResponse);
}

message IntentRequest {
  string intent_text = 1;
  map<string, string> intent_json = 2;
  string tenant_id = 3;
}

message NESTResponse {
  string nest_id = 1;
  string nest_json = 2;
  map<string, string> metadata = 3;
  string status = 4;
}
```

---

## 📊 Persistência

### Banco de Dados (PostgreSQL)

**Tabelas:**
- `intents` - Intenções recebidas
- `nests` - NESTs gerados
- `ontology_cache` - Cache de reasoning

**Modelos SQLAlchemy:**
```python
class IntentModel(Base):
    id = Column(UUID, primary_key=True)
    intent_text = Column(Text)
    intent_json = Column(JSON)
    tenant_id = Column(String)
    status = Column(String)
    created_at = Column(DateTime)
    
class NESTModel(Base):
    id = Column(UUID, primary_key=True)
    intent_id = Column(UUID, ForeignKey('intents.id'))
    nest_json = Column(JSON)
    metadata = Column(JSON)
    created_at = Column(DateTime)
```

---

## 🔍 Observabilidade

### Métricas Prometheus

- `sem_csmf_intents_received_total` - Total de intenções recebidas
- `sem_csmf_nests_generated_total` - Total de NESTs gerados
- `sem_csmf_processing_duration_seconds` - Duração do processamento
- `sem_csmf_ontology_reasoning_duration_seconds` - Duração do reasoning
- `sem_csmf_errors_total` - Total de erros

### Traces OTLP

- Trace completo do pipeline: Intent → Ontology → GST → NEST
- Spans para cada etapa do processamento
- Logs estruturados com contexto

---

## 🧪 Testes

### Testes Unitários

- Parser de linguagem natural
- Mapeamento para ontologia
- Geração de NEST
- Validação de conformidade 3GPP

### Testes de Integração

- Fluxo completo: Intent → NEST
- Comunicação gRPC com Decision Engine
- Persistência em banco de dados

### Testes E2E

- Cenário completo com intenção real
- Validação de NEST gerado
- Verificação de metadados enviados

---

## 📝 Exemplos

### Exemplo 1: Intenção em Linguagem Natural

**Input:**
```
"Preciso de um slice URLLC com latência máxima de 10ms, 
confiabilidade de 99.999% e cobertura urbana"
```

**Output (NEST):**
```json
{
  "nestId": "nest-urllc-001",
  "sliceType": "URLLC",
  "gst": {
    "sst": 2,
    "sd": "urllc-001"
  },
  "subsets": {
    "ran": {
      "latency": {"max": 10, "unit": "ms"},
      "reliability": 0.99999
    },
    "transport": {...},
    "core": {...}
  }
}
```

### Exemplo 2: Intenção em JSON

**Input:**
```json
{
  "sliceType": "eMBB",
  "requirements": {
    "throughput": {"min": 100, "unit": "Mbps"},
    "latency": {"max": 50, "unit": "ms"},
    "coverage": "urban"
  }
}
```

---

## ✅ Critérios de Sucesso

- ✅ Ontologia OWL carregada e validada
- ✅ Reasoning funcionando corretamente
- ✅ Parser de linguagem natural extraindo requisitos
- ✅ NEST gerado conforme 3GPP TS 28.541
- ✅ Interface gRPC I-01 operacional
- ✅ Metadados enviados ao Decision Engine
- ✅ Persistência funcionando
- ✅ Observabilidade completa (métricas, traces, logs)
- ✅ Testes passando (unit, integration, E2E)

---

## 🚀 Deploy

### Docker

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Kubernetes

- Deployment com 2 replicas
- Service para gRPC (port 50051)
- Service para REST API (port 8000)
- ConfigMap para ontologia OWL
- Secret para credenciais de banco

---

## 📚 Referências

- 3GPP TS 28.541 - Management and orchestration; 5G Network Resource Model (NRM)
- OWL 2 Web Ontology Language - W3C Recommendation
- Protégé - Ontology Editor
- gRPC - High Performance RPC Framework

---

## ✔ Pronto para implementação no Cursor
