# TriSLA — Referência de API

## 1. Introdução

### 1.1 Objetivo deste Documento

Este documento fornece a referência técnica completa das APIs do **TriSLA** (Triple-SLA), cobrindo todas as interfaces internas (I-01 a I-07) e APIs externas dos módulos. O documento serve como guia para desenvolvedores que precisam integrar com o TriSLA ou entender a comunicação entre seus módulos.

### 1.2 Arquitetura de APIs do TriSLA

O TriSLA utiliza uma arquitetura de microserviços com comunicação assíncrona e síncrona:

- **gRPC**: Para comunicação síncrona de alta performance (I-01)
- **REST HTTP**: Para APIs externas e comunicação entre módulos (I-02, I-06, I-07)
- **Kafka**: Para mensageria assíncrona e eventos (I-03, I-04, I-05)
- **OTLP**: Para observabilidade e telemetria (I-06)

### 1.3 Convenções

**Formato de dados:**
- **gRPC**: Protocol Buffers (protobuf)
- **REST**: JSON
- **Kafka**: JSON (serializado como string UTF-8)

**Autenticação:**
- **gRPC**: mTLS + JWT (quando aplicável)
- **REST**: JWT Bearer Token
- **Kafka**: SASL/SCRAM + TLS

**Versionamento:**
- APIs seguem versionamento semântico (v1, v2, etc.)
- Versão atual: **v1.0.0**

---

## 2. Tabela Geral das Interfaces Internas (I-01 a I-07)

| Interface | Protocolo | Direção | Função | Endpoint/Tópico |
|-----------|-----------|---------|--------|-----------------|
| **I-01** | gRPC | SEM-CSMF → Decision Engine | Envio de metadados de NEST | `decision-engine:50051` |
| **I-02** | REST | SEM-CSMF → ML-NSMF | Envio de NEST gerado | `POST /api/v1/nest` |
| **I-03** | Kafka | ML-NSMF → Decision Engine | Envio de predições ML | `trisla-ml-predictions` |
| **I-04** | Kafka | Decision Engine → BC-NSSMF | Envio de decisões para blockchain | `trisla-i04-decisions` |
| **I-05** | Kafka | Decision Engine → SLA-Agent Layer | Envio de ações para agentes | `trisla-i05-actions` |
| **I-06** | REST | SLA-Agent Layer → NASP Adapter | Execução de ações no NASP | `POST /api/v1/actions` |
| **I-07** | REST | NASP Adapter → NASP | Integração com plataforma NASP | `POST /api/v1/provision` |

### 2.1 Características das Interfaces

**I-01 (gRPC):**
- **Latência**: p99 < 50ms
- **Timeout**: 5s
- **Segurança**: mTLS obrigatório
- **Idempotência**: Não (cada chamada cria nova decisão)

**I-02 (REST):**
- **Latência**: p99 < 100ms
- **Timeout**: 10s
- **Segurança**: TLS + JWT
- **Idempotência**: Sim (mesmo NEST pode ser enviado múltiplas vezes)

**I-03, I-04, I-05 (Kafka):**
- **Latência**: < 10ms (produção)
- **Retenção**: 7 dias
- **Segurança**: SASL/SCRAM + TLS
- **Idempotência**: Sim (mensagens são idempotentes)

**I-06, I-07 (REST):**
- **Latência**: p99 < 200ms
- **Timeout**: 30s
- **Segurança**: TLS + mTLS + OAuth2
- **Idempotência**: Depende da ação

---

## 3. API de I-01 (gRPC SEM-CSMF ↔ Decision Engine)

### 3.1 Visão Geral

A interface **I-01** utiliza gRPC para comunicação síncrona entre SEM-CSMF e Decision Engine. Esta interface é crítica para o fluxo de decisão, enviando metadados de NEST (Network Slice Template) para avaliação.

### 3.2 Definição do Serviço

**Arquivo Proto: `proto/i01_interface.proto`**

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
```

### 3.3 Mensagens

#### NESTMetadataRequest

```protobuf
message NESTMetadataRequest {
  string intent_id = 1;           // ID único do intent
  string nest_id = 2;             // ID único do NEST gerado
  string tenant_id = 3;           // ID do tenant
  string service_type = 4;        // Tipo de serviço (eMBB, URLLC, mMTC)
  map<string, string> sla_requirements = 5;  // Requisitos de SLA
  string nest_status = 6;         // Status do NEST (generated, validated)
  string timestamp = 7;           // Timestamp ISO 8601
  map<string, string> metadata = 8;  // Metadados adicionais
}
```

**Campos obrigatórios:**
- `intent_id`
- `nest_id`
- `service_type`
- `sla_requirements`

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
    "reliability": "99.9%"
  },
  "nest_status": "generated",
  "timestamp": "2025-01-19T10:30:00Z",
  "metadata": {
    "slice_count": "3",
    "priority": "high"
  }
}
```

