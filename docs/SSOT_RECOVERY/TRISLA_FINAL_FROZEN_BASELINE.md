# TriSLA — baseline final congelado (NASP alignment pack)

**Data:** 2026-05-13  
**Escopo:** consolidação **documental** pós Fases 0–3; **sem** execução Fase 4–5 neste ciclo.

## Arquitetura final congelada

- Mesma que `docs/SSOT_RECOVERY/TRISLA_NASP_RUNTIME_BASELINE.md` e precedência `docs/TRISLA_E2E_FLOW_CANONICAL.md` (2026-05-11).
- **RAN baseline operacional:** my5G-RANTester (`rantester-0`, `ns-1274485`) + **free5GC** no mesmo namespace.
- **Transporte alvo:** ONOS (Running no snapshot) + Mininet (BROKEN no snapshot — limitação registada).
- **Observabilidade:** Prometheus kube-prometheus em `monitoring`.
- **Governance:** BC-NSSMF + Besu (`trisla`).

## Componentes oficiais vs laboratoriais

| Oficial (NASP-aligned) | Laboratório |
|-------------------------|---------------|
| rantester + free5GC | UERANSIM, srsRAN, NONRTRIC |
| ONOS (target) | Mininet (erro no snapshot) |
| Prometheus | Grafana auxiliar `ran-test` |
| trisla-* control plane | `trisla-prb-simulator` |

## PromQL oficial (congelamento recomendado)

- **Portal default (código):** `avg(trisla_ran_prb_utilization{job="trisla-ran-ue-upf-proxy"})` — SSOT authoritative; override via `TELEMETRY_PROMQL_RAN_PRB` apenas com evidência.
- **Throughput slice:** `PROMQL_SUMMARY["throughput_mbps"]` com `rantester.*` em `ns-1274485`.

## Workflow e sequência

- `docs/TRISLA_E2E_FLOW_CANONICAL.md` — não alterada neste pack.

## Interfaces oficiais

- `docs/TRISLA_ARCHITECTURE_EVIDENCE_PATCHED.md` §1.

## Runtime validado (snapshot)

- `evidencias_nasp_alignment/fase1_runtime/pods.txt` e `runtime_classification.md`.

## Evidências associadas

- `evidencias_nasp_alignment/fase2_prb/prb_lineage.md`, `full_reference.txt`.
- `evidencias_nasp_alignment/fase3_plan/recovery_plan.md`.

## Limitações

- Mininet DOWN; UERANSIM endpoint auxiliar em erro; PRB multi-fonte — ver baseline SSOT §20.

## Regras anti-regressão

- Ver `TRISLA_NASP_RUNTIME_BASELINE.md` §10.
- **Fase 4–5:** executar apenas após gate em `recovery_plan.md` e registo em `evidencias_nasp_alignment/PHASE4_5_GATE.md`.
