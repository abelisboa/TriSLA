# TriSLA — Fallback policy (RAN PRB)

**Data:** 2026-05-13  
**Relacionado:** `docs/SSOT_RECOVERY/TRISLA_RAN_SSOT_POLICY.md`

---

## Quando o fallback (simulador) é permitido

- Ensaios **laboratoriais** documentados (carga sintética, stress de UI, demos).
- Quando o operador define explicitamente `TELEMETRY_PROMQL_RAN_PRB` para o job do simulador **e** isso está registado em evidência (não é baseline científico NASP-aligned).
- Quando o SEM-CSMF, após tentar o **proxy authoritative**, não obtém série Prometheus e avança para o segundo item de `SEM_PRB_JOB_PRIORITY` (comportamento já existente — não altera contratos HTTP).

---

## Quando o fallback deve ser ignorado para o paper

- Relatórios científicos, Capítulo IV, e **FASE 13** congelada: usar apenas **trisla-ran-ue-upf-proxy** + **rantester/free5GC**.
- Qualquer métrica publicada como “RAN real” sem menção explícita de que veio do simulador.

---

## Critérios de health (proxy)

- Deployment `trisla-ran-ue-upf-proxy` com réplicas `Ready`.
- `RAN_PROXY_NAMESPACE=ns-1274485`.
- `RAN_PROXY_UE_POD_REGEX` alinhado a pods reais (ex.: `ueransim.*|rantester.*` na spec viva — validar com `kubectl get deploy trisla-ran-ue-upf-proxy -o yaml`).
- Endpoint `/healthz` do exporter na porta de métricas responde (probe Kubernetes).

---

## Critérios de proxy válido (lineage)

- Prometheus expõe série `trisla_ran_prb_utilization{job="trisla-ran-ue-upf-proxy"}` com scrape recente.
- Valores **zero** podem significar ausência de tráfego; não confundir automaticamente com “proxy inválido” sem corroboração (throughput `rantester.*` em `PROMQL_SUMMARY`).

---

## Regras anti-regressão

- Não reintroduzir `avg` sobre `trisla_ran_prb_utilization` sem `job`.
- Não fundir simulador no mesmo PromQL SSOT que o paper.
- Não remover o simulador do cluster (pode permanecer); apenas **desautorizar** como SSOT.

---

## Regras anti-mistura

- **Uma expressão SSOT** por ambiente para o portal: default = job `trisla-ran-ue-upf-proxy`.
- **Throughput / sessões** slice: mantêm-se as queries escopadas `ns-1274485` + `rantester.*` em `PROMQL_SUMMARY` (não misturar com simulador).