#### NESTMetadataResponse

```protobuf
message NESTMetadataResponse {
  bool success = 1;               // Indica se a requisição foi aceita
  string decision_id = 2;         // ID único da decisão gerada
  string message = 3;             // Mensagem de resposta
  int32 status_code = 4;          // Código de status (0 = OK)
}
```

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
  string decision_id = 1;         // ID da decisão a consultar
  string intent_id = 2;          // ID do intent (opcional, para validação)
}
```

#### DecisionStatusResponse

```protobuf
message DecisionStatusResponse {
  string decision_id = 1;         // ID da decisão
  string intent_id = 2;           // ID do intent
  string decision = 3;            // Decisão: ACCEPT, REJECT, RENEGOTIATE
  string reason = 4;             // Razão da decisão
  string timestamp = 5;          // Timestamp da decisão
  map<string, string> details = 6;  // Detalhes adicionais
}
```

**Exemplo de resposta:**

```json
{
  "decision_id": "decision-001",
  "intent_id": "intent-001",
  "decision": "ACCEPT",
  "reason": "SLA requirements met, ML prediction positive",
  "timestamp": "2025-01-19T10:30:05Z",
  "details": {
    "ml_score": "0.87",
    "confidence": "0.92",
    "estimated_latency": "8ms"
  }
}
```

### 3.4 Exemplo de Uso (Python)

**Cliente gRPC (SEM-CSMF):**

```python
import grpc
from proto.proto import i01_interface_pb2
from proto.proto import i01_interface_pb2_grpc

# Criar canal gRPC
channel = grpc.insecure_channel('decision-engine:50051')
stub = i01_interface_pb2_grpc.DecisionEngineServiceStub(channel)

# Criar requisição
request = i01_interface_pb2.NESTMetadataRequest(
    intent_id="intent-001",
    nest_id="nest-intent-001",
    tenant_id="tenant-001",
    service_type="eMBB",
    sla_requirements={
        "latency": "10ms",
        "throughput": "100Mbps"
    },
    nest_status="generated",
    timestamp="2025-01-19T10:30:00Z"
)

# Enviar requisição
response = stub.SendNESTMetadata(request)
print(f"Decision ID: {response.decision_id}")
```

**Servidor gRPC (Decision Engine):**

```python
import grpc
from concurrent import futures
from proto.proto import i01_interface_pb2
from proto.proto import i01_interface_pb2_grpc

class DecisionEngineService(i01_interface_pb2_grpc.DecisionEngineServiceServicer):
    def SendNESTMetadata(self, request, context):
        # Processar metadados
        decision_id = self.process_nest_metadata(request)
        
        return i01_interface_pb2.NESTMetadataResponse(
            success=True,
            decision_id=decision_id,
            message="NEST metadata received",
            status_code=0
        )
    
    def GetDecisionStatus(self, request, context):
        # Buscar status da decisão
        decision = self.get_decision(request.decision_id)
        
        return i01_interface_pb2.DecisionStatusResponse(
            decision_id=decision.id,
            intent_id=decision.intent_id,
            decision=decision.action,
            reason=decision.reason,
            timestamp=decision.timestamp
        )

# Iniciar servidor
server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
i01_interface_pb2_grpc.add_DecisionEngineServiceServicer_to_server(
    DecisionEngineService(), server
)
server.add_insecure_port('[::]:50051')
server.start()
server.wait_for_termination()
```

### 3.5 Exemplo de Uso (gRPCurl)

```bash
# Listar serviços disponíveis
grpcurl -plaintext decision-engine:50051 list

# Listar métodos do serviço
grpcurl -plaintext decision-engine:50051 list trisla.i01.DecisionEngineService

# Enviar metadados
grpcurl -plaintext -d '{
  "intent_id": "intent-001",
  "nest_id": "nest-intent-001",
  "tenant_id": "tenant-001",
  "service_type": "eMBB",
  "sla_requirements": {
    "latency": "10ms",
    "throughput": "100Mbps"
  },
  "nest_status": "generated",
  "timestamp": "2025-01-19T10:30:00Z"
}' decision-engine:50051 trisla.i01.DecisionEngineService/SendNESTMetadata

