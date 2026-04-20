# Regras de alerta V2 — rascunho (PR-06 / FASE 6)

**Estado:** proposta documental — **não aplicado** ainda no Prometheus / Alertmanager.  
Objetivo: base canônica para ativação futura sem cutover de política nesta fase.

Parâmetros simbólicos (`$WINDOW`, `$N`) devem ser calibrados por ambiente.

---

## ALERT 1 — Completude de telemetria abaixo do alvo

- **Condição:** `telemetry_complete_ratio` (ou fração de submits com `metadata.telemetry_complete == true`) **&lt; 0.95** numa janela de execução (`$WINDOW`).
- **Fonte:** agregação sobre logs/respostas do submit ou métricas derivadas do runner.
- **Severidade sugerida:** warning.

---

## ALERT 2 — Gaps persistentes

- **Condição:** `metadata.telemetry_gaps` **não vazio** por mais de **`N`** execuções consecutivas (ou &gt; **N** em `$WINDOW`).
- **Fonte:** submit JSON / CSV E2E.
- **Severidade sugerida:** warning → critical se domínio crítico (ex.: RAN em cenário URLLC).

---

## ALERT 3 — Fallback de política SLA em excesso

- **Condição:** `metadata.sla_policy_version == "v2_fallback_v1"` com frequência acima do esperado (ex.: &gt; **X%** dos submits em `$WINDOW`).
- **Fonte:** metadata do submit.
- **Severidade sugerida:** warning (indica degradação ou indisponibilidade do caminho V2).

---

## ALERT 4 — Jitter de transporte ausente

- **Condição:** `transport.jitter` / `transport.jitter_ms` ausente no snapshot (gap `transport.jitter` em `telemetry_gaps` ou valor nulo).
- **Fonte:** `metadata.telemetry_snapshot` + `telemetry_gaps`.
- **Severidade sugerida:** warning.

---

## ALERT 5 — PRB RAN ausente

- **Condição:** `ran.prb_utilization` ausente (gap `ran.prb_utilization`).
- **Fonte:** snapshot + gaps.
- **Severidade sugerida:** warning.

---

## ALERT 6 — Taxa HTTP 200 no runner controlado

- **Condição:** `http_200 / total_requests < 1.0` no runner controlado (`prompt21_multi_domain_validation.py` ou equivalente).
- **Fonte:** `summary.json`.
- **Severidade sugerida:** critical para gate de release.

---

## Implementação futura (checklist)

1. Exportar contadores/gauges a partir do backend ou do runner para Prometheus (recording rules).
2. Mapear cada alerta a um `runbook` (ação: verificar NASP, RAN exporter, Core scrape).
3. Revisar com a equipa o **N** e **$WINDOW** após baseline em produção.
