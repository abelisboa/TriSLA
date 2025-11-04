# 📘 Apêndice E — Diretrizes de Observabilidade e SLOs

Plano unificado baseado em OpenTelemetry e Prometheus.

Métricas OTLP publicadas com labels interface e domain.

Exemplo PromQL:

```promql
histogram_quantile(0.99, sum(rate(trisla_request_duration_bucket[5m])) by (le, interface))
```

Closed-loop ativo via webhook (Alertmanager → Decision Engine).