# Consultar status
grpcurl -plaintext -d '{
  "decision_id": "decision-001"
}' decision-engine:50051 trisla.i01.DecisionEngineService/GetDecisionStatus
```

---

## 4. API de I-02 (REST Decision Engine ↔ ML-NSMF)

### 4.1 Visão Geral

A interface **I-02** utiliza REST HTTP para comunicação entre SEM-CSMF e ML-NSMF, enviando NEST gerado para análise e predição de viabilidade.

### 4.2 Endpoints

#### POST /api/v1/nest

**Descrição**: Envia NEST gerado para o ML-NSMF para análise de viabilidade.

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
        "throughput": "100Mbps"
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
  "timestamp": "2025-01-19T10:30:01Z"
}
```

**Response (400 Bad Request):**

```json
{
  "error": "Invalid NEST format",
  "message": "Missing required field: network_slices",
  "status_code": 400
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
  "viability_score": 0.87,
  "recommendation": "ACCEPT",
  "confidence": 0.92,
  "explanation": {
    "top_features": [
      {
        "feature": "latency_margin",
        "importance": 0.35,
        "value": 0.85
      },
      {
        "feature": "resource_ratio",
        "importance": 0.28,
        "value": 0.78
      }
    ],
    "shap_values": {
      "latency_margin": 0.15,
      "resource_ratio": 0.12,
      "network_capacity": 0.08
    }
  },
  "timestamp": "2025-01-19T10:30:05Z"
}
```

### 4.3 Modelo de Dados

**NEST Request:**

```typescript
interface NESTRequest {
  nest_id: string;
  intent_id: string;
  tenant_id: string;
  service_type: "eMBB" | "URLLC" | "mMTC";
  network_slices: NetworkSlice[];
  metadata?: Record<string, any>;
}

interface NetworkSlice {
  slice_id: string;
  slice_type: string;
  resources: {
    cpu: number;
    memory: string;
    bandwidth: string;
  };
  sla_requirements: {
    latency?: string;
    throughput?: string;
    reliability?: string;
  };
}
```

**Prediction Response:**

```typescript
interface PredictionResponse {
  prediction_id: string;
  nest_id: string;
  viability_score: number;  // 0.0 a 1.0
  recommendation: "ACCEPT" | "REJECT" | "RENEGOTIATE";
  confidence: number;  // 0.0 a 1.0
  explanation: {
    top_features: Array<{
      feature: string;
      importance: number;
      value: number;
    }>;
    shap_values: Record<string, number>;
  };
  timestamp: string;
}
```

---

## 5. API de I-03 (Kafka ML-NSMF → Decision Engine)

### 5.1 Visão Geral

A interface **I-03** utiliza Kafka para comunicação assíncrona entre ML-NSMF e Decision Engine, enviando predições de viabilidade de SLA.

### 5.2 Tópico Kafka

**Nome do tópico**: `trisla-ml-predictions`

**Configuração:**
- **Partitions**: 3
- **Replication Factor**: 3
- **Retention**: 7 dias
- **Compression**: gzip

### 5.3 Estrutura da Mensagem

**Schema da mensagem:**

```json
{
  "interface": "I-03",
  "source": "ml-nsmf",
  "destination": "decision-engine",
  "prediction_id": "pred-001",
  "nest_id": "nest-intent-001",
  "intent_id": "intent-001",
  "viability_score": 0.87,
  "recommendation": "ACCEPT",
  "confidence": 0.92,
  "explanation": {
    "top_features": [
      {
        "feature": "latency_margin",
        "importance": 0.35,
        "value": 0.85
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
  "timestamp": "2025-01-19T10:30:05Z",
  "version": "1.0.0"
}
```

### 5.4 Campos Obrigatórios

- `interface`: Sempre "I-03"
- `source`: Sempre "ml-nsmf"
- `destination`: Sempre "decision-engine"
- `prediction_id`: ID único da predição
- `nest_id`: ID do NEST analisado
- `viability_score`: Score de viabilidade (0.0 a 1.0)
- `recommendation`: ACCEPT, REJECT ou RENEGOTIATE
- `timestamp`: Timestamp ISO 8601

### 5.5 Exemplo de Produção (Python)

```python
from kafka import KafkaProducer
import json
from datetime import datetime

producer = KafkaProducer(
    bootstrap_servers=['kafka:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

message = {
    "interface": "I-03",
    "source": "ml-nsmf",
    "destination": "decision-engine",
    "prediction_id": "pred-001",
    "nest_id": "nest-intent-001",
    "intent_id": "intent-001",
    "viability_score": 0.87,
    "recommendation": "ACCEPT",
    "confidence": 0.92,
    "explanation": {
        "top_features": [
            {
                "feature": "latency_margin",
                "importance": 0.35,
                "value": 0.85
            }
        ]
    },
    "timestamp": datetime.utcnow().isoformat() + "Z",
    "version": "1.0.0"
}

producer.send('trisla-ml-predictions', value=message)
producer.flush()
```

