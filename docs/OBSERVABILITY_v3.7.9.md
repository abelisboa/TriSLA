# Observability TriSLA v3.7.9 — Guia Completo

**Versão:** 3.7.9  
**Data:** 2025-01-XX  
**Status:** ✅ Integração Completa

---

## 📋 Visão Geral

A versão **3.7.9** do TriSLA integra **observability completa** em todos os módulos Python, fornecendo métricas Prometheus e traces OpenTelemetry para monitoramento end-to-end do sistema.

---

## 🎯 Módulos Instrumentados

| Módulo | Métricas | Traces | Status |
|--------|----------|--------|--------|
| **SEM-CSMF** | ✅ | ✅ | ✅ Completo |
| **ML-NSMF** | ✅ | ✅ | ✅ Completo |
| **Decision Engine** | ✅ | ✅ | ✅ Completo |
| **BC-NSSMF** | ✅ | ✅ | ✅ Completo |
| **SLA-Agent Layer** | ✅ | ✅ | ✅ Completo |

---

## 📦 Componentes de Observability

### 1. Métricas Prometheus

**Localização:** `apps/{module}/src/observability/metrics.py`

**Funcionalidades:**
- Contadores de requisições HTTP
- Histogramas de latência
- Gauges de status de saúde
- Métricas customizadas por módulo

**Endpoint:** `/metrics` (porta padrão do módulo)

**Exemplo:**
```python
from observability.metrics import metrics

# Incrementar contador
metrics.http_requests_total.labels(method="POST", endpoint="/api/v1/intents").inc()

# Registrar latência
metrics.http_request_duration_seconds.labels(method="POST", endpoint="/api/v1/intents").observe(0.123)
```

### 2. Traces OpenTelemetry

**Localização:** `apps/{module}/src/observability/tracing_base.py` e `tracing.py`

**Funcionalidades:**
- Traces distribuídos entre módulos
- Propagação de contexto (B3 e TraceContext)
- Spans automáticos para FastAPI e gRPC
- Exportação via OTLP gRPC

**Configuração:**
```python
from observability.tracing import setup_tracer, get_tracer

# Setup (no início da aplicação)
setup_tracer(
    service_name="trisla-sem-csmf",
    otlp_endpoint="http://otel-collector:4317"
)

# Criar span
tracer = get_tracer(__name__)
with tracer.start_as_current_span("process_intent") as span:
    span.set_attribute("intent_id", intent_id)
    # ... processamento ...
```

### 3. Propagação de Contexto

**Protocolos Suportados:**
- **B3**: `opentelemetry-propagator-b3`
- **TraceContext**: Incluído no `opentelemetry-api`

**Uso:**
```python
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.trace.propagation.b3 import B3MultiFormat

# Propagação automática via CompositeHTTPPropagator
```

---

## 🔧 Dependências

### Requirements.txt

Todos os módulos incluem as seguintes dependências:

```txt
# OpenTelemetry
opentelemetry-api>=1.24.0
opentelemetry-sdk>=1.24.0
opentelemetry-instrumentation-fastapi>=0.44b0
opentelemetry-exporter-otlp-proto-grpc>=1.24.0
opentelemetry-instrumentation-grpc>=0.44b0
opentelemetry-propagator-b3>=1.24.0

# Prometheus
prometheus_client>=0.20.0
```

**Nota:** `TraceContextTextMapPropagator` está incluído no `opentelemetry-api` e não requer pacote separado.

---

## 🚀 Integração nos Módulos

### Estrutura de Arquivos

```
apps/{module}/src/
├── observability/
│   ├── __init__.py
│   ├── metrics.py          # Métricas Prometheus
│   ├── tracing_base.py     # Setup base OpenTelemetry
│   └── tracing.py          # Traces específicos do módulo
└── main.py                 # Inicialização da aplicação
```

### Inicialização

**Exemplo (SEM-CSMF):**
```python
# apps/sem-csmf/src/main.py
from observability.metrics import setup_metrics
from observability.tracing import setup_tracer

# Setup observability
setup_metrics()
setup_tracer(
    service_name="trisla-sem-csmf",
    otlp_endpoint=os.getenv("OTLP_ENDPOINT", "http://otel-collector:4317")
)

# Inicializar FastAPI com instrumentação
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
FastAPIInstrumentor.instrument_app(app)
```

---

## 📊 Métricas Expostas

### Métricas Padrão (Todos os Módulos)

- `trisla_http_requests_total`: Total de requisições HTTP
- `trisla_http_request_duration_seconds`: Latência de requisições HTTP
- `trisla_health_status`: Status de saúde do módulo (1 = saudável, 0 = não saudável)

