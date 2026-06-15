# TriSLA — RAN telemetry SSOT policy (governance)

**Data:** 2026-05-13  
**Precedência:** complementa `docs/SSOT_RECOVERY/TRISLA_NASP_RUNTIME_BASELINE.md` e `docs/SSOT_RECOVERY/TRISLA_FINAL_FROZEN_BASELINE.md`.  
**NASP alignment:** baseline científico segue o modelo publicado no repositório (runbook + E2E canónico + runtime).

---

## AUTHORITATIVE (fonte oficial)

| Campo | Valor |
|--------|--------|
| **Source (job Prometheus)** | `trisla-ran-ue-upf-proxy` |
| **Backing** | **my5G-RANTester** (`rantester` em `ns-1274485`) + **free5GC** (UPF/AMF/SMF no mesmo namespace) + **Prometheus** (scrape) |
| **Role** | **official RAN telemetry SSOT** para `telemetry_snapshot.ran.prb_utilization` quando não houver override explícito por env |
| **PromQL canónico (código)** | `avg(trisla_ran_prb_utilization{job="trisla-ran-ue-upf-proxy"})` em `apps/portal-backend/src/telemetry/promql_ssot.py` e `apps/sla-agent-layer/src/revalidate/promql_ssot.py` |
| **Instant summary (observability index)** | `trisla_ran_prb_utilization{job="trisla-ran-ue-upf-proxy"}` — `PROMQL_SUMMARY["ran_prb_instant"]` |

O proxy observa tráfego derivado de pods UE/UPF conforme `RAN_PROXY_*` no Deployment `trisla-ran-ue-upf-proxy`.

---

## FALLBACK (laboratório)

| Campo | Valor |
|--------|--------|
| **Source** | `trisla-prb-simulator` |
| **Role** | **laboratory fallback only** |
| **Restrictions** | **not authoritative**; **not paper SSOT**; **must not** ser misturado na mesma agregação que o authoritative; não promover a SSOT científico |

Consulta laboratorial opcional (fora do SSOT portal): `avg(trisla_ran_prb_utilization{job="trisla-prb-simulator"})` apenas para ensaios controlados documentados.

---

## LABORATORY (experimental)

| Componentes | Papel |
|---------------|--------|
| **UERANSIM**, **srsRAN**, **NONRTRIC** | laboratório / experimental only — não substituem o authoritative sem decisão de baseline explícita |

---

## PROHIBITED (proibido)

1. **`avg` sem filtro de `job` sobre `trisla_ran_prb_utilization`** — mistura implícita proxy + simulador (anti-pattern científico).
2. **Mistura implícita** de lineage authoritative + fallback na mesma expressão PromQL usada como SSOT.
3. **Simulador como SSOT** do paper ou da decisão NASP-aligned.
4. **Promover fallback** para substituir o proxy quando o proxy está configurado e saudável.

---

## Anti-regressão (resumo)

- Qualquer alteração a `PROMQL_SSOT` / `TELEMETRY_PROMQL_RAN_PRB` exige evidência Prometheus + submit smoke.
- Manter `SEM_PRB_JOB_PRIORITY` coerente: proxy (authoritative) antes do simulador (fallback) — `apps/sem-csmf/src/decision_engine_client.py`.
- Deploy: apenas **GHCR + digest** (sem `:latest`).

Ver também: `docs/SSOT_RECOVERY/TRISLA_FALLBACK_POLICY.md`.
