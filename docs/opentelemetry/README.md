# TriSLA OpenTelemetry

Instrumentação OpenTelemetry para observabilidade completa da arquitetura TriSLA conforme especificado na FASE 4 da dissertação.

## 🎯 Visão Geral

O OpenTelemetry fornece observabilidade unificada através de:

- **Traces**: Rastreamento de requisições entre módulos
- **Métricas**: Monitoramento de performance e SLA
- **Logs**: Registro estruturado de eventos

## 🏗️ Arquitetura de Observabilidade

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   SEM-NSMF      │    │   ML-NSMF       │    │   BC-NSSMF      │
│  (Instrumented) │    │  (Instrumented) │    │  (Instrumented) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                OPENTELEMETRY COLLECTOR                         │
│  • Receivers: OTLP, Prometheus, Filelog                       │
│  • Processors: Batch, Memory Limiter, Attributes              │
│  • Exporters: Jaeger, Prometheus, Loki                        │
└─────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Jaeger      │    │   Prometheus    │    │      Loki       │
│   (Traces)      │    │   (Metrics)     │    │     (Logs)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Funcionalidades

### **1. Instrumentação Automática**

#### **Decorators**
```python
from apps.common.telemetry import trace_function, measure_time, log_execution

@trace_function(operation_name="process_sla_request")
@measure_time(metric_name="sla_processing_time")
@log_execution(level=logging.INFO)
async def process_sla_request(request):
    # Implementação da função
    pass
```

#### **Instrumentação de Classe**
```python
from apps.common.telemetry import instrument_class

@instrument_class(class_name="DecisionEngine", methods=["make_decision", "evaluate_policy"])
class DecisionEngine:
    def make_decision(self, request):
        # Implementação
        pass
```

### **2. Métricas Customizadas**

#### **Métricas de SLA**
```python
from apps.common.telemetry import create_trisla_metrics

metrics = create_trisla_metrics("decision-engine")

# Registrar violação de SLA
metrics.record_sla_violation("RAN", "latency", "critical")

# Registrar slice ativado
metrics.record_slice_activated("URLLC", "slice-001")

# Definir disponibilidade SLA
metrics.set_sla_availability(99.9, "RAN")
```

#### **Métricas de Performance**
```python
# Registrar tempo de resposta
metrics.record_response_time(0.150, "decision", "success")

# Registrar requisição
metrics.record_request("decision", "success")

# Definir throughput
metrics.set_throughput(100.5)
```

### **3. Contexto de Traces**

#### **Gerenciamento de Traces**
```python
from apps.common.telemetry import create_trace_manager

trace_manager = create_trace_manager("decision-engine")

# Iniciar span
trace_context = trace_manager.start_span(
    operation_name="process_decision",
    attributes={"slice_id": "slice-001", "type": "URLLC"}
)

# Adicionar evento
trace_manager.add_event(trace_context, "policy_evaluated", {
    "policy_name": "URLLC_Latency_Critical",
    "result": "accepted"
})

# Finalizar span
trace_manager.end_span(trace_context, "success")
```

#### **Propagação de Contexto**
```python
from apps.common.telemetry import create_trace_propagator

propagator = create_trace_propagator()

# Injetar contexto em requisição
carrier = {}
propagator.inject_context(trace_context, carrier)

# Extrair contexto de requisição
extracted_context = propagator.extract_context(carrier)
```

## 🔧 Configuração

### **Variáveis de Ambiente**

```bash
# OpenTelemetry
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
OTEL_SERVICE_NAME=trisla-service
OTEL_SERVICE_VERSION=1.0.0
OTEL_RESOURCE_ATTRIBUTES=environment=production,cluster=trisla-cluster

# Instrumentação
ENABLE_AUTO_INSTRUMENTATION=true
OTEL_LOG_LEVEL=INFO
```

### **Configuração do Collector**

```yaml
# monitoring/otel-collector/otel-collector.yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  batch:
    timeout: 1s
    send_batch_size: 1024

exporters:
  jaeger:
    endpoint: jaeger:14250
  prometheus:
    endpoint: "0.0.0.0:8889"
  loki:
    endpoint: http://loki:3100/loki/api/v1/push
```

## 🚀 Deploy

### **OpenTelemetry Collector**

