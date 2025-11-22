# TriSLA — Interfaces Internas I-01 a I-07

## 1. Introdução ao Papel das Interfaces Internas

### 1.1 Objetivo das Interfaces Internas

As interfaces internas do TriSLA (I-01 a I-07) definem os contratos de comunicação entre os módulos da arquitetura. Estas interfaces garantem:

- **Desacoplamento**: Módulos podem evoluir independentemente
- **Interoperabilidade**: Comunicação padronizada entre componentes
- **Rastreabilidade**: Fluxo de dados auditável e observável
- **Confiabilidade**: Garantias de entrega e processamento
- **Segurança**: Autenticação e autorização em todas as comunicações

### 1.2 Princípios de Design

As interfaces internas seguem os seguintes princípios:

1. **Semântica clara**: Cada interface tem propósito único e bem definido
2. **Idempotência**: Quando possível, operações são idempotentes
3. **Versionamento**: Suporte a evolução sem breaking changes
4. **Observabilidade**: Todas as comunicações são instrumentadas
5. **Segurança por padrão**: Autenticação e criptografia obrigatórias

### 1.3 Classificação das Interfaces

**Por tipo de comunicação:**

- **Síncrona**: I-01 (gRPC), I-02 (REST)
- **Assíncrona**: I-03, I-04, I-05 (Kafka)
- **Observabilidade**: I-06 (OTLP)
- **Integração externa**: I-07 (REST)

**Por criticidade:**

- **Crítica**: I-01, I-03, I-05 (fluxo principal de decisão)
- **Importante**: I-02, I-04 (suporte à decisão)
- **Observabilidade**: I-06 (monitoramento)
- **Integração**: I-07 (execução de ações)

---

## 2. Estrutura Geral

### 2.1 Tabela de Interfaces

| Interface | Protocolo | Direção | Confiabilidade | Formato | Módulo Origem | Módulo Destino | Latência p99 |
|-----------|-----------|---------|----------------|---------|---------------|----------------|--------------|
| **I-01** | gRPC | SEM-CSMF → Decision Engine | At-least-once | Protobuf | SEM-CSMF | Decision Engine | < 50ms |
| **I-02** | REST | SEM-CSMF → ML-NSMF | At-least-once | JSON | SEM-CSMF | ML-NSMF | < 100ms |
| **I-03** | Kafka | ML-NSMF → Decision Engine | Exactly-once | JSON | ML-NSMF | Decision Engine | < 10ms |
| **I-04** | Kafka | Decision Engine → BC-NSSMF | Exactly-once | JSON | Decision Engine | BC-NSSMF | < 10ms |
| **I-05** | Kafka | Decision Engine → SLA-Agent Layer | Exactly-once | JSON | Decision Engine | SLA-Agent Layer | < 10ms |
| **I-06** | REST/OTLP | SLA-Agent Layer → NASP Adapter | Best-effort | JSON/OTLP | SLA-Agent Layer | NASP Adapter | < 200ms |
| **I-07** | REST | NASP Adapter → NASP | At-least-once | JSON | NASP Adapter | NASP | < 500ms |

### 2.2 Características por Protocolo

**gRPC (I-01):**
- **Vantagens**: Alta performance, tipagem forte, streaming
- **Desvantagens**: Requer geração de código, menos flexível
- **Uso**: Comunicação síncrona crítica

**REST HTTP (I-02, I-06, I-07):**
- **Vantagens**: Simples, amplamente suportado, cacheável
- **Desvantagens**: Overhead de HTTP, sem tipagem forte
- **Uso**: APIs externas e comunicação entre módulos

**Kafka (I-03, I-04, I-05):**
- **Vantagens**: Alta throughput, persistência, replay
- **Desvantagens**: Complexidade operacional, latência adicional
- **Uso**: Mensageria assíncrona e eventos

**OTLP (I-06):**
- **Vantagens**: Padrão da indústria, rico em metadados
- **Desvantagens**: Overhead de telemetria
- **Uso**: Observabilidade e monitoramento

---

## 3. Interface I-01 — SEM-CSMF → Decision Engine

### 3.1 Propósito

A interface **I-01** é responsável por transmitir metadados de NEST (Network Slice Template) do SEM-CSMF para o Decision Engine de forma síncrona e confiável. Esta interface é crítica para o fluxo de decisão, pois é o ponto de entrada dos dados necessários para avaliação de SLA.

### 3.2 Fluxo de Dados

```
SEM-CSMF                    Decision Engine
    |                              |
    |--- NESTMetadataRequest ---->|
    |   (gRPC)                     |
    |                              | [Processa metadados]
    |                              | [Inicia decisão]
    |<-- NESTMetadataResponse ----|
    |   (decision_id)              |
    |                              |
    |--- DecisionStatusRequest --->|
    |                              | [Consulta status]
    |<-- DecisionStatusResponse --|
    |   (ACCEPT/REJECT/RENEG)     |
```

### 3.3 Protocolo e Formato

**Protocolo**: gRPC (HTTP/2)  
**Porta**: 50051  
**Formato**: Protocol Buffers (protobuf)

**Definição do serviço:**

```protobuf
syntax = "proto3";

package trisla.i01;

service DecisionEngineService {
  // Envia metadados de NEST para iniciar processo de decisão
  rpc SendNESTMetadata(NESTMetadataRequest) returns (NESTMetadataResponse);
  
  // Consulta status de uma decisão em andamento ou concluída
  rpc GetDecisionStatus(DecisionStatusRequest) returns (DecisionStatusResponse);
}
```

### 3.4 Mensagens Protobuf

#### NESTMetadataRequest

```protobuf
message NESTMetadataRequest {
  string intent_id = 1;                    // ID único do intent (obrigatório)
  string nest_id = 2;                      // ID único do NEST gerado (obrigatório)
  string tenant_id = 3;                    // ID do tenant (obrigatório)
  string service_type = 4;                 // Tipo: eMBB, URLLC, mMTC (obrigatório)
  map<string, string> sla_requirements = 5; // Requisitos de SLA (obrigatório)
  string nest_status = 6;                  // Status: generated, validated
  string timestamp = 7;                    // Timestamp ISO 8601
  map<string, string> metadata = 8;        // Metadados adicionais
}
```

**Semântica dos campos:**

- `intent_id`: Identificador único do intent de tenant. Usado para rastreabilidade.
- `nest_id`: Identificador único do NEST gerado. Vincula NEST ao intent.
- `tenant_id`: Identificador do tenant. Usado para autorização e isolamento.
- `service_type`: Tipo de serviço 5G. Determina requisitos de recursos.
- `sla_requirements`: Mapa de requisitos de SLA. Chaves comuns: "latency", "throughput", "reliability".
- `nest_status`: Estado atual do NEST. Valores: "generated", "validated", "error".
- `timestamp`: Timestamp de criação do NEST. Formato ISO 8601 UTC.
- `metadata`: Metadados adicionais. Estrutura flexível para extensibilidade.

**Exemplo de payload:**

```json
{
  "intent_id": "intent-001",
  "nest_id": "nest-intent-001",
  "tenant_id": "tenant-001",
  "service_type": "eMBB",
  "sla_requirements": {
    "latency": "10ms",
    "throughput": "100Mbps",
    "reliability": "99.9%",
    "jitter": "2ms"
  },
  "nest_status": "generated",
  "timestamp": "2025-01-19T10:30:00Z",
  "metadata": {
    "slice_count": "3",
    "priority": "high",
    "application_type": "AR"
  }
}
```

