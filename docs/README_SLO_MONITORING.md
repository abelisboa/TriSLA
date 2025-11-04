# 📊 TriSLA — SLO & Observabilidade (v3.3.0)

Este documento complementa o Apêndice E da dissertação e descreve a implementação operacional dos SLOs e da observabilidade.

## 🔹 Componentes Ativos
- Prometheus + Grafana integrados (namespace: monitoring)
- OpenTelemetry Collector ativo (OTLP → Prometheus)
- Alertmanager → Decision Engine Webhook (Closed-Loop Assurance)
- Métricas exportadas com labels [interface, domain]
- Adaptador NWDAF simulando análises 3GPP
- Matriz de rastreabilidade gerada automaticamente

## 🔹 Regras SLO Declarativas
Local: `monitoring/prometheus-rules/trisla-slo.yaml`

Cada interface I-* é monitorada quanto a:
- Latência p99 (histogram_quantile)
- Taxa de erro por requisições 5xx
- Disponibilidade (via uptime series)

## 🔹 Closed-Loop Assurance
Alertas do Prometheus acionam automaticamente o Decision Engine via Webhook.

```text
Alertmanager --> Decision Engine --> Reconfiguração Agente --> Métrica Atualizada
```

## 🔹 Rastreamento e Logs
Logs OTLP armazenados em `/data/logs/`, com formato JSON:
```json
{
 "timestamp": "...",
 "traceId": "...",
 "module": "bc-nssmf",
 "metric": {"latencyMs": 176},
 "decision": "ACCEPT",
 "slo": "latency_p99",
 "explanation": "Latência dentro do limite"
}
```

