# Decision Engine — Motor de Decisão TriSLA

**Versão:** 3.7.4  
**Fase:** D (Decision Engine)  
**Status:** Estabilizado

---

## 📋 Visão Geral

O **Decision Engine** é o núcleo decisório do TriSLA, responsável por:

- **Orquestrar** integração entre SEM-CSMF, ML-NSMF e BC-NSSMF
- **Tomar decisões** sobre SLAs (ACCEPT, RENEGOTIATE, REJECT)
- **Aplicar regras** de decisão baseadas em ML predictions e thresholds
- **Registrar** decisões no blockchain (quando aceitas)
- **Alta disponibilidade** com replicação

---

## 🏗️ Arquitetura

### Componentes Principais

1. **DecisionEngine** (`src/engine.py`)
   - Motor principal de decisão
   - Orquestra fluxo: SEM → ML → Regras → BC

2. **DecisionService** (`src/service.py`)
   - Camada de serviço que expõe funcionalidades via API
   - Usado por rotas REST e gRPC

3. **DecisionMaker** (`src/decision_maker.py`)
   - Toma decisões baseadas em regras e contexto
   - Ações: ACCEPT, RENEGOTIATE, REJECT

4. **RuleEngine** (`src/rule_engine.py`)
   - Engine de regras com thresholds
   - Avalia contexto contra regras de decisão

5. **SEMClient** (`src/sem_client.py`)
   - Cliente para comunicação com SEM-CSMF
   - Busca intents e NESTs

6. **MLClient** (`src/ml_client.py`)
   - Cliente para comunicação com ML-NSMF
   - Obtém previsões de risco

7. **BCClient** (`src/bc_client.py`)
   - Cliente para comunicação com BC-NSSMF
   - Registra SLAs no blockchain

---

## 🔄 Fluxo de Decisão

```
1. Intent (SEM-CSMF) → Buscar intent e NEST
2. ML Prediction (ML-NSMF) → Obter risk_score e risk_level
3. Decision Rules → Aplicar regras de decisão
4. Decision → ACCEPT / RENEGOTIATE / REJECT
5. Blockchain (BC-NSSMF) → Registrar se ACCEPT
```

---

## 📐 Regras de Decisão

### REGRA 1: Risco ALTO → REJECT
- **Condição:** `risk_level == HIGH` OU `risk_score > 0.7`
- **Ação:** REJECT

### REGRA 2: URLLC Crítico → ACCEPT
- **Condição:** `service_type == URLLC` E `risk_level == LOW` E `latency <= 10ms`
- **Ação:** ACCEPT

### REGRA 3: Risco MÉDIO → RENEGOTIATE
- **Condição:** `risk_level == MEDIUM` OU `0.4 <= risk_score <= 0.7`
- **Ação:** RENEGOTIATE

### REGRA 4: Risco BAIXO → ACCEPT
- **Condição:** `risk_level == LOW` E `risk_score < 0.4`
- **Ação:** ACCEPT

### REGRA PADRÃO: ACCEPT
- **Condição:** Nenhuma regra acima aplica
- **Ação:** ACCEPT (com aviso)

**Documentação completa:** Ver `DECISION_RULES.md`

---

## 🔌 Interfaces

### I-01 (gRPC Server)
- **Endpoint:** `0.0.0.0:50051`
- **Origem:** SEM-CSMF
- **Função:** Recebe metadados de NEST

### I-02 (Kafka Consumer)
- **Tópico:** `trisla-ml-predictions`
- **Origem:** ML-NSMF
- **Função:** Consome previsões de risco

### I-03 (Kafka Producer)
- **Tópico:** `trisla-decisions`
- **Destino:** SLA-Agent Layer
- **Função:** Produz decisões

### I-04 (Blockchain)
- **Interface:** BC-NSSMF
- **Função:** Registra SLAs no blockchain

### I-05 (HTTP REST)
- **Endpoint:** `/api/v1/evaluate`
- **Origem:** SEM-CSMF (HTTP fallback)
- **Função:** Avalia intents via HTTP

### HTTP API

- **POST `/api/v1/evaluate`**
  - Recebe intent/NEST
  - Retorna decisão

- **GET `/health`**
  - Health check do serviço

---

## ⚙️ Configuração

### Variáveis de Ambiente

```bash
# SEM-CSMF
SEM_CSMF_HTTP_URL=http://trisla-sem-csmf:8080
SEM_CSMF_GRPC_HOST=trisla-sem-csmf
SEM_CSMF_GRPC_PORT=50051

# ML-NSMF
ML_NSMF_HTTP_URL=http://trisla-ml-nsmf:8081

# BC-NSSMF
BC_ENABLED=false  # true para produção
TRISLA_RPC_URL=http://trisla-bc-nssmf:8545

# Decision Engine
GRPC_PORT=50051
HTTP_PORT=8082

# OpenTelemetry
OTLP_ENABLED=true
OTLP_ENDPOINT_GRPC=http://trisla-otel-collector:4317
```