#### NESTMetadataResponse

```protobuf
message NESTMetadataResponse {
  bool success = 1;          // Indica se requisição foi aceita
  string decision_id = 2;    // ID único da decisão gerada
  string message = 3;        // Mensagem de resposta
  int32 status_code = 4;     // Código: 0=OK, >0=erro
}
```

**Semântica da resposta:**

- `success`: `true` se metadados foram aceitos e decisão foi iniciada.
- `decision_id`: Identificador único da decisão. Usado para consulta posterior.
- `message`: Mensagem descritiva do resultado.
- `status_code`: Código numérico. 0 indica sucesso, valores > 0 indicam erros.

**Exemplo de resposta:**

```json
{
  "success": true,
  "decision_id": "decision-001",
  "message": "NEST metadata received and decision initiated",
  "status_code": 0
}
```

#### DecisionStatusRequest

```protobuf
message DecisionStatusRequest {
  string decision_id = 1;    // ID da decisão a consultar (obrigatório)
  string intent_id = 2;      // ID do intent (opcional, para validação)
}
```

#### DecisionStatusResponse

```protobuf
message DecisionStatusResponse {
  string decision_id = 1;              // ID da decisão
  string intent_id = 2;                // ID do intent
  string decision = 3;                  // ACCEPT, REJECT, RENEGOTIATE
  string reason = 4;                   // Razão da decisão
  string timestamp = 5;                // Timestamp da decisão
  map<string, string> details = 6;     // Detalhes adicionais
}
```

**Valores possíveis de `decision`:**

- `ACCEPT`: NEST aceito, slice pode ser provisionado
- `REJECT`: NEST rejeitado, slice não será provisionado
- `RENEGOTIATE`: NEST requer negociação, ajustes necessários

**Exemplo de resposta:**

```json
{
  "decision_id": "decision-001",
  "intent_id": "intent-001",
  "decision": "ACCEPT",
  "reason": "SLA requirements met, ML prediction positive (score: 0.87), resources available",
  "timestamp": "2025-01-19T10:30:05Z",
  "details": {
    "ml_score": "0.87",
    "ml_confidence": "0.92",
    "estimated_latency": "8ms",
    "estimated_throughput": "1.2Gbps",
    "resource_utilization": "0.65"
  }
}
```

### 3.5 Garantias e Comportamento

**Garantias de entrega:**
- **At-least-once**: Mensagem pode ser entregue múltiplas vezes
- **Timeout**: 5 segundos
- **Retry**: Cliente deve implementar retry com backoff exponencial

**Comportamento em caso de erro:**

| Erro | Código gRPC | Ação do Cliente |
|------|-------------|-----------------|
| Timeout | DEADLINE_EXCEEDED | Retry com backoff |
| Serviço indisponível | UNAVAILABLE | Retry após delay |
| Dados inválidos | INVALID_ARGUMENT | Não retry, corrigir dados |
| Não autorizado | UNAUTHENTICATED | Verificar credenciais |

**Idempotência:**
- **Não idempotente**: Cada chamada cria nova decisão
- **Recomendação**: Usar `nest_id` como chave de idempotência no lado do servidor

---

## 4. Interface I-02 — SEM-CSMF → ML-NSMF

### 4.1 Propósito

A interface **I-02** transmite NEST gerado do SEM-CSMF para o ML-NSMF para análise de viabilidade e predição de violações de SLA. Esta interface permite que o ML-NSMF avalie a viabilidade do NEST antes da decisão final.

### 4.2 Fluxo de Dados

```
SEM-CSMF                    ML-NSMF
    |                            |
    |--- POST /api/v1/nest ---->|
    |   (NEST completo)          |
    |                            | [Analisa NEST]
    |                            | [Coleta métricas]
    |                            | [Gera predição]
    |<-- 200 OK ----------------|
    |   (prediction_id)         |
    |                            |
    |--- GET /predictions/{id} ->|
    |                            | [Retorna predição]
    |<-- PredictionResponse ----|
    |   (viability_score)        |
```

### 4.3 Protocolo e Formato

**Protocolo**: REST HTTP/1.1  
**Porta**: 8081  
**Formato**: JSON

### 4.4 Endpoints

#### POST /api/v1/nest

**Descrição**: Envia NEST gerado para análise de viabilidade.

**Request:**

```http
POST /api/v1/nest HTTP/1.1
Host: ml-nsmf:8081
Content-Type: application/json
Authorization: Bearer <JWT_TOKEN>

{
  "nest_id": "nest-intent-001",
  "intent_id": "intent-001",
  "tenant_id": "tenant-001",
  "service_type": "eMBB",
  "network_slices": [
    {
      "slice_id": "slice-001",
      "slice_type": "eMBB",
      "resources": {
        "cpu": 4,
        "memory": "8Gi",
        "bandwidth": "1Gbps"
      },
      "sla_requirements": {
        "latency": "10ms",
        "throughput": "100Mbps",
        "reliability": "99.9%"
      }
    }
  ],
  "metadata": {
    "priority": "high",
    "generated_at": "2025-01-19T10:30:00Z"
  }
}
```

**Response (200 OK):**

```json
{
  "nest_id": "nest-intent-001",
  "status": "received",
  "message": "NEST received and queued for prediction",
  "prediction_id": "pred-001",
  "estimated_completion": "2025-01-19T10:30:05Z",
  "timestamp": "2025-01-19T10:30:01Z"
}
```

**Response (400 Bad Request):**

```json
{
  "error": "Invalid NEST format",
  "message": "Missing required field: network_slices",
  "status_code": 400,
  "details": {
    "missing_fields": ["network_slices"],
    "received_fields": ["nest_id", "intent_id"]
  }
}
```

#### GET /api/v1/predictions/{prediction_id}

**Descrição**: Consulta resultado de uma predição.

**Request:**

```http
GET /api/v1/predictions/pred-001 HTTP/1.1
Host: ml-nsmf:8081
Authorization: Bearer <JWT_TOKEN>
```

**Response (200 OK):**

```json
{
  "prediction_id": "pred-001",
  "nest_id": "nest-intent-001",
  "status": "completed",
  "viability_score": 0.87,
  "recommendation": "ACCEPT",
  "confidence": 0.92,
  "explanation": {
    "top_features": [
      {
        "feature": "latency_margin",
        "importance": 0.35,
        "value": 0.85,
        "contribution": "positive"
      },
      {
        "feature": "resource_ratio",
        "importance": 0.28,
        "value": 0.78,
        "contribution": "positive"
      },
      {
        "feature": "network_capacity",
        "importance": 0.22,
        "value": 0.65,
        "contribution": "neutral"
      }
    ],
    "shap_values": {
      "latency_margin": 0.15,
      "resource_ratio": 0.12,
      "network_capacity": 0.08,
      "historical_compliance": 0.05
    },
    "risk_factors": [
      {
        "factor": "high_network_utilization",
        "severity": "medium",
        "impact": "May affect latency during peak hours"
      }
    ]
  },
  "metrics_used": {
    "cpu_utilization": 0.65,
    "memory_utilization": 0.70,
    "network_bandwidth_available": 500,
    "active_slices": 15,
    "historical_violation_rate": 0.05
  },
  "timestamp": "2025-01-19T10:30:05Z"
}
```

### 4.5 Semântica da Comunicação

**Modelo de requisição-resposta:**
- **Síncrono**: Cliente aguarda resposta
- **Assíncrono opcional**: Cliente pode consultar resultado posteriormente via `prediction_id`

