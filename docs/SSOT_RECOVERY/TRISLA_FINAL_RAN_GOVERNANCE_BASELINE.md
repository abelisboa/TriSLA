# TriSLA — final RAN governance baseline

**Data:** 2026-05-13  
**Evidências:** `evidencias_ssot_ran_governance_20260513T204501Z/` (snapshot Fase 0), `evidencias_nasp_alignment/` (fases 1–4a).

---

## Authoritative telemetry source

- **Job:** `trisla-ran-ue-upf-proxy`
- **Backing:** my5G-RANTester + free5GC + Prometheus
- **PromQL (portal + revalidate):** `avg(trisla_ran_prb_utilization{job="trisla-ran-ue-upf-proxy"})`
- **Instant (summary index):** `trisla_ran_prb_utilization{job="trisla-ran-ue-upf-proxy"}`

## Fallback policy

- **Job:** `trisla-prb-simulator` — apenas laboratório; nunca SSOT do paper; ver `docs/SSOT_RECOVERY/TRISLA_FALLBACK_POLICY.md`.

## NASP alignment

- RAN: **rantester**; Core: **free5GC**; Transport: **ONOS** (+ Mininet quando saudável); Observability: **Prometheus**; Governance: **Besu + BC-NSSMF**; Assurance: **SLA-Agent** — ver `docs/TRISLA_E2E_FLOW_CANONICAL.md`.

## Runtime lineage

- PRB: proxy → (opcional) simulador via `SEM_PRB_JOB_PRIORITY` no SEM-CSMF; portal/revalidate já **não** usam média global sem `job`.

## Observability governance

- Proibido usar `avg` sobre `trisla_ran_prb_utilization` **sem** seletor `job` em `apps/`, `docs/`, `scripts/`, `helm/` (validação grep).
- Overrides: `TELEMETRY_PROMQL_RAN_PRB`, `RAN_I1_PRB_QUERY`, `SEM_PRB_JOB_PRIORITY` — documentados no runbook.

## Anti-regression rules

- Digest-only GHCR; SSH via `node006`.
- Não alterar endpoints `POST /api/v1/sla/submit` nem `POST /api/v1/sla/revalidate-telemetry`.
- Não alterar semantics do Decision Engine, BC-NSSMF, SLA-Agent.

## Official PromQL (RAN PRB)

- `avg(trisla_ran_prb_utilization{job="trisla-ran-ue-upf-proxy"})`

## Official workflow

- Inalterado: `docs/TRISLA_E2E_FLOW_CANONICAL.md`.

## Official SSOT documents

- `docs/SSOT_RECOVERY/TRISLA_RAN_SSOT_POLICY.md`
- `docs/SSOT_RECOVERY/TRISLA_NASP_RUNTIME_BASELINE.md`
- `docs/SSOT_RECOVERY/TRISLA_FINAL_FROZEN_BASELINE.md`

## Fase 5–6

- **Build/deploy:** apenas se imagem mudar (digest GHCR) — não executado neste commit de código/docs.
- **E2E:** executar smoke `submit` + verificar `telemetry_snapshot`, `tx_hash`, `block_number`, revalidate, após rollout portal-backend.
