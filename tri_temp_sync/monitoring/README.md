# Observabilidade TriSLA

Configuração completa de observabilidade usando OpenTelemetry, Prometheus, Grafana e SLO Reports.

## Componentes

### 1. OpenTelemetry Collector
- Recebe traces, metrics e logs via OTLP
- Exporta para Prometheus, Loki, Tempo
- Configuração: `otel-collector/config.yaml`

### 2. Prometheus
- Coleta métricas de todos os serviços TriSLA
- Alertas baseados em SLO
- Configuração: `prometheus/prometheus.yml`

### 3. Grafana
- Dashboards para visualização
- Integração com Prometheus, Loki, Tempo
- Dashboards: `grafana/dashboards/`

### 4. SLO Reports
- Geração automática de relatórios
- Cálculo de compliance
- Export em JSON/HTML

## Deploy

```bash
kubectl apply -f monitoring/
```

## Dashboards

- TriSLA Overview
- SLO Compliance
- Module Metrics
- Network Metrics