**Garantias:**
- **At-least-once**: Requisição pode ser reenviada
- **Idempotência**: Enviar mesmo NEST múltiplas vezes produz mesmo resultado (baseado em `nest_id`)

**Validação:**
- NEST deve conter pelo menos um `network_slice`
- Cada slice deve ter `resources` e `sla_requirements` definidos
- `service_type` deve ser um dos valores válidos: "eMBB", "URLLC", "mMTC"

---

## 5. Interface I-03 — ML-NSMF → Decision Engine

### 5.1 Propósito

A interface **I-03** transmite predições de viabilidade de SLA do ML-NSMF para o Decision Engine de forma assíncrona via Kafka. Esta interface é crítica para o processo de decisão, fornecendo insights de machine learning que influenciam a decisão final.

### 5.2 Fluxo de Dados

```
ML-NSMF                    Kafka                    Decision Engine
    |                         |                            |
    |--- Prediction Message -->|                            |
    |   (trisla-ml-predictions)|                            |
    |                         |--- Consume Message ------->|
    |                         |                            | [Processa predição]
    |                         |                            | [Usa na decisão]
```

### 5.3 Protocolo e Formato

**Protocolo**: Apache Kafka  
**Tópico**: `trisla-ml-predictions`  
**Formato**: JSON (serializado como UTF-8)

**Configuração do tópico:**

```yaml
# Configuração Kafka Topic
name: trisla-ml-predictions
partitions: 3
replication-factor: 3
retention-ms: 604800000  # 7 dias
compression-type: gzip
cleanup-policy: delete
```

### 5.4 Estrutura da Mensagem

**Schema completo:**

```json
{
  "interface": "I-03",
  "source": "ml-nsmf",
  "destination": "decision-engine",
  "prediction_id": "pred-001",
  "nest_id": "nest-intent-001",
  "intent_id": "intent-001",
  "tenant_id": "tenant-001",
  "viability_score": 0.87,
  "recommendation": "ACCEPT",
  "confidence": 0.92,
  "explanation": {
    "top_features": [
      {
        "feature": "latency_margin",
        "importance": 0.35,
        "value": 0.85,
        "contribution": "positive"
      }
    ],
    "shap_values": {
      "latency_margin": 0.15,
      "resource_ratio": 0.12
    }
  },
  "metrics_used": {
    "cpu_utilization": 0.65,
    "memory_utilization": 0.70,
    "network_bandwidth_available": 500
  },
  "model_version": "1.0.0",
  "timestamp": "2025-01-19T10:30:05Z",
  "version": "1.0.0"
}
```

### 5.5 Campos e Semântica

**Campos obrigatórios:**

- `interface`: Sempre "I-03"
- `source`: Sempre "ml-nsmf"
- `destination`: Sempre "decision-engine"
- `prediction_id`: ID único da predição
- `nest_id`: ID do NEST analisado
- `viability_score`: Score de viabilidade (0.0 a 1.0)
- `recommendation`: ACCEPT, REJECT ou RENEGOTIATE
- `timestamp`: Timestamp ISO 8601

**Semântica dos scores:**

- `viability_score`:
  - **0.0 - 0.5**: Baixa viabilidade, recomendação REJECT
  - **0.5 - 0.7**: Viabilidade média, recomendação RENEGOTIATE
  - **0.7 - 1.0**: Alta viabilidade, recomendação ACCEPT

- `confidence`:
  - **0.0 - 0.7**: Baixa confiança na predição
  - **0.7 - 0.9**: Confiança média
  - **0.9 - 1.0**: Alta confiança

### 5.6 Garantias de Entrega

**Kafka Exactly-Once Semantics:**

- **Idempotência**: Producer idempotente habilitado
- **Transações**: Mensagens são enviadas em transação
- **Acknowledgment**: `acks=all` (aguarda confirmação de todos os replicas)

**Retentativas automáticas:**

```python
from kafka import KafkaProducer
from kafka.errors import KafkaError

producer = KafkaProducer(
    bootstrap_servers=['kafka:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    acks='all',  # Aguardar confirmação de todos os replicas
    retries=3,   # Retry automático
    max_in_flight_requests_per_connection=1,  # Exactly-once
    enable_idempotence=True,  # Idempotência
    transaction_id='ml-nsmf-producer'  # Transações
)

# Iniciar transação
producer.begin_transaction()

try:
    future = producer.send('trisla-ml-predictions', value=message)
    record_metadata = future.get(timeout=10)
    producer.commit_transaction()
except KafkaError as e:
    producer.abort_transaction()
    raise e
```

---

## 6. Interface I-04 — Decision Engine → BC-NSSMF

### 6.1 Propósito

A interface **I-04** transmite decisões tomadas pelo Decision Engine para o BC-NSSMF para registro imutável em blockchain. Esta interface garante auditabilidade e rastreabilidade de todas as decisões de SLA.

### 6.2 Fluxo de Dados

```
Decision Engine            Kafka                    BC-NSSMF
    |                         |                         |
    |--- Decision Message ---->|                         |
    |   (trisla-i04-decisions)|                         |
    |                         |--- Consume Message ---->|
    |                         |                         | [Valida assinatura]
    |                         |                         | [Registra em blockchain]
    |                         |<-- Confirmation --------|
    |                         |   (transaction_hash)    |
```

### 6.3 Protocolo e Formato

**Protocolo**: Apache Kafka  
**Tópico**: `trisla-i04-decisions`  
**Formato**: JSON (serializado como UTF-8)

**Configuração do tópico:**

```yaml
name: trisla-i04-decisions
partitions: 3
replication-factor: 3
retention-ms: 2592000000  # 30 dias (maior retenção para auditoria)
compression-type: gzip
cleanup-policy: delete
```

### 6.4 Estrutura da Mensagem

**Schema completo:**

```json
{
  "interface": "I-04",
  "source": "decision-engine",
  "destination": "bc-nssmf",
  "decision_id": "decision-001",
  "intent_id": "intent-001",
  "nest_id": "nest-intent-001",
  "tenant_id": "tenant-001",
  "decision": "ACCEPT",
  "reason": "SLA requirements met, ML prediction positive",
  "sla_data": {
    "latency": "10ms",
    "throughput": "100Mbps",
    "reliability": "99.9%"
  },
  "ml_prediction": {
    "prediction_id": "pred-001",
    "viability_score": 0.87,
    "confidence": 0.92,
    "recommendation": "ACCEPT"
  },
  "decision_rules": {
    "rule_1": "ML score > 0.7",
    "rule_2": "Resources available",
    "rule_3": "SLA requirements feasible"
  },
  "timestamp": "2025-01-19T10:30:10Z",
  "signature": "0x1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b",
  "version": "1.0.0"
}
```

### 6.5 Assinatura Digital

**Propósito**: Garantir integridade e autenticidade da decisão.

**Algoritmo**: HMAC-SHA256

**Processo de assinatura:**