### 5.6 Exemplo de Consumo (Python)

```python
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'trisla-ml-predictions',
    bootstrap_servers=['kafka:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    group_id='decision-engine-consumer',
    auto_offset_reset='earliest',
    enable_auto_commit=True
)

for message in consumer:
    prediction = message.value
    print(f"Received prediction: {prediction['prediction_id']}")
    print(f"Viability score: {prediction['viability_score']}")
    print(f"Recommendation: {prediction['recommendation']}")
    
    # Processar predição
    process_prediction(prediction)
```

---

## 6. API de I-04 (Kafka Decision Engine → BC-NSSMF)

### 6.1 Visão Geral

A interface **I-04** utiliza Kafka para comunicação assíncrona entre Decision Engine e BC-NSSMF, enviando decisões para registro em blockchain.

### 6.2 Tópico Kafka

**Nome do tópico**: `trisla-i04-decisions`

**Configuração:**
- **Partitions**: 3
- **Replication Factor**: 3
- **Retention**: 30 dias (maior retenção para auditoria)
- **Compression**: gzip

### 6.3 Estrutura da Mensagem

**Schema da mensagem:**

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
    "confidence": 0.92
  },
  "timestamp": "2025-01-19T10:30:10Z",
  "signature": "0x...",  // Assinatura da decisão
  "version": "1.0.0"
}
```

### 6.4 Campos Obrigatórios

- `interface`: Sempre "I-04"
- `source`: Sempre "decision-engine"
- `destination`: Sempre "bc-nssmf"
- `decision_id`: ID único da decisão
- `intent_id`: ID do intent
- `decision`: ACCEPT, REJECT ou RENEGOTIATE
- `timestamp`: Timestamp ISO 8601
- `signature`: Assinatura criptográfica da decisão

### 6.5 Exemplo de Produção

```python
from kafka import KafkaProducer
import json
import hashlib
import hmac
from datetime import datetime