---

## 🧪 Testes

### Testes Unitários

```bash
pytest tests/unit/test_decision_engine_rule_engine.py -v
pytest tests/unit/test_decision_engine_decision_maker.py -v
```

**Cobertura:**
- Regras de decisão (7 testes)
- DecisionMaker (6 testes)

### Testes de Integração

```bash
pytest tests/integration/test_decision_engine_integration.py -v
```

**Cobertura:**
- Integração SEM → DE
- Integração ML → DE
- Diferentes tipos de slice

### Testes E2E

```bash
pytest tests/integration/test_decision_engine_e2e.py -v
```

**Cobertura:**
- Fluxo completo: Intent → Decisão
- Performance E2E

---

## 📊 Performance

### Latência de Decisão

- **Buscar Intent (SEM):** < 100ms
- **Obter ML Prediction:** < 500ms
- **Aplicar Regras:** < 10ms
- **Registrar no BC:** < 200ms (se habilitado)
- **Total:** < 1000ms (1s)

### Otimizações

- Cache de intents frequentes (futuro)
- Circuit breaker para serviços externos (futuro)
- Processamento assíncrono (Kafka)

---

## 🔄 Alta Disponibilidade

### Replicação

O Decision Engine suporta **replicação** via Kubernetes:

```yaml
replicaCount: 2  # Múltiplas instâncias
```

### Load Balancing

- Kubernetes Service distribui requisições entre réplicas
- Health checks garantem que apenas pods saudáveis recebem tráfego

### Failover

- Se uma instância falhar, Kubernetes redireciona tráfego para outras
- Health checks detectam falhas automaticamente

---

## 📦 Estrutura de Diretórios

```
apps/decision-engine/
├── src/
│   ├── main.py              # FastAPI application
│   ├── engine.py            # DecisionEngine (motor principal)
│   ├── service.py           # DecisionService (camada de serviço)
│   ├── decision_maker.py    # DecisionMaker
│   ├── rule_engine.py       # RuleEngine
│   ├── sem_client.py        # SEMClient
│   ├── ml_client.py         # MLClient
│   ├── bc_client.py         # BCClient
│   ├── grpc_server.py       # gRPC Server (I-01)
│   ├── kafka_consumer.py    # Kafka Consumer (I-02)
│   ├── kafka_producer.py    # Kafka Producer (I-03)
│   ├── models.py            # Modelos Pydantic
│   └── config.py            # Configurações
├── proto/                   # Arquivos gRPC
├── Dockerfile
├── requirements.txt
├── README.md
└── DECISION_RULES.md        # Documentação formal das regras
```

---

## 🚀 Uso

### Exemplo de Requisição HTTP

```bash
curl -X POST http://localhost:8082/api/v1/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "intent_id": "intent-001",
    "nest_id": "nest-001",
    "context": {}
  }'
```

### Resposta

```json
{
  "decision_id": "dec-intent-001",
  "intent_id": "intent-001",
  "nest_id": "nest-001",
  "action": "AC",
  "reasoning": "SLA eMBB aceito. ML prevê risco BAIXO (score: 0.20). SLOs viáveis. Dominios: RAN, Transporte.",
  "confidence": 0.9,
  "ml_risk_score": 0.2,
  "ml_risk_level": "low",
  "slos": [
    {"name": "latency", "value": 50, "threshold": 50, "unit": "ms"},
    {"name": "throughput", "value": 100, "threshold": 100, "unit": "Mbps"}
  ],
  "domains": ["RAN", "Transporte"],
  "timestamp": "2025-01-27T00:00:00Z"
}
```

---

## 📝 Changelog

### v3.7.4 (FASE D)

- ✅ Regras de decisão otimizadas e documentadas
- ✅ Integração SEM + ML validada
- ✅ Testes unitários completos (13 testes)
- ✅ Testes de integração completos (5 testes)
- ✅ Testes E2E completos (4 testes)
- ✅ Performance validada (< 1s)
- ✅ Alta disponibilidade configurada (replicação)
- ✅ Documentação formal das regras
- ✅ Correções de datetime (timezone-aware)
- ✅ Correções de imports

---

## 🔗 Referências

- **Roadmap:** `TRISLA_PROMPTS_v3.5/roadmap/TRISLA_GUIDE_PHASED_IMPLEMENTATION.md`
- **Regras:** `apps/decision-engine/DECISION_RULES.md`
- **Tabela NASP:** `TRISLA_PROMPTS_v3.5/roadmap/05_TABELA_CONSOLIDADA_NASP.md`

---

**Status:** ✅ Estabilizado — Pronto para produção