```python
import hashlib
import hmac
import json

def sign_decision(decision_data: dict, secret_key: str) -> str:
    """
    Assina decisão antes de enviar para blockchain.
    
    Args:
        decision_data: Dados da decisão (sem signature)
        secret_key: Chave secreta compartilhada
    
    Returns:
        Assinatura hexadecimal (prefixed com 0x)
    """
    # Remover signature se existir
    data_to_sign = {k: v for k, v in decision_data.items() if k != 'signature'}
    
    # Serializar de forma determinística
    message = json.dumps(data_to_sign, sort_keys=True, separators=(',', ':'))
    
    # Calcular HMAC
    signature = hmac.new(
        secret_key.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return f"0x{signature}"

def verify_decision_signature(signed_decision: dict, secret_key: str) -> bool:
    """
    Verifica assinatura de decisão recebida.
    
    Args:
        signed_decision: Decisão com signature
        secret_key: Chave secreta compartilhada
    
    Returns:
        True se assinatura válida, False caso contrário
    """
    received_signature = signed_decision.get('signature', '')
    if not received_signature:
        return False
    
    # Remover signature para recalcular
    data_to_verify = {k: v for k, v in signed_decision.items() if k != 'signature'}
    message = json.dumps(data_to_verify, sort_keys=True, separators=(',', ':'))
    
    expected_signature = hmac.new(
        secret_key.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    expected_with_prefix = f"0x{expected_signature}"
    
    return hmac.compare_digest(received_signature, expected_with_prefix)
```

### 6.6 Integração com Blockchain

**Processo no BC-NSSMF:**

1. **Receber mensagem** do Kafka
2. **Verificar assinatura** da decisão
3. **Validar estrutura** da mensagem
4. **Criar transação** no smart contract
5. **Assinar transação** com chave privada
6. **Enviar para blockchain** (GoQuorum/Besu)
7. **Aguardar confirmação** (receipt)
8. **Publicar confirmação** em tópico de resposta (opcional)

**Smart Contract (exemplo):**

```solidity
// SLAContract.sol
contract SLAContract {
    struct SLADecision {
        string decisionId;
        string intentId;
        string tenantId;
        string decision;  // ACCEPT, REJECT, RENEGOTIATE
        string reason;
        uint256 timestamp;
        bytes32 signature;
    }
    
    mapping(string => SLADecision) public decisions;
    
    function registerDecision(
        string memory decisionId,
        string memory intentId,
        string memory tenantId,
        string memory decision,
        string memory reason,
        bytes32 signature
    ) public returns (bool) {
        decisions[decisionId] = SLADecision({
            decisionId: decisionId,
            intentId: intentId,
            tenantId: tenantId,
            decision: decision,
            reason: reason,
            timestamp: block.timestamp,
            signature: signature
        });
        
        emit DecisionRegistered(decisionId, intentId, decision);
        return true;
    }
    
    event DecisionRegistered(
        string indexed decisionId,
        string indexed intentId,
        string decision
    );
}
```

---

## 7. Interface I-05 — Decision Engine → SLA-Agent Layer

### 7.1 Propósito

A interface **I-05** transmite ações a serem executadas pelo Decision Engine para os agentes SLA (RAN, Transport, Core) de forma assíncrona via Kafka. Esta interface permite que o Decision Engine orquestre ações corretivas e de provisionamento nos domínios da rede.

### 7.2 Fluxo de Dados

```
Decision Engine            Kafka                    SLA-Agent Layer
    |                         |                         |
    |--- Action Message ----->|                         |
    |   (trisla-i05-actions)   |                         |
    |                         |--- Consume Message ---->|
    |                         |                         | [Filtra por domínio]
    |                         |                         | [RAN/Transport/Core]
    |                         |                         | [Executa ação]
    |                         |<-- Status Update -------|
    |                         |   (action_status)        |
```

### 7.3 Protocolo e Formato

**Protocolo**: Apache Kafka  
**Tópico**: `trisla-i05-actions`  
**Formato**: JSON (serializado como UTF-8)

**Configuração do tópico:**

```yaml
name: trisla-i05-actions
partitions: 3
replication-factor: 3
retention-ms: 604800000  # 7 dias
compression-type: gzip
cleanup-policy: delete
```

### 7.4 Estrutura da Mensagem

**Schema completo:**

```json
{
  "interface": "I-05",
  "source": "decision-engine",
  "destination": "sla-agents",
  "action_id": "action-001",
  "decision_id": "decision-001",
  "intent_id": "intent-001",
  "nest_id": "nest-intent-001",
  "tenant_id": "tenant-001",
  "action_type": "PROVISION_SLICE",
  "domain": "RAN",
  "action_data": {
    "slice_id": "slice-001",
    "resources": {
      "cpu": 4,
      "memory": "8Gi",
      "bandwidth": "1Gbps"
    },
    "sla_requirements": {
      "latency": "10ms",
      "throughput": "100Mbps"
    },
    "configuration": {
      "qos_profile": "gold",
      "network_slice_type": "eMBB"
    }
  },
  "priority": "high",
  "deadline": "2025-01-19T10:35:00Z",
  "timestamp": "2025-01-19T10:30:15Z",
  "version": "1.0.0"
}
```

### 7.5 Tipos de Ação

| Tipo de Ação | Descrição | Domínios Válidos | Idempotente |
|--------------|-----------|------------------|-------------|
| `PROVISION_SLICE` | Provisionar novo slice | RAN, Transport, Core | Sim |
| `SCALE_SLICE` | Escalar recursos do slice | RAN, Transport, Core | Sim |
| `RECONFIGURE_SLICE` | Reconfigurar slice existente | RAN, Transport, Core | Sim |
| `TERMINATE_SLICE` | Terminar slice | RAN, Transport, Core | Sim |
| `COLLECT_METRICS` | Coletar métricas | RAN, Transport, Core | Sim |
| `APPLY_CORRECTIVE_ACTION` | Aplicar ação corretiva | RAN, Transport, Core | Depende |

### 7.6 Filtragem por Domínio

**Processo no SLA-Agent Layer:**

```python
from kafka import KafkaConsumer
import json

class ActionConsumer:
    def __init__(self, domain: str):
        self.domain = domain.upper()  # RAN, TRANSPORT, CORE
        self.consumer = KafkaConsumer(
            'trisla-i05-actions',
            bootstrap_servers=['kafka:9092'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            group_id=f'sla-agent-{domain.lower()}-consumer',
            auto_offset_reset='earliest'
        )
    
    def consume_actions(self):
        """Consome ações filtradas por domínio"""
        for message in self.consumer:
            action = message.value
            
            # Filtrar por domínio
            if action.get('domain') != self.domain:
                continue  # Ignorar ações de outros domínios
            
            # Processar ação
            self.process_action(action)
    
    def process_action(self, action: dict):
        """Processa ação específica do domínio"""
        action_type = action.get('action_type')
        action_data = action.get('action_data', {})
        
        if action_type == 'PROVISION_SLICE':
            self.provision_slice(action_data)
        elif action_type == 'SCALE_SLICE':
            self.scale_slice(action_data)
        elif action_type == 'RECONFIGURE_SLICE':
            self.reconfigure_slice(action_data)
        elif action_type == 'TERMINATE_SLICE':
            self.terminate_slice(action_data)
        elif action_type == 'COLLECT_METRICS':
            self.collect_metrics(action_data)
        else:
            print(f"Unknown action type: {action_type}")
```

### 7.7 Retentativas Automáticas

**Configuração de retry no producer:**

```python
from kafka import KafkaProducer
from kafka.errors import KafkaError
import time

producer = KafkaProducer(
    bootstrap_servers=['kafka:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    acks='all',
    retries=3,
    retry_backoff_ms=100,  # Backoff exponencial
    max_in_flight_requests_per_connection=1,
    enable_idempotence=True
)

def send_action_with_retry(action_data: dict, max_retries: int = 3):
    """Envia ação com retry automático"""
    for attempt in range(max_retries):
        try:
            future = producer.send('trisla-i05-actions', value=action_data)
            record_metadata = future.get(timeout=10)
            return record_metadata
        except KafkaError as e:
            if attempt == max_retries - 1:
                raise  # Última tentativa falhou
            time.sleep(2 ** attempt)  # Backoff exponencial
```

