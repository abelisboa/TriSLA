# Observability TriSLA v3.7.10 — Guia Completo

**Versão:** 3.7.10  
**Data:** 2025-12-05  
**Status:** ✅ Integração Completa e Deployado

---

## 📋 Visão Geral

A versão **3.7.10** do TriSLA integra **observabilidade completa** em todos os módulos Python, fornecendo métricas Prometheus e traces OpenTelemetry para monitoramento end-to-end do sistema. O sistema está **deployado e operacional** no ambiente NASP com ServiceMonitors configurados e OTEL Collector funcionando.

---

## 🎯 Módulos Instrumentados

| Módulo | Métricas | Traces | Status | Endpoint |
|--------|----------|--------|--------|----------|
| **SEM-CSMF** | ✅ | ✅ | ✅ Completo | `:8080/metrics` |
| **ML-NSMF** | ✅ | ✅ | ✅ Completo | `:8081/metrics` |
| **Decision Engine** | ✅ | ✅ | ✅ Completo | `:8082/metrics` |
| **BC-NSSMF** | ✅ | ✅ | ✅ Completo | `:8083/metrics` |
| **SLA-Agent Layer** | ✅ | ✅ | ✅ Completo | `:8084/metrics` |

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

**Status de Deploy:**
- ✅ **ServiceMonitors**: 6 configurados e ativos
  - `trisla-api-backend`
  - `trisla-bc-nssmf`
  - `trisla-decision-engine`
  - `trisla-ml-nsmf`
  - `trisla-sem-csmf`
  - `trisla-sla-agent-layer`
- ✅ **Prometheus**: Scraping automático via ServiceMonitors
- ✅ **Endpoints**: Todos os módulos expõem `/metrics` funcionando

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

**Status de Deploy:**
- ✅ **OTEL Collector**: Deployado no namespace `trisla`
  - **Deployment**: `trisla-otel-collector`
  - **Serviço**: `trisla-otel-collector` (ClusterIP, porta 4317)
  - **Versão**: 0.141.0
  - **Status**: Running
- ✅ **OTLP_ENDPOINT**: Configurado em todos os pods
- ✅ **Traces**: Funcionando (requer tráfego de API real)

**Configuração:**
```python
from observability.tracing import setup_tracer, get_tracer

# Setup (no início da aplicação)
setup_tracer(
    service_name="trisla-sem-csmf",
    otlp_endpoint="http://trisla-otel-collector.trisla.svc.cluster.local:4317"
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
    otlp_endpoint=os.getenv("OTLP_ENDPOINT", "http://trisla-otel-collector.trisla.svc.cluster.local:4317")
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
docker build -t ghcr.io/abelisboa/trisla-sem-csmf:3.7.10 apps/sem-csmf

# Build e push de todos os módulos
bash build_push_3.7.10.sh
```

**Status:**
- ✅ **7 imagens construídas** com tag `3.7.10`
- ✅ **Todas publicadas** no GHCR
- ✅ **Helm atualizado** com tags `3.7.10`

### Variáveis de Ambiente

**OTLP Endpoint:**
```yaml
env:
  - name: OTLP_ENDPOINT
    value: "http://trisla-otel-collector.trisla.svc.cluster.local:4317"
```

**Prometheus Port:**
- Métricas expostas na porta padrão do módulo (`/metrics`)
- Exemplo: `http://trisla-sem-csmf.trisla.svc.cluster.local:8080/metrics`

---

## 📈 Visualização

### Prometheus

**Status de Deploy:**
- ✅ **Prometheus**: Rodando no namespace `monitoring`
- ✅ **ServiceMonitors**: 6 configurados para descoberta automática
- ✅ **Targets**: Configurados via ServiceMonitors

**Acessar:**
```bash
# Port-forward para Prometheus
kubectl port-forward -n monitoring svc/monitoring-kube-prometheus-prometheus 9090:9090

# Acessar: http://localhost:9090
# Targets: http://localhost:9090/targets
```

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
curl http://trisla-sem-csmf.trisla.svc.cluster.local:8080/metrics

# Verificar ServiceMonitor
kubectl get servicemonitors -n trisla

