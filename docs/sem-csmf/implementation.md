# Implementação — SEM-NSMF

**Versão:** S4.0  
**Data:** 2025-01-27  
**Origem do Conteúdo:** `SEM_CSMF_COMPLETE_GUIDE.md` (seções Arquitetura, Interfaces, Persistência, Exemplos, Troubleshooting, Observabilidade)

---

## 📋 Sumário

1. [Arquitetura do Módulo](#arquitetura-do-módulo)
2. [Componentes Principais](#componentes-principais)
3. [Interfaces de Comunicação](#interfaces-de-comunicação)
4. [Persistência](#persistência)
5. [Configuração](#configuração)
6. [Exemplos de Implementação](#exemplos-de-implementação)
7. [Troubleshooting](#troubleshooting)

---

## Arquitetura do Módulo

### Estrutura de Diretórios

```
apps/sem-csmf/
├── src/
│   ├── main.py                 # Aplicação FastAPI
│   ├── intent_processor.py     # Processador principal de intents
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
│   ├── database.py             # Configuração do banco
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

### Tecnologias Utilizadas

- **Framework**: FastAPI (Python 3.10+)
- **Ontologia**: owlready2, rdflib
- **NLP**: spaCy
- **Banco de dados**: PostgreSQL com SQLAlchemy
- **Comunicação**: gRPC (grpcio), Kafka (kafka-python)
- **Observabilidade**: OpenTelemetry

---

## Componentes Principais

### 1. IntentProcessor

**Arquivo:** `src/intent_processor.py`

**Responsabilidades:**
- Orquestrar o fluxo completo de processamento
- Coordenar NLP, validação semântica e geração de NEST
- Gerenciar erros e retries

**Métodos principais:**
```python
class IntentProcessor:
    async def process_intent(self, intent: Intent) -> NEST:
        """Processa intent completo"""
        
    async def validate_semantic(self, intent: Intent) -> ValidatedIntent:
        """Valida intent semanticamente"""
        
    async def generate_nest(self, validated: ValidatedIntent) -> NEST:
        """Gera NEST a partir de intent validado"""
```

### 2. OntologyLoader

**Arquivo:** `src/ontology/loader.py`

**Responsabilidades:**
- Carregar ontologia OWL (`trisla.ttl`)
- Aplicar reasoning (Pellet)
- Cache de ontologia

**Métodos principais:**
```python
class OntologyLoader:
    def load(self, apply_reasoning: bool = True) -> None:
        """Carrega ontologia"""
        
    def get_class(self, class_name: str) -> Class:
        """Obtém classe da ontologia"""
        
    def query(self, sparql_query: str) -> List[Dict]:
        """Executa query SPARQL"""
```

### 3. SemanticReasoner

**Arquivo:** `src/ontology/reasoner.py`

**Responsabilidades:**
- Validação semântica de requisitos
- Reasoning sobre classes e propriedades
- Verificação de consistência

**Métodos principais:**
```python
class SemanticReasoner:
    def validate_sla_requirements(
        self, 
        slice_type: str, 
        sla_dict: Dict
    ) -> bool:
        """Valida requisitos de SLA"""
        
    def check_consistency(self) -> bool:
        """Verifica consistência da ontologia"""
```

### 4. NLPParser

**Arquivo:** `src/nlp/parser.py`

**Responsabilidades:**
- Extrair tipo de slice de texto
- Extrair requisitos de SLA
- Normalizar dados

**Métodos principais:**
```python
class NLPParser:
    def parse_intent_text(self, text: str) -> Dict:
        """Extrai informações de texto"""
        
    def extract_slice_type(self, text: str) -> str:
        """Extrai tipo de slice"""
        
    def extract_sla_requirements(self, text: str) -> Dict:
        """Extrai requisitos de SLA"""
```

### 5. NESTGenerator

**Arquivo:** `src/nest_generator.py`

**Responsabilidades:**
- Converter GST para NEST
- Validar NEST contra ontologia
- Persistir NEST

**Métodos principais:**
```python
class NESTGenerator:
    def generate(self, validated: ValidatedIntent) -> NEST:
        """Gera NEST"""
        
    def validate_nest(self, nest: NEST) -> bool:
        """Valida NEST"""
        
    async def persist(self, nest: NEST) -> None:
        """Persiste NEST em PostgreSQL"""
```

### 6. DecisionEngineClient

**Arquivo:** `src/grpc_client.py`

**Responsabilidades:**
- Comunicação gRPC com Decision Engine (I-01)
- Retry automático em falhas
- Timeout e circuit breaker

**Métodos principais:**
```python
class DecisionEngineClient:
    async def send_nest_metadata(
        self,
        intent_id: str,
        nest_id: str,
        metadata: Dict
    ) -> bool:
        """Envia metadados de NEST via gRPC"""
```

### 7. NESTProducer

**Arquivo:** `src/kafka_producer.py`

**Responsabilidades:**
- Publicar NESTs no Kafka (I-02)
- Retry automático em falhas
- Serialização JSON

**Métodos principais:**
```python
class NESTProducer:
    async def send_nest(self, nest: NEST) -> bool:
        """Envia NEST completo via Kafka"""
```

---

## Interfaces de Comunicação

### Interface I-01 (gRPC)

**Protocolo:** gRPC  
**Direção:** SEM-NSMF → Decision Engine  
**Endpoint:** `decision-engine:50051`  
**Serviço:** `ProcessNESTMetadata`

**Definição Protobuf (conceitual):**
```protobuf
service DecisionEngine {
  rpc ProcessNESTMetadata(NESTMetadataRequest) returns (NESTMetadataResponse);
}

message NESTMetadataRequest {
  string nest_id = 1;
  string intent_id = 2;
  string tenant_id = 3;
  string service_type = 4;
  map<string, string> sla_requirements = 5;
}

message NESTMetadataResponse {
  bool accepted = 1;
  string message = 2;
}
```

**Implementação:**
```python
from grpc_client import DecisionEngineClient

client = DecisionEngineClient(
    endpoint="decision-engine:50051",
    timeout=5.0,
    retry_attempts=3
)

await client.send_nest_metadata(
    intent_id="intent-001",
    nest_id="nest-urllc-001",
    tenant_id="tenant-001",
    service_type="URLLC",
    sla_requirements={"latency": "10ms"}
)
```

**Tratamento de Erros:**
- Retry automático (3 tentativas)
- Backoff exponencial
- Circuit breaker após 5 falhas consecutivas

### Interface I-02 (Kafka)

**Protocolo:** Kafka  
**Direção:** SEM-NSMF → ML-NSMF  
**Tópico:** `sem-csmf-nests`  
**Partições:** 3  
**Replicação:** 1

**Payload:**
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
  "domain_config": {
    "ran": {...},
    "transport": {...},
    "core": {...}
  },
  "timestamp": "2025-01-27T10:00:00Z"
}
```

**Implementação:**
```python
from kafka_producer import NESTProducer

producer = NESTProducer(
    bootstrap_servers="kafka:9092",
    topic="sem-csmf-nests",
    retry_attempts=3
)

await producer.send_nest(nest_data)
```

**Tratamento de Erros:**
- Retry automático (3 tentativas)
- Idempotência garantida
- Log de falhas

---

## Persistência

### PostgreSQL

**Configuração:**
```python
DATABASE_URL=postgresql://user:pass@localhost/trisla
```

**Modelos SQLAlchemy:**

```python
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from database import Base

class IntentModel(Base):
    __tablename__ = "intents"
    
    intent_id = Column(String, primary_key=True)
    tenant_id = Column(String, nullable=False)
    service_type = Column(String)
    sla_requirements = Column(JSON)
    created_at = Column(DateTime)

class NESTModel(Base):
    __tablename__ = "nests"
    
    nest_id = Column(String, primary_key=True)
    intent_id = Column(String, ForeignKey('intents.intent_id'))
    slice_type = Column(String)
    sla_requirements = Column(JSON)
    domain_config = Column(JSON)
    created_at = Column(DateTime)
```

**Repositório:**
```python
from repository import IntentRepository, NESTRepository

intent_repo = IntentRepository()
nest_repo = NESTRepository()

# Criar intent
intent = await intent_repo.create_intent(intent_data)

# Criar NEST
nest = await nest_repo.create_nest(nest_data)
```

---

## Configuração

### Variáveis de Ambiente

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/trisla

# gRPC
DECISION_ENGINE_GRPC=decision-engine:50051
GRPC_TIMEOUT=5.0
GRPC_RETRY_ATTEMPTS=3

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
KAFKA_TOPIC_NEST=sem-csmf-nests
KAFKA_RETRY_ATTEMPTS=3

# OpenTelemetry
OTLP_ENDPOINT=http://otlp-collector:4317
OTLP_PROTOCOL=grpc

# Ontologia
ONTOLOGY_PATH=apps/sem-csmf/src/ontology/trisla.ttl
ONTOLOGY_APPLY_REASONING=true

# NLP
SPACY_MODEL=pt_core_news_sm
```

### Dependências

**requirements.txt:**
```
fastapi==0.104.1
uvicorn==0.24.0
owlready2==0.40
rdflib==6.3.2
spacy==3.7.2
grpcio==1.59.0
kafka-python==2.0.2
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
opentelemetry-api==1.21.0
opentelemetry-sdk==1.21.0
opentelemetry-instrumentation-fastapi==0.42b0
pydantic==2.5.0
```

---

## Exemplos de Implementação

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

### Exemplo 2: Processar Intent em Linguagem Natural

```python
intent = Intent(
    intent_id="intent-002",
    tenant_id="tenant-001"
)

# Processar com NLP
validated = await processor.validate_semantic(
    intent,
    intent_text="Preciso de um slice URLLC com latência máxima de 10ms"
)

nest = await processor.generate_nest(validated)
```

### Exemplo 3: API REST Endpoint

```python
from fastapi import FastAPI, HTTPException
from models.intent import Intent

app = FastAPI()
processor = IntentProcessor()

@app.post("/api/v1/intents")
async def create_intent(intent: Intent):
    try:
        validated = await processor.validate_semantic(intent)
        nest = await processor.generate_nest(validated)
        return {"nest_id": nest.nest_id, "status": "created"}
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

---

## Troubleshooting

### Problema 1: Ontologia não carrega

**Sintoma:** `ImportError: owlready2 is not installed`

**Solução:**
```bash
pip install owlready2==0.40
```

### Problema 2: NLP não funciona

**Sintoma:** `OSError: SpaCy model not found`

**Solução:**
```bash
python -m spacy download pt_core_news_sm
python -m spacy download en_core_web_sm
```

### Problema 3: gRPC não conecta

**Sintoma:** `grpc._channel._InactiveRpcError`

**Solução:**
- Verificar se Decision Engine está rodando
- Verificar endpoint: `DECISION_ENGINE_GRPC`
- Verificar conectividade de rede
- Verificar firewall

### Problema 4: Kafka não envia

**Sintoma:** `kafka.errors.KafkaError`

**Solução:**
- Verificar se Kafka está rodando
- Verificar `KAFKA_BOOTSTRAP_SERVERS`
- Verificar tópico existe: `kafka-topics --list`
- Criar tópico se necessário: `kafka-topics --create --topic sem-csmf-nests`

### Problema 5: PostgreSQL não conecta

**Sintoma:** `sqlalchemy.exc.OperationalError`

**Solução:**
- Verificar se PostgreSQL está rodando
- Verificar `DATABASE_URL`
- Verificar credenciais
- Verificar se banco `trisla` existe

---

## Observabilidade

### Métricas Prometheus

O módulo expõe métricas via endpoint `/metrics`:

| Métrica | Tipo | Descrição |
|---------|------|-----------|
| `trisla_intents_total` | Counter | Total de intents processados |
| `trisla_nests_generated_total` | Counter | Total de NESTs gerados |
| `trisla_intent_processing_duration_seconds` | Histogram | Duração de processamento |
| `trisla_ontology_validation_duration_seconds` | Histogram | Duração de validação semântica |
| `trisla_nest_generation_duration_seconds` | Histogram | Duração de geração de NEST |
| `trisla_grpc_requests_total` | Counter | Total de requisições gRPC (I-01) |
| `trisla_kafka_messages_sent_total` | Counter | Total de mensagens Kafka (I-02) |

### Traces OpenTelemetry

Traces distribuídos são gerados para rastreabilidade:

- **Span:** `sem_nsmf.process_intent` — Processamento completo
- **Span:** `sem_nsmf.nlp_parse` — Processamento NLP
- **Span:** `sem_nsmf.validate_semantic` — Validação semântica
- **Span:** `sem_nsmf.generate_nest` — Geração de NEST
- **Span:** `sem_nsmf.send_to_decision_engine` — Envio I-01 (gRPC)
- **Span:** `sem_nsmf.send_to_ml_nsmf` — Envio I-02 (Kafka)

### Logs Estruturados

Logs estruturados incluem:
- `intent_id`: Identificador do intent
- `nest_id`: Identificador do NEST gerado
- `processing_time`: Tempo de processamento
- `validation_status`: Status da validação semântica
- `error`: Mensagem de erro (se houver)

---

## Origem do Conteúdo

Este documento foi consolidado a partir de:
- `SEM_CSMF_COMPLETE_GUIDE.md` — Seções "Arquitetura do Módulo", "Interfaces", "Persistência", "Exemplos de Uso", "Troubleshooting", "Observabilidade"

**Última atualização:** 2025-01-27  
**Versão:** S4.0