---

## 8. Interface I-06 — Observabilidade OTLP

### 8.1 Propósito

A interface **I-06** é responsável pela exportação de telemetria (métricas, traces, logs) de todos os módulos TriSLA para o OTLP Collector, que por sua vez exporta para Prometheus, Grafana e outros sistemas de observabilidade.

### 8.2 Fluxo de Dados

```
Módulos TriSLA              OTLP Collector            Prometheus/Grafana
    |                            |                            |
    |--- Metrics/Traces/Logs --->|                            |
    |   (OTLP gRPC/HTTP)          |                            |
    |                            |--- Export Metrics -------->|
    |                            |                            | [Armazena]
    |                            |--- Export Traces -------->|
    |                            |                            | [Visualiza]
```

### 8.3 Protocolo e Formato

**Protocolo**: OpenTelemetry Protocol (OTLP)  
**Transporte**: gRPC ou HTTP  
**Endpoints**: 
- gRPC: `otlp-collector:4317`
- HTTP: `otlp-collector:4318`

**Formato**: Protocol Buffers (OTLP)

### 8.4 Estrutura de Dados OTLP

**Métricas:**

```protobuf
// Estrutura simplificada de métrica OTLP
message Metric {
  string name = 1;
  MetricType type = 2;
  repeated DataPoint data_points = 3;
}

message DataPoint {
  int64 time_unix_nano = 1;
  double value = 2;
  map<string, string> attributes = 3;
}
```

**Traces:**

```protobuf
// Estrutura simplificada de trace OTLP
message Span {
  string trace_id = 1;
  string span_id = 2;
  string name = 3;
  int64 start_time_unix_nano = 4;
  int64 end_time_unix_nano = 5;
  SpanKind kind = 6;
  Status status = 7;
  repeated Attribute attributes = 8;
}
```

### 8.5 Exemplo de Exportação

**Exportação de métricas (Python):**

```python
from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

# Configurar exportador
metric_exporter = OTLPMetricExporter(
    endpoint="http://otlp-collector:4317",
    insecure=True
)

# Configurar reader com intervalo de exportação
metric_reader = PeriodicExportingMetricReader(
    metric_exporter,
    export_interval_millis=5000  # Exportar a cada 5 segundos
)

# Configurar provider
meter_provider = MeterProvider(metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)

# Criar métricas
meter = metrics.get_meter(__name__)

# Counter
intents_counter = meter.create_counter(
    "trisla_intents_total",
    description="Total number of intents processed",
    unit="1"
)

# Histogram
decision_latency = meter.create_histogram(
    "trisla_decision_latency_seconds",
    description="Latency of decision making",
    unit="s"
)

# Gauge
sla_compliance = meter.create_up_down_counter(
    "trisla_sla_compliance_rate",
    description="SLA compliance rate",
    unit="1"
)

# Usar métricas
intents_counter.add(1, {"module": "sem-csmf", "status": "success"})
decision_latency.record(0.05, {"decision": "ACCEPT"})
sla_compliance.add(0.95, {"tenant": "tenant-001"})
```

**Exportação de traces (Python):**

```python
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Configurar exportador
trace_exporter = OTLPSpanExporter(
    endpoint="http://otlp-collector:4317",
    insecure=True
)

# Configurar provider
tracer_provider = TracerProvider()
tracer_provider.add_span_processor(BatchSpanProcessor(trace_exporter))
trace.set_tracer_provider(tracer_provider)

# Criar tracer
tracer = trace.get_tracer(__name__)

# Criar span
with tracer.start_as_current_span("process_intent") as span:
    span.set_attribute("intent.id", "intent-001")
    span.set_attribute("intent.tenant", "tenant-001")
    span.set_attribute("intent.service_type", "eMBB")
    
    # Processar intent
    result = process_intent(intent)
    
    span.set_attribute("result.status", result.status)
    span.set_status(trace.Status(trace.StatusCode.OK))
```

### 8.6 Métricas Principais Exportadas

**Métricas por módulo:**

| Módulo | Métricas Principais |
|--------|---------------------|
| **SEM-CSMF** | `trisla_intents_total`, `trisla_nests_generated_total`, `trisla_intent_processing_duration_seconds` |
| **ML-NSMF** | `trisla_predictions_total`, `trisla_prediction_duration_seconds`, `trisla_prediction_accuracy` |
| **Decision Engine** | `trisla_decisions_total`, `trisla_decision_latency_seconds`, `trisla_decision_by_type` |
| **BC-NSSMF** | `trisla_blockchain_transactions_total`, `trisla_transaction_duration_seconds`, `trisla_transaction_failures_total` |
| **SLA-Agent Layer** | `trisla_actions_executed_total`, `trisla_action_duration_seconds`, `trisla_metrics_collected_total` |
| **NASP Adapter** | `trisla_nasp_requests_total`, `trisla_nasp_request_duration_seconds`, `trisla_nasp_errors_total` |

---

## 9. Interface I-07 — NASP Integration

### 9.1 Propósito

A interface **I-07** é responsável pela integração do NASP Adapter com a plataforma NASP real, executando ações de provisionamento, escalonamento e coleta de métricas nos domínios RAN, Transport e Core.

### 9.2 Fluxo de Dados

```
SLA-Agent Layer            NASP Adapter              NASP Platform
    |                            |                         |
    |--- Action Request -------->|                         |
    |   (REST /api/v1/actions)    |                         |
    |                            |--- Provision Request -->|
    |                            |   (REST + mTLS)         |
    |                            |                         | [Executa ação]
    |                            |<-- Response ------------|
    |                            |   (status, resources)  |
    |<-- Action Response ---------|                         |
    |   (action_id, status)      |                         |
```

### 9.3 Protocolo e Formato

**Protocolo**: REST HTTP/1.1  
**Porta**: 8085 (NASP Adapter), variável (NASP)  
**Formato**: JSON

**Segurança**: TLS + mTLS + OAuth2

### 9.4 Endpoints do NASP Adapter

#### POST /api/v1/actions

**Descrição**: Executa ação no NASP.

**Request:**

```http
POST /api/v1/actions HTTP/1.1
Host: nasp-adapter:8085
Content-Type: application/json
Authorization: Bearer <JWT_TOKEN>

{
  "action_id": "action-001",
  "decision_id": "decision-001",
  "nest_id": "nest-intent-001",
  "domain": "RAN",
  "action_type": "PROVISION_SLICE",
  "slice_config": {
    "slice_id": "slice-001",
    "slice_type": "eMBB",
    "resources": {
      "cpu": 4,
      "memory": "8Gi",
      "bandwidth": "1Gbps"
    },
    "sla_requirements": {
      "latency": "10ms",
      "throughput": "100Mbps"
    },
    "qos_profile": "gold"
  },
  "priority": "high",
  "deadline": "2025-01-19T10:35:00Z"
}
```

**Response (200 OK):**

```json
{
  "action_id": "action-001",
  "status": "SUCCESS",
  "slice_id": "slice-001",
  "provisioned_at": "2025-01-19T10:30:20Z",
  "resources": {
    "ran": {
      "node_id": "node-001",
      "resources_allocated": {
        "cpu": 4,
        "memory": "8Gi",
        "prb_allocated": 50
      }
    },
    "transport": {
      "bandwidth_allocated": "1Gbps",
      "connection_id": "conn-001"
    },
    "core": {
      "connections_allocated": 1000,
      "session_id": "session-001"
    }
  },
  "estimated_compliance": {
    "latency": "8ms",
    "throughput": "1.2Gbps"
  }
}
```