def sign_decision(decision_data, secret_key):
    """Assina decisão antes de enviar"""
    message = json.dumps(decision_data, sort_keys=True)
    signature = hmac.new(
        secret_key.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    return f"0x{signature}"

producer = KafkaProducer(
    bootstrap_servers=['kafka:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

decision_data = {
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
    "timestamp": datetime.utcnow().isoformat() + "Z"
}

# Assinar decisão
decision_data["signature"] = sign_decision(decision_data, SECRET_KEY)

producer.send('trisla-i04-decisions', value=decision_data)
producer.flush()
```

---

## 7. API de I-05 (Kafka Decision Engine → SLA-Agent Layer)

### 7.1 Visão Geral

A interface **I-05** utiliza Kafka para comunicação assíncrona entre Decision Engine e SLA-Agent Layer, enviando ações para execução nos agentes RAN, Transport e Core.

### 7.2 Tópico Kafka

**Nome do tópico**: `trisla-i05-actions`

**Configuração:**
- **Partitions**: 3
- **Replication Factor**: 3
- **Retention**: 7 dias
- **Compression**: gzip

### 7.3 Estrutura da Mensagem

**Schema da mensagem:**

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

### 7.4 Tipos de Ação

| Tipo de Ação | Descrição | Domínio |
|--------------|-----------|---------|
| `PROVISION_SLICE` | Provisionar novo slice | RAN, Transport, Core |
| `SCALE_SLICE` | Escalar recursos do slice | RAN, Transport, Core |
| `RECONFIGURE_SLICE` | Reconfigurar slice existente | RAN, Transport, Core |
| `TERMINATE_SLICE` | Terminar slice | RAN, Transport, Core |
| `COLLECT_METRICS` | Coletar métricas | RAN, Transport, Core |

### 7.5 Exemplo de Consumo (SLA-Agent Layer)

```python
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'trisla-i05-actions',
    bootstrap_servers=['kafka:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    group_id='sla-agent-consumer',
    auto_offset_reset='earliest'
)

for message in consumer:
    action = message.value
    
    # Filtrar por domínio
    domain = action.get('domain')
    if domain == 'RAN':
        execute_ran_action(action)
    elif domain == 'TRANSPORT':
        execute_transport_action(action)
    elif domain == 'CORE':
        execute_core_action(action)
```

---

## 8. API de I-06 (REST Observability / OTLP)

### 8.1 Visão Geral

A interface **I-06** utiliza OpenTelemetry Protocol (OTLP) para exportação de métricas, traces e logs de todos os módulos TriSLA.

### 8.2 Endpoints OTLP

**gRPC Endpoint**: `otlp-collector:4317`  
**HTTP Endpoint**: `otlp-collector:4318`

### 8.3 Exportação de Métricas

**Exemplo (Python):**

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

# Configurar reader
metric_reader = PeriodicExportingMetricReader(
    metric_exporter,
    export_interval_millis=5000
)

# Configurar provider
meter_provider = MeterProvider(metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)

# Criar métrica
meter = metrics.get_meter(__name__)
counter = meter.create_counter(
    "trisla_intents_total",
    description="Total number of intents processed"
)

# Incrementar contador
counter.add(1, {"module": "sem-csmf", "status": "success"})
```

### 8.4 Exportação de Traces

**Exemplo (Python):**

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

# Criar trace
tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("process_intent") as span:
    span.set_attribute("intent.id", "intent-001")
    span.set_attribute("intent.tenant", "tenant-001")
    
    # Processar intent
    process_intent(intent)
    
    span.set_status(trace.Status(trace.StatusCode.OK))
```

### 8.5 Estrutura de Métricas Exportadas

**Métricas principais:**

| Métrica | Tipo | Descrição |
|---------|------|-----------|
| `trisla_intents_total` | Counter | Total de intents processados |
| `trisla_nests_generated_total` | Counter | Total de NESTs gerados |
| `trisla_decisions_total` | Counter | Total de decisões tomadas |
| `trisla_prediction_duration_seconds` | Histogram | Duração de predições ML |
| `trisla_decision_latency_seconds` | Histogram | Latência de decisões |
| `trisla_sla_compliance_rate` | Gauge | Taxa de compliance de SLA |

---

## 9. API de I-07 (REST NASP Integration)

### 9.1 Visão Geral

A interface **I-07** utiliza REST HTTP para integração com a plataforma NASP, executando ações reais em RAN, Transport e Core.

### 9.2 Endpoints do NASP Adapter

#### POST /api/v1/provision

**Descrição**: Provisiona slice no NASP.

**Request:**

```http
POST /api/v1/provision HTTP/1.1
Host: nasp-adapter:8085
Content-Type: application/json
Authorization: Bearer <JWT_TOKEN>

{
  "action_id": "action-001",
  "decision_id": "decision-001",
  "nest_id": "nest-intent-001",
  "tenant_id": "tenant-001",
  "domain": "RAN",
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
    }
  }
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
        "memory": "8Gi"
      }
    },
    "transport": {
      "bandwidth_allocated": "1Gbps"
    },
    "core": {
      "connections_allocated": 1000
    }
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
    "latency_ms": 8.2
  },
  "timestamp": "2025-01-19T10:30:00Z"
}
```

#### POST /api/v1/actions/{action_id}/status

**Descrição**: Consulta status de uma ação.

**Request:**

```http
POST /api/v1/actions/action-001/status HTTP/1.1
Host: nasp-adapter:8085
Authorization: Bearer <JWT_TOKEN>
```

**Response (200 OK):**

```json
{
  "action_id": "action-001",
  "status": "IN_PROGRESS",
  "progress": 0.65,
  "estimated_completion": "2025-01-19T10:31:00Z",
  "details": {
    "ran": "COMPLETED",
    "transport": "IN_PROGRESS",
    "core": "PENDING"
  }
}
```

### 9.3 Integração com NASP Real

**Endpoints NASP (exemplo):**

- **RAN**: `https://nasp-ran.local/api/v1/slices`
- **Transport**: `https://nasp-transport.local/api/v1/connections`
- **Core**: `https://nasp-core.local/api/v1/sessions`

**Autenticação:**

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context
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
def get_oauth_token():
    response = requests.post(
        'https://nasp.local/oauth/token',
        auth=('client_id', 'client_secret'),
        data={'grant_type': 'client_credentials'},
        verify='/etc/nasp/ca.crt'
    )
    return response.json()['access_token']

# Fazer requisição autenticada
token = get_oauth_token()
response = session.post(
    'https://nasp-ran.local/api/v1/slices',
    headers={'Authorization': f'Bearer {token}'},
    json=slice_config
)
```

---

## 10. Segurança das APIs

### 10.1 TLS

**TLS obrigatório para todas as comunicações HTTP/gRPC:**

```yaml
# Configuração TLS no Kubernetes
apiVersion: v1
kind: Secret
metadata:
  name: trisla-tls
  namespace: trisla
type: kubernetes.io/tls
data:
  tls.crt: <BASE64_CERT>
  tls.key: <BASE64_KEY>
