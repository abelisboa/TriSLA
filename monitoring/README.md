# Observabilidade TriSLA

Configuração completa de observabilidade usando OpenTelemetry, Prometheus, Grafana e SLO Reports.

## Componentes

### 1. OpenTelemetry Collector
- Recebe traces, metrics e logs via OTLP
- Exporta para Prometheus, Loki, Jaeger
- Configuração: `otel-collector/config.yaml`

**Exporters:**
- **Prometheus**: Métricas (porta 8889)
- **Jaeger**: Traces distribuídos (porta 14250)
- **Loki**: Logs estruturados (porta 3100)

### 2. Prometheus
- Coleta métricas de todos os serviços TriSLA
- Alertas baseados em SLO por interface
- Configuração: `prometheus/prometheus.yml`

**Alertas:**
- SLO por interface (I-01 a I-07)
- Latência, throughput, error rate
- Compliance geral

### 3. Grafana
- Dashboards para visualização
- Integração com Prometheus, Loki, Jaeger
- Dashboards: `grafana/dashboards/`

**Dashboards:**
- **TriSLA Overview**: Visão geral do sistema
- **SLO Compliance por Interface**: SLOs por interface (I-01 a I-07)
- **Module Metrics**: Métricas por módulo
- **Distributed Traces**: Traces distribuídos

### 4. SLO Reports
- Geração automática de relatórios
- Cálculo de compliance por interface
- Export em JSON/HTML

## Métricas por Interface

### I-01: SEM-CSMF → Decision Engine
- `trisla_i01_requests_total`: Total de requisições
- `trisla_i01_request_duration_seconds`: Duração de requisições
- `trisla_i01_errors_total`: Total de erros

**SLO Targets:**
- Latência p99: 100ms
- Throughput: 100 req/s
- Error rate: 1%
- Disponibilidade: 99%

### I-02: ML-NSMF → Decision Engine
- `trisla_i02_messages_total`: Total de mensagens
- `trisla_i02_message_duration_seconds`: Duração de mensagens
- `trisla_i02_errors_total`: Total de erros

**SLO Targets:**
- Latência p99: 200ms
- Throughput: 50 msg/s
- Error rate: 1%
- Disponibilidade: 99%

### I-03: Decision Engine → ML-NSMF
- `trisla_i03_messages_total`: Total de mensagens
- `trisla_i03_message_duration_seconds`: Duração de mensagens
- `trisla_i03_errors_total`: Total de erros

**SLO Targets:**
- Latência p99: 200ms
- Throughput: 50 msg/s
- Error rate: 1%
- Disponibilidade: 99%

### I-04: Decision Engine → BC-NSSMF
- `trisla_i04_requests_total`: Total de requisições
- `trisla_i04_request_duration_seconds`: Duração de requisições
- `trisla_i04_errors_total`: Total de erros

**SLO Targets:**
- Latência p99: 500ms (blockchain)
- Throughput: 10 req/s
- Error rate: 5%
- Disponibilidade: 95%

### I-05: Decision Engine → SLA-Agent Layer
- `trisla_i05_messages_total`: Total de mensagens
- `trisla_i05_message_duration_seconds`: Duração de mensagens
- `trisla_i05_errors_total`: Total de erros

**SLO Targets:**
- Latência p99: 200ms
- Throughput: 50 msg/s
- Error rate: 1%
- Disponibilidade: 99%

### I-06: SLA-Agent Layer → Decision Engine
- `trisla_i06_events_total`: Total de eventos
- `trisla_i06_event_duration_seconds`: Duração de eventos
- `trisla_i06_errors_total`: Total de erros

**SLO Targets:**
- Latência p99: 200ms
- Throughput: 50 msg/s
- Error rate: 1%
- Disponibilidade: 99%

### I-07: NASP Adapter
- `trisla_i07_requests_total`: Total de requisições
- `trisla_i07_request_duration_seconds`: Duração de requisições
- `trisla_i07_errors_total`: Total de erros

**SLO Targets:**
- Latência p99: 1000ms
- Throughput: 20 req/s
- Error rate: 5%
- Disponibilidade: 95%

## Métricas Gerais

- `trisla_intents_total`: Total de intents processados
- `trisla_nests_generated_total`: Total de NESTs gerados
- `trisla_predictions_total`: Total de predições ML
- `trisla_decisions_total`: Total de decisões
- `trisla_blockchain_transactions_total`: Total de transações blockchain
- `trisla_actions_executed_total`: Total de ações executadas
- `trisla_slo_compliance_rate`: Taxa de compliance com SLO
- `trisla_slo_violations_total`: Total de violações de SLO

## Traces Distribuídos

O TriSLA suporta traces distribuídos com propagação de contexto:

- **Context Propagation**: Propagação de contexto entre módulos
- **Trace Correlation**: Correlação de traces entre interfaces
- **Jaeger Integration**: Visualização de traces no Jaeger

## Deploy

```bash
kubectl apply -f monitoring/
```

## Configuração

### Variáveis de Ambiente

- `OTLP_ENABLED`: Habilitar OTLP (padrão: false)
- `OTLP_ENDPOINT_GRPC`: Endpoint OTLP gRPC (padrão: http://otlp-collector:4317)
- `OTLP_ENDPOINT_HTTP`: Endpoint OTLP HTTP (padrão: http://otlp-collector:4318)

## Versão

v3.7.7 (FASE O)