#### GET /api/v1/metrics/{domain}

**Descrição**: Coleta métricas de um domínio específico.

**Request:**

```http
GET /api/v1/metrics/RAN?start_time=2025-01-19T10:00:00Z&end_time=2025-01-19T10:30:00Z HTTP/1.1
Host: nasp-adapter:8085
Authorization: Bearer <JWT_TOKEN>
```

**Response (200 OK):**

```json
{
  "domain": "RAN",
  "metrics": {
    "cpu_utilization": 0.65,
    "memory_utilization": 0.70,
    "prb_utilization": 0.45,
    "active_slices": 15,
    "throughput_mbps": 1200.5,
    "latency_ms": 8.2,
    "error_rate": 0.001
  },
  "timestamp": "2025-01-19T10:30:00Z",
  "time_range": {
    "start": "2025-01-19T10:00:00Z",
    "end": "2025-01-19T10:30:00Z"
  }
}
```

### 9.5 Integração com NASP Real

**Endpoints NASP (exemplo):**

- **RAN**: `https://nasp-ran.local/api/v1/slices`
- **Transport**: `https://nasp-transport.local/api/v1/connections`
- **Core**: `https://nasp-core.local/api/v1/sessions`

**Autenticação mTLS + OAuth2:**

```python
import requests
from requests.adapters import HTTPAdapter
import ssl

# Configurar mTLS
session = requests.Session()
adapter = HTTPAdapter()
adapter.init_poolmanager(
    ssl_context=ssl.create_default_context(cafile='/etc/nasp/ca.crt'),
    cert=('/etc/nasp/client.crt', '/etc/nasp/client.key')
)
session.mount('https://', adapter)

# Obter token OAuth2
def get_oauth_token() -> str:
    """Obtém token OAuth2 do NASP"""
    response = requests.post(
        'https://nasp.local/oauth/token',
        auth=('client_id', 'client_secret'),
        data={'grant_type': 'client_credentials'},
        verify='/etc/nasp/ca.crt'
    )
    response.raise_for_status()
    return response.json()['access_token']

# Executar ação
token = get_oauth_token()
response = session.post(
    'https://nasp-ran.local/api/v1/slices',
    headers={
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    },
    json=slice_config,
    timeout=30
)
response.raise_for_status()
return response.json()
```

---

## 10. Validação dos Fluxos

### 10.1 Validação de I-01 (gRPC)

**Validação de requisição:**

```python
def validate_nest_metadata_request(request: NESTMetadataRequest) -> bool:
    """Valida requisição I-01"""
    # Campos obrigatórios
    if not request.intent_id:
        raise ValueError("intent_id is required")
    if not request.nest_id:
        raise ValueError("nest_id is required")
    if not request.service_type:
        raise ValueError("service_type is required")
    if not request.sla_requirements:
        raise ValueError("sla_requirements is required")
    
    # Validação de service_type
    valid_types = ["eMBB", "URLLC", "mMTC"]
    if request.service_type not in valid_types:
        raise ValueError(f"service_type must be one of {valid_types}")
    
    # Validação de sla_requirements
    required_sla_keys = ["latency", "throughput"]
    for key in required_sla_keys:
        if key not in request.sla_requirements:
            raise ValueError(f"sla_requirements must contain {key}")
    
    return True
```

### 10.2 Validação de I-02 (REST)

**Validação de NEST:**

```python
from pydantic import BaseModel, validator
from typing import List, Dict

class NetworkSlice(BaseModel):
    slice_id: str
    slice_type: str
    resources: Dict[str, any]
    sla_requirements: Dict[str, str]

class NESTRequest(BaseModel):
    nest_id: str
    intent_id: str
    tenant_id: str
    service_type: str
    network_slices: List[NetworkSlice]
    metadata: Dict[str, any] = {}
    
    @validator('network_slices')
    def validate_slices(cls, v):
        if not v or len(v) == 0:
            raise ValueError('network_slices must contain at least one slice')
        return v
    
    @validator('service_type')
    def validate_service_type(cls, v):
        valid_types = ["eMBB", "URLLC", "mMTC"]
        if v not in valid_types:
            raise ValueError(f'service_type must be one of {valid_types}')
        return v
```

### 10.3 Validação de I-03, I-04, I-05 (Kafka)

**Validação de mensagem Kafka:**

```python
import json
from jsonschema import validate, ValidationError

# Schema para I-03
I03_SCHEMA = {
    "type": "object",
    "required": [
        "interface", "source", "destination", "prediction_id",
        "nest_id", "viability_score", "recommendation", "timestamp"
    ],
    "properties": {
        "interface": {"type": "string", "const": "I-03"},
        "source": {"type": "string", "const": "ml-nsmf"},
        "destination": {"type": "string", "const": "decision-engine"},
        "prediction_id": {"type": "string"},
        "nest_id": {"type": "string"},
        "viability_score": {"type": "number", "minimum": 0, "maximum": 1},
        "recommendation": {"type": "string", "enum": ["ACCEPT", "REJECT", "RENEGOTIATE"]},
        "timestamp": {"type": "string"}
    }
}

def validate_kafka_message(message: dict, schema: dict) -> bool:
    """Valida mensagem Kafka contra schema"""
    try:
        validate(instance=message, schema=schema)
        return True
    except ValidationError as e:
        print(f"Validation error: {e.message}")
        return False
```

### 10.4 Validação End-to-End

**Script de validação:**

```python
async def validate_e2e_flow():
    """Valida fluxo completo I-01 → I-02 → I-03 → I-04 → I-05"""
    
    # 1. Criar intent (SEM-CSMF)
    intent = await create_intent({
        "tenant_id": "tenant-001",
        "intent": "Criar slice para AR"
    })
    
    # 2. Verificar I-01 (gRPC)
    nest_metadata = await get_nest_metadata(intent.nest_id)
    assert nest_metadata is not None
    
    # 3. Verificar I-02 (REST)
    prediction = await get_prediction(nest_metadata.prediction_id)
    assert prediction.viability_score > 0
    
    # 4. Verificar I-03 (Kafka)
    kafka_message = await consume_kafka_message('trisla-ml-predictions')
    assert kafka_message['interface'] == 'I-03'
    
    # 5. Verificar I-04 (Kafka)
    decision_message = await consume_kafka_message('trisla-i04-decisions')
    assert decision_message['interface'] == 'I-04'
    
    # 6. Verificar I-05 (Kafka)
    action_message = await consume_kafka_message('trisla-i05-actions')
    assert action_message['interface'] == 'I-05'
    
    print("✅ E2E flow validation passed")
```

---

## 11. Versionamento de Interfaces

### 11.1 Estratégia de Versionamento

**Princípios:**

1. **Backward compatibility**: Versões menores mantêm compatibilidade
2. **Breaking changes**: Requerem nova versão major
3. **Deprecation**: Interfaces antigas são depreciadas antes de remoção

**Formato de versão:**

- **Major.Minor.Patch** (ex: 1.0.0)
- **Major**: Breaking changes
- **Minor**: Novas funcionalidades, compatível
- **Patch**: Correções, compatível

### 11.2 Versionamento em gRPC

**Incluir versão no package:**