```

**Configuração no código:**

```python
import ssl
import grpc
from grpc import ssl_channel_credentials

# Carregar certificados
with open('/etc/tls/tls.crt', 'rb') as f:
    cert = f.read()
with open('/etc/tls/tls.key', 'rb') as f:
    key = f.read()
with open('/etc/tls/ca.crt', 'rb') as f:
    ca_cert = f.read()

# Criar credenciais TLS
credentials = ssl_channel_credentials(
    root_certificates=ca_cert,
    private_key=key,
    certificate_chain=cert
)

# Criar canal seguro
channel = grpc.secure_channel('decision-engine:50051', credentials)
```

### 10.2 JWT (SEM-CSMF)

**Geração de token:**

```python
import jwt
from datetime import datetime, timedelta

def generate_jwt_token(tenant_id: str, secret_key: str) -> str:
    payload = {
        'tenant_id': tenant_id,
        'exp': datetime.utcnow() + timedelta(hours=1),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, secret_key, algorithm='HS256')
```

**Validação de token:**

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

@app.post("/api/v1/intents")
async def create_intent(
    intent: IntentRequest,
    token_payload: dict = Depends(verify_token)
):
    # Verificar autorização do tenant
    if token_payload['tenant_id'] != intent.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized tenant"
        )
    # Processar intent
    ...
```

### 10.3 Políticas de Acesso

**Network Policies (Kubernetes):**

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: sem-csmf-netpol
  namespace: trisla
spec:
  podSelector:
    matchLabels:
      app: sem-csmf
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: decision-engine
      ports:
        - protocol: TCP
          port: 8080
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: decision-engine
      ports:
        - protocol: TCP
          port: 50051
    - to:
        - podSelector:
            matchLabels:
              app: postgres
      ports:
        - protocol: TCP
          port: 5432
```

**Rate Limiting:**

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@limiter.limit("100/minute")
@app.post("/api/v1/intents")
async def create_intent(intent: IntentRequest):
    ...
```

---

## 11. Versionamento das APIs

### 11.1 Estratégia de Versionamento

O TriSLA utiliza versionamento semântico para APIs:

- **Versão atual**: v1.0.0
- **Formato**: `v<major>.<minor>.<patch>`

**Mudanças de versão:**
- **Major (v2.0.0)**: Breaking changes, requer migração
- **Minor (v1.1.0)**: Novas funcionalidades, compatível com v1.0.0
- **Patch (v1.0.1)**: Correções de bugs, compatível com v1.0.0

### 11.2 Versionamento em gRPC

**Incluir versão no package:**

```protobuf
package trisla.i01.v1;

service DecisionEngineService {
  rpc SendNESTMetadata(NESTMetadataRequest) returns (NESTMetadataResponse);
}
```

### 11.3 Versionamento em REST

**Incluir versão no path:**

```
/api/v1/intents
/api/v2/intents  // Futura versão
```

**Ou via header:**

```http
GET /api/intents HTTP/1.1
Host: sem-csmf:8080
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

---

## 12. Exemplos Práticos

### 12.1 Exemplo Completo: gRPC

**Cliente completo:**

```python
import grpc
from proto.proto import i01_interface_pb2
from proto.proto import i01_interface_pb2_grpc
import time

def send_nest_metadata():
    # Criar canal
    channel = grpc.insecure_channel('decision-engine:50051')
    stub = i01_interface_pb2_grpc.DecisionEngineServiceStub(channel)
    
    # Criar requisição
    request = i01_interface_pb2.NESTMetadataRequest(
        intent_id="intent-001",
        nest_id="nest-intent-001",
        tenant_id="tenant-001",
        service_type="eMBB",
        sla_requirements={
            "latency": "10ms",
            "throughput": "100Mbps"
        },
        nest_status="generated",
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    )
    
    try:
        # Enviar com timeout
        response = stub.SendNESTMetadata(
            request,
            timeout=5.0
        )
        
        if response.success:
            print(f"Decision ID: {response.decision_id}")
            
            # Consultar status
            status_request = i01_interface_pb2.DecisionStatusRequest(
                decision_id=response.decision_id
            )
            status_response = stub.GetDecisionStatus(
                status_request,
                timeout=5.0
            )
            print(f"Decision: {status_response.decision}")
        else:
            print(f"Error: {response.message}")
    except grpc.RpcError as e:
        print(f"gRPC error: {e.code()} - {e.details()}")
    finally:
        channel.close()
```

### 12.2 Exemplo Completo: REST

**Cliente REST completo:**

```python
import requests
from typing import Dict, Any

class TriSLAClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def create_intent(self, intent_data: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/api/v1/intents",
            json=intent_data,
            headers=self.headers,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    
    def get_nest(self, nest_id: str) -> Dict[str, Any]:
        response = requests.get(
            f"{self.base_url}/api/v1/nests/{nest_id}",
            headers=self.headers,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    
    def get_prediction(self, prediction_id: str) -> Dict[str, Any]:
        response = requests.get(
            f"{self.base_url}/api/v1/predictions/{prediction_id}",
            headers=self.headers,
            timeout=10
        )
        response.raise_for_status()
        return response.json()

# Uso
client = TriSLAClient("http://sem-csmf:8080", "jwt-token")

intent = client.create_intent({
    "tenant_id": "tenant-001",
    "intent": "Criar slice para aplicação de realidade aumentada",
    "priority": "high"
})

nest = client.get_nest(intent["nest_id"])
prediction = client.get_prediction(nest["prediction_id"])
```

### 12.3 Exemplo Completo: Kafka

**Producer completo:**

```python
from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
from datetime import datetime

class KafkaMessageProducer:
    def __init__(self, bootstrap_servers: list):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            acks='all',  # Aguardar confirmação de todos os replicas
            retries=3,
            max_in_flight_requests_per_connection=1
        )
    
    def send_prediction(self, prediction_data: dict):
        message = {
            "interface": "I-03",
            "source": "ml-nsmf",
            "destination": "decision-engine",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "version": "1.0.0",
            **prediction_data
        }
        
        future = self.producer.send('trisla-ml-predictions', value=message)
        
        try:
            record_metadata = future.get(timeout=10)
            print(f"Message sent to {record_metadata.topic}[{record_metadata.partition}]")
        except KafkaError as e:
            print(f"Failed to send message: {e}")

# Uso
producer = KafkaMessageProducer(['kafka:9092'])
producer.send_prediction({
    "prediction_id": "pred-001",
    "nest_id": "nest-intent-001",
    "viability_score": 0.87,
    "recommendation": "ACCEPT"
})
```

**Consumer completo:**

```python
from kafka import KafkaConsumer
from kafka.errors import KafkaError
import json

class KafkaMessageConsumer:
    def __init__(self, topic: str, group_id: str, bootstrap_servers: list):
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            group_id=group_id,
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            max_poll_records=10
        )
    
    def consume(self, callback):
        try:
            for message in self.consumer:
                try:
                    callback(message.value)
                except Exception as e:
                    print(f"Error processing message: {e}")
        except KafkaError as e:
            print(f"Kafka error: {e}")
        finally:
            self.consumer.close()

# Uso
def process_prediction(prediction):
    print(f"Processing prediction: {prediction['prediction_id']}")
    # Processar predição
    ...

consumer = KafkaMessageConsumer(
    'trisla-ml-predictions',
    'decision-engine-consumer',
    ['kafka:9092']
)
consumer.consume(process_prediction)
```

---

## 13. Fluxos E2E com Chamadas Encadeadas

### 13.1 Fluxo Completo: Intent → Decisão → Ação

**Passo 1: Criar Intent (SEM-CSMF)**

```http
POST /api/v1/intents HTTP/1.1
Host: sem-csmf:8080
Content-Type: application/json
Authorization: Bearer <JWT_TOKEN>

{
  "tenant_id": "tenant-001",
  "intent": "Criar slice para aplicação de realidade aumentada com latência < 10ms e throughput > 1Gbps",
  "priority": "high"
}
```

**Resposta:**

```json
{
  "intent_id": "intent-001",
  "status": "received",
  "nest_id": "nest-intent-001"
}
```

**Passo 2: SEM-CSMF envia NEST via gRPC (I-01)**

```python
# SEM-CSMF → Decision Engine
request = NESTMetadataRequest(
    intent_id="intent-001",
    nest_id="nest-intent-001",
    tenant_id="tenant-001",
    service_type="eMBB",
    sla_requirements={
        "latency": "10ms",
        "throughput": "1Gbps"
    }
)
response = stub.SendNESTMetadata(request)
# response.decision_id = "decision-001"
```

**Passo 3: SEM-CSMF envia NEST para ML-NSMF (I-02)**

```http
POST /api/v1/nest HTTP/1.1
Host: ml-nsmf:8081
Content-Type: application/json