# Verificar targets no Prometheus
kubectl port-forward -n monitoring svc/monitoring-kube-prometheus-prometheus 9090:9090
# Acessar: http://localhost:9090/targets
```

### Traces Não Aparecem

**Verificar:**
```bash
# Verificar logs do módulo
kubectl logs -n trisla deployment/trisla-sem-csmf | grep -i otlp

# Verificar OTEL Collector
kubectl logs -n trisla deployment/trisla-otel-collector

# Verificar conectividade
kubectl exec -n trisla deployment/trisla-sem-csmf -- \
  curl -v http://trisla-otel-collector.trisla.svc.cluster.local:4317
```

### Métricas Customizadas Não Aparecem

**Nota Importante:**
- Métricas customizadas (`trisla_*`, `intent_*`, etc.) só aparecem com **tráfego real de API**
- Gerar requisições POST/GET aos endpoints de negócio
- Não apenas acessar o endpoint `/metrics`

---

## 📊 Status de Deploy (NASP)

### Helm Release

- **Release**: `trisla`
- **Namespace**: `trisla`
- **Revision**: 32
- **Status**: ✅ deployed

### Pods em Execução

- **Total**: 14 pods em Running
  - SEM-CSMF: 2 pods
  - ML-NSMF: 2 pods
  - Decision Engine: 3 pods
  - BC-NSSMF: 2 pods
  - SLA-Agent Layer: 2 pods
  - NASP Adapter: 2 pods
  - UI Dashboard: 1 pod
  - OTEL Collector: 1 pod

### ServiceMonitors

- **Total**: 6 ServiceMonitors configurados
  - `trisla-api-backend`
  - `trisla-bc-nssmf`
  - `trisla-decision-engine`
  - `trisla-ml-nsmf`
  - `trisla-sem-csmf`
  - `trisla-sla-agent-layer`

### OTEL Collector

- **Deployment**: `trisla-otel-collector`
- **Serviço**: `trisla-otel-collector` (ClusterIP, porta 4317)
- **Status**: ✅ Running
- **Versão**: 0.141.0

### Imagens Deployadas

Todas as imagens estão na versão **3.7.10**:
- `ghcr.io/abelisboa/trisla-sem-csmf:3.7.10`
- `ghcr.io/abelisboa/trisla-ml-nsmf:3.7.10`
- `ghcr.io/abelisboa/trisla-decision-engine:3.7.10`
- `ghcr.io/abelisboa/trisla-bc-nssmf:3.7.10`
- `ghcr.io/abelisboa/trisla-sla-agent-layer:3.7.10`
- `ghcr.io/abelisboa/trisla-nasp-adapter:3.7.10`
- `ghcr.io/abelisboa/trisla-ui-dashboard:3.7.10`

---

## 📚 Documentação Adicional

- **Guia de Deploy**: [`docs/deployment/DEPLOY_v3.7.10.md`](deployment/DEPLOY_v3.7.10.md)
- **Changelog**: [`docs/CHANGELOG_v3.7.10.md`](CHANGELOG_v3.7.10.md)
- **Relatório Técnico Final**: [`TRISLA_PROMPTS_v3.5/FASE_6_RELATORIO_TECNICO_FINAL.md`](../../TRISLA_PROMPTS_v3.5/FASE_6_RELATORIO_TECNICO_FINAL.md)

---

## ✅ Validações Realizadas

### Métricas Prometheus
- ✅ **Endpoints /metrics**: Funcionando em todos os módulos
- ✅ **Métricas padrão Python**: Disponíveis
- ✅ **ServiceMonitors**: Configurados e ativos
- ⚠️ **Métricas customizadas**: Requerem tráfego de API real

### Traces OpenTelemetry
- ✅ **OTEL Collector**: Deployado e Running
- ✅ **OTLP_ENDPOINT**: Configurado em todos os pods
- ⚠️ **Traces**: Requerem tráfego de API real para aparecer

### Prometheus
- ✅ **Prometheus**: Rodando no namespace monitoring
- ✅ **ServiceMonitors**: Configurados para descoberta automática
- ⚠️ **Targets**: Requer verificação manual via UI

---

**Status:** ✅ Observability v3.7.10 completa, deployada e operacional

**Última atualização:** 2025-12-05