### Métricas Customizadas por Módulo

#### SEM-CSMF
- `trisla_intents_processed_total`: Total de intents processados
- `trisla_nest_generation_duration_seconds`: Tempo de geração de NEST

#### ML-NSMF
- `trisla_predictions_total`: Total de predições realizadas
- `trisla_prediction_duration_seconds`: Tempo de predição

#### Decision Engine
- `trisla_decisions_total`: Total de decisões tomadas
- `trisla_decision_duration_seconds`: Tempo de decisão

#### BC-NSSMF
- `trisla_blockchain_transactions_total`: Total de transações blockchain
- `trisla_blockchain_transaction_duration_seconds`: Tempo de transação

#### SLA-Agent Layer
- `trisla_agent_actions_total`: Total de ações executadas pelos agentes
- `trisla_agent_action_duration_seconds`: Tempo de execução de ações

---

## 🔍 Traces e Spans

### Spans Automáticos

**FastAPI:**
- Span por endpoint HTTP
- Atributos: `http.method`, `http.route`, `http.status_code`

**gRPC:**
- Span por chamada RPC
- Atributos: `rpc.method`, `rpc.service`, `rpc.status_code`

### Spans Customizados

**Exemplo:**
```python
from observability.tracing import get_tracer

tracer = get_tracer(__name__)

with tracer.start_as_current_span("process_intent") as span:
    span.set_attribute("intent.id", intent_id)
    span.set_attribute("intent.service_type", service_type)
    
    # Processamento...
    
    span.set_status(Status(StatusCode.OK))
```

---

## 🐳 Build e Deploy

### Build das Imagens

As imagens Docker já incluem toda a instrumentação:

```bash
# Build individual
docker build -t ghcr.io/abelisboa/trisla-sem-csmf:3.7.9 apps/sem-csmf

# Build e push de todos os módulos
bash build_push_3.7.9.sh
```

### Variáveis de Ambiente

**OTLP Endpoint:**
```yaml
env:
  - name: OTLP_ENDPOINT
    value: "http://otel-collector:4317"
```

**Prometheus Port:**
- Métricas expostas na porta padrão do módulo (`/metrics`)
- Exemplo: `http://trisla-sem-csmf:8080/metrics`

---

## 📈 Visualização

### Prometheus

**Scraping Config:**
```yaml
scrape_configs:
  - job_name: 'trisla'
    kubernetes_sd_configs:
      - role: pod
        namespaces:
          names:
            - trisla
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app_kubernetes_io_name]
        action: keep
        regex: trisla
```

### Grafana

**Dashboards:**
- Overview do TriSLA
- Métricas por módulo
- Latência das interfaces I-01 a I-07
- Health status

### Jaeger/Tempo

**Traces distribuídos:**
- Visualização de traces end-to-end
- Análise de latência por span
- Detecção de bottlenecks

---

## 🔧 Troubleshooting

### Métricas Não Aparecem

**Verificar:**
```bash
# Testar endpoint de métricas
curl http://trisla-sem-csmf:8080/metrics

# Verificar ServiceMonitor
kubectl get servicemonitor -n trisla

# Verificar targets no Prometheus
kubectl port-forward -n monitoring svc/prometheus 9090:9090
# Acessar: http://localhost:9090/targets
```

### Traces Não Aparecem

**Verificar:**
```bash
# Verificar logs do módulo
kubectl logs -n trisla deployment/trisla-sem-csmf | grep -i otlp

# Verificar OTLP Collector
kubectl logs -n monitoring deployment/otel-collector

# Verificar conectividade
kubectl exec -n trisla deployment/trisla-sem-csmf -- \
  curl -v http://otel-collector:4317
```

---

## 📚 Documentação Adicional

- **Guia de Build e Push**: [`TRISLA_PROMPTS_v3.5/8_NASP_INSTRUCOES/GUIA_BUILD_PUSH_IMAGENS_3.7.9.md`](../../TRISLA_PROMPTS_v3.5/8_NASP_INSTRUCOES/GUIA_BUILD_PUSH_IMAGENS_3.7.9.md)
- **Integração Observability**: [`EXECUCAO_INTEGRACAO_OBSERVABILITY_3.7.9.md`](../../EXECUCAO_INTEGRACAO_OBSERVABILITY_3.7.9.md)
- **Validação Build**: [`VALIDACAO_BUILD_3.7.9_PROXIMOS_PASSOS.md`](../../VALIDACAO_BUILD_3.7.9_PROXIMOS_PASSOS.md)

---

**Status:** ✅ Documentação completa da observability v3.7.9