```bash
# Aplicar configuração
kubectl apply -f monitoring/otel-collector/otel-collector.yaml

# Aplicar deployment
kubectl apply -f monitoring/otel-collector/deployment.yaml

# Verificar status
kubectl get pods -n trisla-nsp -l app=otel-collector
```

### **Instrumentação nos Módulos**

```python
# Em cada módulo, adicionar no início do main.py
from apps.common.telemetry import auto_setup_telemetry

# Configuração automática
auto_setup_telemetry()
```

## 🧪 Testes

### **Teste Automatizado**

```bash
# Executar teste completo
./scripts/test_opentelemetry.sh
```

### **Teste Manual**

```bash
# Verificar collector
kubectl logs -n trisla-nsp -l app=otel-collector

# Verificar métricas
kubectl port-forward -n trisla-nsp svc/otel-collector 8889:8889
curl http://localhost:8889/metrics

# Verificar traces no Jaeger
kubectl port-forward -n trisla-nsp svc/jaeger 16686:16686
# Acessar http://localhost:16686
```

## 📊 Monitoramento

### **Métricas Disponíveis**

#### **Métricas de SLA**
- `trisla_sla_violations_total`: Total de violações de SLA
- `trisla_sla_latency_seconds`: Latência de processamento SLA
- `trisla_sla_availability_percent`: Disponibilidade SLA atual

#### **Métricas de Performance**
- `trisla_response_time_seconds`: Tempo de resposta das operações
- `trisla_requests_total`: Total de requisições processadas
- `trisla_errors_total`: Total de erros processados
- `trisla_throughput_per_second`: Throughput atual

#### **Métricas de Sistema**
- `trisla_cpu_usage_percent`: Uso de CPU atual
- `trisla_memory_usage_bytes`: Uso de memória atual
- `trisla_active_connections`: Conexões ativas

#### **Métricas de Negócio**
- `trisla_decisions_total`: Total de decisões tomadas
- `trisla_ml_predictions_total`: Total de predições ML
- `trisla_semantic_analyses_total`: Total de análises semânticas
- `trisla_blockchain_validations_total`: Total de validações blockchain

### **Traces Disponíveis**

#### **Operações Rastreadas**
- `process_sla_request`: Processamento de requisição SLA
- `make_decision`: Tomada de decisão pelo Decision Engine
- `evaluate_policy`: Avaliação de política SLA
- `activate_slice`: Ativação de slice no NASP
- `collect_metrics`: Coleta de métricas pelos agentes SLA

#### **Atributos de Trace**
- `service.name`: Nome do serviço
- `service.version`: Versão do serviço
- `slice_id`: ID do slice
- `slice_type`: Tipo do slice (URLLC, eMBB, mMTC)
- `policy_name`: Nome da política aplicada
- `decision_result`: Resultado da decisão

### **Logs Estruturados**

```json
{
  "timestamp": "2025-10-29T18:00:00Z",
  "level": "INFO",
  "service": "decision-engine",
  "trace_id": "1234567890abcdef",
  "span_id": "abcdef1234567890",
  "event": "decision_made",
  "slice_id": "slice-001",
  "decision": "ACCEPT",
  "confidence": 0.95,
  "policy": "URLLC_Latency_Critical"
}
```

## 🔗 Integração

### **Com Jaeger**
- **URL**: http://jaeger:16686
- **Funcionalidade**: Visualização de traces
- **Filtros**: Por serviço, operação, tempo

### **Com Prometheus**
- **URL**: http://prometheus:9090
- **Funcionalidade**: Consulta de métricas
- **Queries**: PromQL para análise

### **Com Loki**
- **URL**: http://loki:3100
- **Funcionalidade**: Consulta de logs
- **Filtros**: Por serviço, nível, tempo

## 📚 Referências

- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [TriSLA Architecture](https://github.com/abelisboa/TriSLA-Portal)
- [Dissertação - Capítulo 7](docs/Referencia_Tecnica_TriSLA.md)

## 👥 Autores

- **Abel Lisboa** - *Desenvolvimento* - [@abelisboa](https://github.com/abelisboa)
- **NASP-UNISINOS** - *Infraestrutura*

---

**TriSLA OpenTelemetry** - Observabilidade Unificada da Arquitetura TriSLA 📊