{
  "nest_id": "nest-intent-001",
  "intent_id": "intent-001",
  "network_slices": [...]
}
```

**Passo 4: ML-NSMF publica predição (I-03)**

```python
# ML-NSMF → Kafka → Decision Engine
producer.send('trisla-ml-predictions', value={
    "interface": "I-03",
    "prediction_id": "pred-001",
    "nest_id": "nest-intent-001",
    "viability_score": 0.87,
    "recommendation": "ACCEPT"
})
```

**Passo 5: Decision Engine toma decisão e publica (I-04, I-05)**

```python
# Decision Engine → BC-NSSMF (I-04)
producer.send('trisla-i04-decisions', value={
    "interface": "I-04",
    "decision_id": "decision-001",
    "decision": "ACCEPT",
    ...
})

# Decision Engine → SLA-Agents (I-05)
producer.send('trisla-i05-actions', value={
    "interface": "I-05",
    "action_id": "action-001",
    "action_type": "PROVISION_SLICE",
    "domain": "RAN",
    ...
})
```

**Passo 6: SLA-Agent Layer executa ação no NASP (I-06, I-07)**

```http
POST /api/v1/provision HTTP/1.1
Host: nasp-adapter:8085
Content-Type: application/json

{
  "action_id": "action-001",
  "domain": "RAN",
  "slice_config": {...}
}
```

### 13.2 Diagrama de Sequência

```
Tenant → SEM-CSMF → Decision Engine
                ↓
            ML-NSMF (I-02)
                ↓
         Kafka (I-03)
                ↓
         Decision Engine
                ↓
    ┌───────────┴───────────┐
    ↓                       ↓
BC-NSSMF (I-04)    SLA-Agents (I-05)
    ↓                       ↓
Blockchain          NASP Adapter (I-06, I-07)
                            ↓
                          NASP
```

---

## 14. Apêndice

### 14.1 Arquivos `.proto` Explicados

**Estrutura do arquivo `proto/i01_interface.proto`:**

```protobuf
syntax = "proto3";

package trisla.i01;

// Serviço gRPC
service DecisionEngineService {
  rpc SendNESTMetadata(NESTMetadataRequest) returns (NESTMetadataResponse);
  rpc GetDecisionStatus(DecisionStatusRequest) returns (DecisionStatusResponse);
}

// Mensagens
message NESTMetadataRequest {
  string intent_id = 1;
  string nest_id = 2;
  // ...
}

message NESTMetadataResponse {
  bool success = 1;
  string decision_id = 2;
  // ...
}
```

**Geração de código Python:**

```bash
# Gerar código Python a partir do .proto
python -m grpc_tools.protoc \
  -I. \
  --python_out=. \
  --grpc_python_out=. \
  proto/i01_interface.proto
```

### 14.2 Estruturas JSON das Mensagens Principais

**Intent Request:**

```json
{
  "tenant_id": "tenant-001",
  "intent": "Criar slice para aplicação de realidade aumentada",
  "priority": "high",
  "metadata": {
    "application_type": "AR",
    "expected_users": 1000
  }
}
```

**NEST Structure:**

```json
{
  "nest_id": "nest-intent-001",
  "intent_id": "intent-001",
  "tenant_id": "tenant-001",
  "status": "generated",
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
    "generated_at": "2025-01-19T10:30:00Z",
    "gst_version": "1.0"
  }
}
```

**Decision Structure:**

```json
{
  "decision_id": "decision-001",
  "intent_id": "intent-001",
  "nest_id": "nest-intent-001",
  "tenant_id": "tenant-001",
  "decision": "ACCEPT",
  "reason": "SLA requirements met, ML prediction positive",
  "ml_prediction": {
    "prediction_id": "pred-001",
    "viability_score": 0.87,
    "confidence": 0.92
  },
  "timestamp": "2025-01-19T10:30:10Z",
  "details": {
    "estimated_latency": "8ms",
    "estimated_throughput": "1.2Gbps"
  }
}
```

**Action Structure:**

```json
{
  "action_id": "action-001",
  "decision_id": "decision-001",
  "intent_id": "intent-001",
  "nest_id": "nest-intent-001",
  "action_type": "PROVISION_SLICE",
  "domain": "RAN",
  "action_data": {
    "slice_id": "slice-001",
    "resources": {
      "cpu": 4,
      "memory": "8Gi",
      "bandwidth": "1Gbps"
    }
  },
  "priority": "high",
  "timestamp": "2025-01-19T10:30:15Z"
}
```

---

## Conclusão

Este documento fornece a referência completa das APIs do TriSLA. Para integração, consulte os exemplos práticos fornecidos em cada seção.

**Última atualização:** 2025-01-XX  
**Versão do documento:** 1.0.0  
**Versão das APIs:** 1.0.0

**Referências:**
- `README_OPERATIONS_PROD.md`: Guia de operações
- `TROUBLESHOOTING_TRISLA.md`: Guia de troubleshooting
- `SECURITY_HARDENING.md`: Guia de segurança