```protobuf
// Versão 1.0.0
package trisla.i01.v1;

service DecisionEngineService {
  rpc SendNESTMetadata(NESTMetadataRequest) returns (NESTMetadataResponse);
}

// Versão 2.0.0 (futura, com breaking changes)
package trisla.i01.v2;

service DecisionEngineService {
  rpc SendNESTMetadata(NESTMetadataRequestV2) returns (NESTMetadataResponseV2);
}
```

### 11.3 Versionamento em REST

**Via path:**

```
/api/v1/nest
/api/v2/nest  // Futura versão
```

**Via header:**

```http
GET /api/nest HTTP/1.1
Host: ml-nsmf:8081
API-Version: v1
```

### 11.4 Versionamento em Kafka

**Incluir versão na mensagem:**

```json
{
  "interface": "I-03",
  "version": "1.0.0",
  ...
}
```

**Ou via tópico versionado:**

```
trisla-ml-predictions-v1
trisla-ml-predictions-v2  // Futura versão
```

### 11.5 Processo de Deprecação

**Exemplo de deprecação:**

1. **Anunciar deprecação**: Documentar em changelog
2. **Período de transição**: 6 meses
3. **Suporte duplo**: Manter ambas versões
4. **Remoção**: Após período de transição

---

## 12. Medidas de Segurança por Interface

### 12.1 I-01 (gRPC)

**Segurança:**

- **mTLS obrigatório**: Certificados mútuos
- **JWT opcional**: Para autorização adicional
- **Rate limiting**: Limite de requisições por tenant

**Implementação:**

```python
import grpc
from grpc import ssl_channel_credentials

# Carregar certificados
with open('/etc/tls/tls.crt', 'rb') as f:
    cert = f.read()
with open('/etc/tls/tls.key', 'rb') as f:
    key = f.read()
with open('/etc/tls/ca.crt', 'rb') as f:
    ca_cert = f.read()

# Criar credenciais mTLS
credentials = ssl_channel_credentials(
    root_certificates=ca_cert,
    private_key=key,
    certificate_chain=cert
)

# Criar canal seguro
channel = grpc.secure_channel('decision-engine:50051', credentials)
```

### 12.2 I-02 (REST)

**Segurança:**

- **TLS obrigatório**: HTTPS apenas
- **JWT obrigatório**: Autenticação de tenant
- **Rate limiting**: 100 requisições/minuto por tenant

**Implementação:**

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
import jwt

security = HTTPBearer()

async def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### 12.3 I-03, I-04, I-05 (Kafka)

**Segurança:**

- **SASL/SCRAM**: Autenticação de clientes
- **TLS obrigatório**: Criptografia em trânsito
- **ACLs**: Controle de acesso por tópico

**Configuração:**

```yaml
# Kafka server.properties
security.inter.broker.protocol=SASL_SSL
sasl.mechanism.inter.broker.protocol=SCRAM-SHA-512
sasl.enabled.mechanisms=SCRAM-SHA-512
listeners=SASL_SSL://:9093
ssl.keystore.location=/etc/kafka/secrets/kafka.keystore.jks
ssl.truststore.location=/etc/kafka/secrets/kafka.truststore.jks
authorizer.class.name=kafka.security.authorizer.AclAuthorizer
allow.everyone.if.no.acl.found=false
```

**Cliente:**

```python
from kafka import KafkaProducer
import ssl

producer = KafkaProducer(
    bootstrap_servers=['kafka:9093'],
    security_protocol='SASL_SSL',
    sasl_mechanism='SCRAM-SHA-512',
    sasl_plain_username='ml-nsmf',
    sasl_plain_password='<PASSWORD>',
    ssl_context=ssl.create_default_context(),
    ssl_check_hostname=True
)
```

### 12.4 I-06, I-07 (REST)

**Segurança:**

- **TLS obrigatório**: HTTPS apenas
- **mTLS**: Para comunicação com NASP
- **OAuth2**: Para autenticação com NASP
- **Rate limiting**: 50 requisições/minuto

---

## 13. Diagrama Textual dos Fluxos Internos

### 13.1 Fluxo Principal: Intent → Decisão → Ação

```
┌─────────────┐
│   Tenant    │
└──────┬──────┘
       │ POST /api/v1/intents
       ▼
┌─────────────┐
│  SEM-CSMF   │
│             │
│ [Processa]  │
│ [Gera NEST] │
└──────┬──────┘
       │
       ├─────────────────────────────────┐
       │                                 │
       │ I-01 (gRPC)                     │ I-02 (REST)
       ▼                                 ▼
┌─────────────────┐            ┌─────────────┐
│ Decision Engine │            │   ML-NSMF   │
│                 │            │             │
│ [Recebe NEST]   │            │ [Analisa]   │
│                 │            │ [Prediz]    │
└──────┬──────────┘            └──────┬──────┘
       │                               │
       │                               │ I-03 (Kafka)
       │                               │ trisla-ml-predictions
       │                               ▼
       │                       ┌─────────────┐
       │                       │   Kafka     │
       │                       └──────┬──────┘
       │                               │
       │<──────────────────────────────┘
       │ [Recebe predição]
       │
       │ [Toma decisão]
       │
       ├─────────────────┬─────────────────┐
       │                 │                 │
       │ I-04 (Kafka)    │ I-05 (Kafka)    │
       │ trisla-i04-     │ trisla-i05-     │
       │ decisions       │ actions          │
       ▼                 ▼                 ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  BC-NSSMF   │    │SLA-Agent    │    │SLA-Agent    │
│             │    │Layer (RAN)  │    │Layer (Core) │
│ [Registra]  │    │             │    │             │
│ [Blockchain]│    │ [Executa]   │    │ [Executa]   │
└─────────────┘    └──────┬───────┘    └──────┬──────┘
                         │                   │
                         │ I-06 (REST)       │ I-06 (REST)
                         ▼                   ▼
                    ┌─────────────┐    ┌─────────────┐
                    │NASP Adapter │    │NASP Adapter │
                    └──────┬──────┘    └──────┬──────┘
                           │                  │
                           │ I-07 (REST)      │ I-07 (REST)
                           │ + mTLS           │ + mTLS
                           ▼                  ▼
                    ┌─────────────┐    ┌─────────────┐
                    │   NASP      │    │   NASP      │
                    │   (RAN)     │    │   (Core)    │
                    └─────────────┘    └─────────────┘
```

### 13.2 Fluxo de Observabilidade (I-06)

```
┌─────────────┐
│ SEM-CSMF    │───OTLP───┐
└─────────────┘          │
                         │
┌─────────────┐          │
│  ML-NSMF    │───OTLP───┤
└─────────────┘          │
                         │
┌─────────────┐          │
│Decision     │───OTLP───┤
│Engine       │          │
└─────────────┘          │
                         ▼
                  ┌─────────────┐
                  │OTLP Collector│
                  └──────┬───────┘
                         │
            ┌─────────────┼─────────────┐
            │             │             │
            ▼             ▼             ▼
      ┌──────────┐  ┌──────────┐  ┌──────────┐
      │Prometheus│  │  Grafana │  │Alertmanager│
      └──────────┘  └──────────┘  └──────────┘
```

### 13.3 Fluxo de Retry e Recuperação

```
┌─────────────┐
│   Producer   │
└──────┬───────┘
       │ Send Message
       ▼
┌─────────────┐
│   Kafka     │
└──────┬──────┘
       │
       ├─── Success ────► Consumer
       │
       └─── Failure ────► Retry (exponential backoff)
                          │
                          ├─── Max Retries ────► Dead Letter Queue
                          │
                          └─── Success ────► Consumer
```

