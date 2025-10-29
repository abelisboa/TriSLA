# TriSLA Interfaces

Documentação das interfaces internas da arquitetura TriSLA conforme especificado na FASE 3 da dissertação.

## 🎯 Visão Geral

As interfaces internas conectam os módulos da arquitetura TriSLA, permitindo comunicação bidirecional e troca de dados em tempo real:

- **I-01**: SEM-NSMF → ML-NSMF (gRPC)
- **I-02**: ML-NSMF → Decision Engine (gRPC)
- **I-03**: ML-NSMF ← NASP Telemetry (Kafka)
- **I-04**: BC-NSSMF ↔ Oracles (REST)
- **I-05**: SLA-Agent Layer ↔ Decision Engine (Kafka)
- **I-06**: Decision Engine ↔ NASP API (REST)
- **I-07**: Decision Engine ↔ NASP API (REST)

## 🏗️ Arquitetura das Interfaces

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   SEM-NSMF      │    │   ML-NSMF       │    │   BC-NSSMF      │
│  (Semantic)     │    │   (AI/ML)       │    │  (Blockchain)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │ I-01 (gRPC)           │ I-02 (gRPC)           │ I-04 (REST)
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DECISION ENGINE                             │
│  • Orquestração de módulos                                    │
│  • Políticas SLA-aware                                        │
│  • Interface I-05 (Kafka)                                     │
│  • Interface I-06 (REST)                                      │
│  • Interface I-07 (REST)                                      │
└─────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────────┐
│   NASP API      │    │   Oracles       │
│  (Ativação)     │    │  (Externos)     │
└─────────────────┘    └─────────────────┘
```

## 📡 Interfaces Implementadas

### **I-01: SEM-NSMF → ML-NSMF (gRPC)**

**Propósito**: Enviar templates NEST validados para ML-NSMF

**Localização**: `apps/semantic/interfaces/i01_ml_nsmf.py`

**Funcionalidades**:
- Envio de templates NEST validados
- Processamento em lote
- Validação de templates
- Consulta de status

**Exemplo de Uso**:
```python
# Criar template NEST
template = NESTTemplate(
    template_id="template-001",
    slice_type="URLLC",
    requirements={"latency": 10, "reliability": 99.9},
    semantic_analysis={"confidence": 0.95},
    validation_status="validated",
    timestamp=datetime.now(),
    confidence=0.95,
    metadata={}
)

# Enviar para ML-NSMF
response = await interface.send_nest_template(template)
```

### **I-02: ML-NSMF → Decision Engine (gRPC)**

**Propósito**: Enviar predições e resultados XAI para Decision Engine

**Localização**: `apps/decision_engine/interfaces/i02_ml_nsmf.py`

**Funcionalidades**:
- Envio de predições ML
- Explicações XAI
- Disponibilidade de recursos
- Viabilidade de SLA

**Exemplo de Uso**:
```python
# Obter predição do ML-NSMF
prediction = await interface.get_prediction(nest_template, requirements)

# Obter explicação XAI
explanation = await interface.get_xai_explanation(nest_template, requirements)
```

### **I-03: ML-NSMF ← NASP Telemetry (Kafka)**

**Propósito**: Consumir telemetria em tempo real do NASP

**Localização**: `apps/ai/interfaces/i03_nasp_telemetry.py`

**Funcionalidades**:
- Consumo de métricas em tempo real
- Processamento de eventos
- Alertas e notificações
- Callbacks personalizados

**Exemplo de Uso**:
```python
# Registrar callback para métricas
async def metrics_callback(metrics):
    print(f"Métricas recebidas: {metrics}")

interface.register_metrics_callback(metrics_callback)

# Iniciar consumo
await interface.start_consuming_telemetry()
```

### **I-04: BC-NSSMF ↔ Oracles (REST)**

**Propósito**: Comunicação com oráculos externos para dados e eventos

**Localização**: `apps/blockchain/interfaces/i04_oracle_interface.py`

**Funcionalidades**:
- Obtenção de dados de rede
- Dados de mercado
- Eventos externos
- Publicação de eventos de contrato

**Exemplo de Uso**:
```python
# Obter eventos de rede
network_events = await interface.get_network_events()

# Publicar violação de SLA
violation_data = {
    "slice_id": "slice-001",
    "violation_type": "latency",
    "threshold": 10,
    "actual_value": 15
}
responses = await interface.publish_sla_violation(violation_data)
```

### **I-05: SLA-Agent Layer ↔ Decision Engine (Kafka)**

**Propósito**: Comunicação entre agentes SLA e Decision Engine

**Localização**: `apps/sla_agents/interfaces/i05_kafka_interface.py`

**Funcionalidades**:
- Publicação de métricas SLA
- Violações de SLA
- Status de agentes
- Comandos do Decision Engine

**Exemplo de Uso**:
```python
# Publicar métricas
await interface.publish_metrics("RAN", metrics)