---

## 14. Apêndice

### 14.1 Fragmentos de `.proto`

**Arquivo completo: `proto/i01_interface.proto`**

```protobuf
syntax = "proto3";

package trisla.i01;

// Serviço gRPC para comunicação SEM-CSMF ↔ Decision Engine
service DecisionEngineService {
  // Envia metadados de NEST para decisão
  rpc SendNESTMetadata(NESTMetadataRequest) returns (NESTMetadataResponse);
  
  // Consulta status de uma decisão
  rpc GetDecisionStatus(DecisionStatusRequest) returns (DecisionStatusResponse);
}

// Requisição de metadados de NEST
message NESTMetadataRequest {
  string intent_id = 1;                    // ID único do intent
  string nest_id = 2;                      // ID único do NEST gerado
  string tenant_id = 3;                    // ID do tenant
  string service_type = 4;                 // Tipo: eMBB, URLLC, mMTC
  map<string, string> sla_requirements = 5; // Requisitos de SLA
  string nest_status = 6;                  // Status do NEST
  string timestamp = 7;                    // Timestamp ISO 8601
  map<string, string> metadata = 8;        // Metadados adicionais
}

// Resposta de metadados de NEST
message NESTMetadataResponse {
  bool success = 1;          // Indica se requisição foi aceita
  string decision_id = 2;     // ID único da decisão gerada
  string message = 3;         // Mensagem de resposta
  int32 status_code = 4;      // Código: 0=OK, >0=erro
}

// Requisição de status de decisão
message DecisionStatusRequest {
  string decision_id = 1;     // ID da decisão a consultar
  string intent_id = 2;       // ID do intent (opcional)
}

// Resposta de status de decisão
message DecisionStatusResponse {
  string decision_id = 1;              // ID da decisão
  string intent_id = 2;                // ID do intent
  string decision = 3;                  // ACCEPT, REJECT, RENEGOTIATE
  string reason = 4;                   // Razão da decisão
  string timestamp = 5;                // Timestamp da decisão
  map<string, string> details = 6;     // Detalhes adicionais
}
```

**Geração de código:**

```bash
# Gerar código Python
python -m grpc_tools.protoc \
  -I. \
  --python_out=. \
  --grpc_python_out=. \
  proto/i01_interface.proto
```

### 14.2 Fragmentos YAML

**Configuração Kafka Topic (I-03, I-04, I-05):**

```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: trisla-ml-predictions
  namespace: trisla
spec:
  partitions: 3
  replicas: 3
  config:
    retention.ms: 604800000  # 7 dias
    compression.type: gzip
    cleanup.policy: delete
    min.insync.replicas: 2
```

**Configuração Network Policy (I-01):**

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: i01-grpc-policy
  namespace: trisla
spec:
  podSelector:
    matchLabels:
      app: decision-engine
  policyTypes:
    - Ingress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: sem-csmf
      ports:
        - protocol: TCP
          port: 50051
```

### 14.3 Estruturas JSON Principais

**Mensagem I-03 (Kafka):**

```json
{
  "interface": "I-03",
  "source": "ml-nsmf",
  "destination": "decision-engine",
  "prediction_id": "pred-001",
  "nest_id": "nest-intent-001",
  "intent_id": "intent-001",
  "tenant_id": "tenant-001",
  "viability_score": 0.87,
  "recommendation": "ACCEPT",
  "confidence": 0.92,
  "explanation": {
    "top_features": [
      {
        "feature": "latency_margin",
        "importance": 0.35,
        "value": 0.85,
        "contribution": "positive"
      }
    ],
    "shap_values": {
      "latency_margin": 0.15,
      "resource_ratio": 0.12
    }
  },
  "metrics_used": {
    "cpu_utilization": 0.65,
    "memory_utilization": 0.70
  },
  "timestamp": "2025-01-19T10:30:05Z",
  "version": "1.0.0"
}
```

**Mensagem I-04 (Kafka):**

```json
{
  "interface": "I-04",
  "source": "decision-engine",
  "destination": "bc-nssmf",
  "decision_id": "decision-001",
  "intent_id": "intent-001",
  "nest_id": "nest-intent-001",
  "tenant_id": "tenant-001",
  "decision": "ACCEPT",
  "reason": "SLA requirements met",
  "sla_data": {
    "latency": "10ms",
    "throughput": "100Mbps"
  },
  "ml_prediction": {
    "prediction_id": "pred-001",
    "viability_score": 0.87
  },
  "timestamp": "2025-01-19T10:30:10Z",
  "signature": "0x1a2b3c4d...",
  "version": "1.0.0"
}
```

**Mensagem I-05 (Kafka):**

```json
{
  "interface": "I-05",
  "source": "decision-engine",
  "destination": "sla-agents",
  "action_id": "action-001",
  "decision_id": "decision-001",
  "intent_id": "intent-001",
  "nest_id": "nest-intent-001",
  "tenant_id": "tenant-001",
  "action_type": "PROVISION_SLICE",
  "domain": "RAN",
  "action_data": {
    "slice_id": "slice-001",
    "resources": {
      "cpu": 4,
      "memory": "8Gi",
      "bandwidth": "1Gbps"
    },
    "sla_requirements": {
      "latency": "10ms",
      "throughput": "100Mbps"
    }
  },
  "priority": "high",
  "timestamp": "2025-01-19T10:30:15Z",
  "version": "1.0.0"
}
```

### 14.4 Esquemas de Validação JSON Schema

**Schema para I-03:**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": [
    "interface", "source", "destination", "prediction_id",
    "nest_id", "viability_score", "recommendation", "timestamp"
  ],
  "properties": {
    "interface": {
      "type": "string",
      "const": "I-03"
    },
    "source": {
      "type": "string",
      "const": "ml-nsmf"
    },
    "destination": {
      "type": "string",
      "const": "decision-engine"
    },
    "prediction_id": {
      "type": "string",
      "pattern": "^pred-[a-z0-9-]+$"
    },
    "nest_id": {
      "type": "string",
      "pattern": "^nest-[a-z0-9-]+$"
    },
    "viability_score": {
      "type": "number",
      "minimum": 0,
      "maximum": 1
    },
    "recommendation": {
      "type": "string",
      "enum": ["ACCEPT", "REJECT", "RENEGOTIATE"]
    },
    "confidence": {
      "type": "number",
      "minimum": 0,
      "maximum": 1
    },
    "timestamp": {
      "type": "string",
      "format": "date-time"
    },
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$"
    }
  }
}
```

---

## Conclusão

Este documento fornece a documentação completa das interfaces internas I-01 a I-07 do TriSLA. Cada interface foi detalhada com propósito, fluxo de dados, payloads, protocolos e medidas de segurança.

**Principais pontos:**

- **I-01**: Comunicação síncrona crítica via gRPC
- **I-02**: Transmissão de NEST via REST
- **I-03, I-04, I-05**: Mensageria assíncrona via Kafka
- **I-06**: Observabilidade via OTLP
- **I-07**: Integração externa com NASP

**Última atualização:** 2025-01-XX  
**Versão do documento:** 1.0.0  
**Versão das interfaces:** 1.0.0

**Referências:**
- `API_REFERENCE.md`: Referência completa de APIs
- `README_OPERATIONS_PROD.md`: Guia de operações
- `TROUBLESHOOTING_TRISLA.md`: Guia de troubleshooting