# Publicar violação
await interface.publish_violation("RAN", violation)

# Consumir comandos
await interface.start_consuming_commands(callback)
```

### **I-06: Decision Engine ↔ NASP API (REST)**

**Propósito**: Ativação e ajustes de slice no NASP

**Localização**: `apps/decision_engine/interfaces/i06_nasp_api.py`

**Funcionalidades**:
- Ativação de slices
- Desativação de slices
- Ajustes de configuração
- Status da rede

**Exemplo de Uso**:
```python
# Ativar slice
slice_config = {
    "slice_id": "slice-001",
    "type": "URLLC",
    "requirements": {"latency": 10, "reliability": 99.9}
}
result = await interface.activate_slice(slice_config)

# Obter status da rede
status = await interface.get_network_status()
```

### **I-07: Decision Engine ↔ NASP API (REST)**

**Propósito**: Comunicação bidirecional com NASP para monitoramento

**Localização**: `apps/decision_engine/interfaces/i07_nasp_api.py`

**Funcionalidades**:
- Ativação de slices
- Modificação de slices
- Status de slices
- Recursos disponíveis

**Exemplo de Uso**:
```python
# Ativar slice
slice_config = SliceConfiguration(
    slice_id="slice-001",
    slice_type="URLLC",
    requirements={"latency": 10, "reliability": 99.9},
    resources={"cpu": 100, "memory": 512},
    policies={},
    metadata={}
)
response = await interface.activate_slice(slice_config)

# Obter status da NASP
status = await interface.get_nasp_status()
```

## 🔧 Configuração

### **Variáveis de Ambiente**

```bash
# gRPC
GRPC_PORT=50051
ML_NSMF_URL=ml-nsmf:50051

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
TELEMETRY_TOPIC=nasp-telemetry
METRICS_TOPIC=sla-metrics

# REST APIs
NASP_API_URL=http://nasp-api:8080
ORACLE_NETWORK_URL=http://network-oracle:8080
ORACLE_MARKET_URL=http://market-oracle:8080
```

### **Configuração de Tópicos Kafka**

```yaml
# Tópicos para Interface I-03
nasp-telemetry:
  partitions: 3
  replication-factor: 1
  retention: 7d

nasp-metrics:
  partitions: 3
  replication-factor: 1
  retention: 7d

# Tópicos para Interface I-05
sla-metrics:
  partitions: 3
  replication-factor: 1
  retention: 7d

sla-violations:
  partitions: 3
  replication-factor: 1
  retention: 7d
```

## 🧪 Testes

### **Teste Automatizado**

```bash
# Executar teste de todas as interfaces
./scripts/test_interfaces.sh
```

### **Teste Individual**

```bash
# Testar Interface I-01
python apps/semantic/interfaces/i01_ml_nsmf.py

# Testar Interface I-03
python apps/ai/interfaces/i03_nasp_telemetry.py

# Testar Interface I-04
python apps/blockchain/interfaces/i04_oracle_interface.py

# Testar Interface I-07
python apps/decision_engine/interfaces/i07_nasp_api.py
```

## 📊 Monitoramento

### **Métricas de Interface**

- `interface_requests_total`: Total de requisições por interface
- `interface_response_time_seconds`: Tempo de resposta por interface
- `interface_errors_total`: Total de erros por interface
- `interface_throughput_per_second`: Throughput por interface

### **Logs Estruturados**

```json
{
  "timestamp": "2025-10-29T18:00:00Z",
  "level": "INFO",
  "interface": "I-01",
  "operation": "send_nest_template",
  "template_id": "template-001",
  "status": "success",
  "duration_ms": 150
}
```

## 🔗 Integração

### **Fluxo de Dados**

1. **SEM-NSMF** valida requisitos e envia template via **I-01**
2. **ML-NSMF** processa template e envia predição via **I-02**
3. **ML-NSMF** consome telemetria via **I-03**
4. **BC-NSSMF** obtém dados externos via **I-04**
5. **SLA-Agent Layer** publica métricas via **I-05**
6. **Decision Engine** ativa slices via **I-06** e **I-07**

### **Tratamento de Erros**

- **Retry automático**: 3 tentativas com backoff exponencial
- **Circuit breaker**: Proteção contra falhas em cascata
- **Fallback**: Respostas padrão em caso de falha
- **Logging**: Registro detalhado de erros e exceções

## 📚 Referências

- [TriSLA Architecture](https://github.com/abelisboa/TriSLA-Portal)
- [Dissertação - Capítulo 6](docs/Referencia_Tecnica_TriSLA.md)
- [Interfaces Internas](docs/Referencia_Tecnica_TriSLA.md#a-interfaces-internas-i-)

## 👥 Autores

- **Abel Lisboa** - *Desenvolvimento* - [@abelisboa](https://github.com/abelisboa)
- **NASP-UNISINOS** - *Infraestrutura*

---

**TriSLA Interfaces** - Comunicação Interna da Arquitetura TriSLA 🔗
