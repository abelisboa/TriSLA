# Prompts & audit drivers — index (no duplication)

There is **no** top-level `PROMPTS/` directory in this repository. Operational “prompt” style material lives under **`docs/`** and **`backup/prompts/`** (the latter is a **frozen mirror** of `docs/` from backup; prefer **`docs/`** when both exist for the same relative name).

## Restoration / governance (meta)

| Document | Role |
|----------|------|
| [../OPERATING_RULES.md](../OPERATING_RULES.md) | Governance v2 — no silent changes |
| [../AUDIT_REPORT_V2.md](../AUDIT_REPORT_V2.md) | Read-only audit summary (pipeline + telemetry) |

## Validation / E2E / RAN

| Document | Role |
|----------|------|
| [../../VALIDACAO_FINAL_E2E_RAN_REAL.md](../../VALIDACAO_FINAL_E2E_RAN_REAL.md) | RAN E2E validation evidence |
| [../../VALIDACAO_TECNICA_XAI_SUBMIT.md](../../VALIDACAO_TECNICA_XAI_SUBMIT.md) | XAI submit technical validation |
| [../../TRISLA_DIRETRIZES_RAN_E2E.md](../../TRISLA_DIRETRIZES_RAN_E2E.md) | RAN E2E directives |
| [../../ACCEPTANCE_CRITERIA_TELEMETRY_V2.md](../../ACCEPTANCE_CRITERIA_TELEMETRY_V2.md) | Telemetry v2 acceptance |

## Audit series (representative `docs/AUDITORIA_*.md`)

Use `ls docs/AUDITORIA_*.md` for the full set. High-signal entries for **RAN / telemetry / NASP**:

- `docs/AUDITORIA_PROMPT05_RAN_PRB_PIPELINE.md`
- `docs/AUDITORIA_PROMPT06_1_RAN_PRB_OPERACIONAL.md`
- `docs/AUDITORIA_PROMPT09_SRSENB_FIX.md`
- `docs/AUDITORIA_PROMPT10_TELEMETRIA_RAN.md`
- `docs/AUDITORIA_PROMPT11_TELEMETRIA_ATIVADA.md`
- `docs/AUDITORIA_PROMPT12_EXPORTER_RAN.md`
- `docs/AUDITORIA_PROMPT13_FONTE_PRB_SRSENB.md`
- `docs/AUDITORIA_PROMPT14_SRSRAN_STANDALONE.md`
- `docs/AUDITORIA_PROMPT14_1_NASP_RAN_ALIGNMENT.md`
- `docs/AUDITORIA_PROMPT15_SSOT_RAN_NASP.md`
- `docs/AUDITORIA_PROMPT15_1_NASP_FULL_STACK.md`
- `docs/AUDITORIA_PROMPT16_RAN_LOAD_TELEMETRY.md`
- `docs/AUDITORIA_PROMPT16_1_RAN_LOAD_STABILITY.md`

## Named PROMPT files (only under `backup/prompts/` today)

| File | Role |
|------|------|
| [../../../backup/prompts/PROMPT_33_AUDITORIA_ALINHAMENTO_METRICAS_3_DOMINIOS_NASP_V1.md](../../../backup/prompts/PROMPT_33_AUDITORIA_ALINHAMENTO_METRICAS_3_DOMINIOS_NASP_V1.md) | 3-domain NASP metrics audit |
| [../../../backup/prompts/PROMPT_34_PLANO_REALINHAMENTO_DOMINIOS_RAN_TRANSPORT_CORE_V1.md](../../../backup/prompts/PROMPT_34_PLANO_REALINHAMENTO_DOMINIOS_RAN_TRANSPORT_CORE_V1.md) | RAN/transport/core realignment plan |
| [../../../backup/prompts/PROMPT_35_CHECKLIST_PRs.md](../../../backup/prompts/PROMPT_35_CHECKLIST_PRs.md) | PR checklist |

## Collection / campaigns

| Document | Role |
|----------|------|
| [../../TRISLA_FINAL_EVIDENCE_CAMPAIGN.md](../../TRISLA_FINAL_EVIDENCE_CAMPAIGN.md) | Evidence campaign |
| [../../CURSOR_WORKFLOW_RULES.md](../../CURSOR_WORKFLOW_RULES.md) | Cursor / agent workflow rules |

**Count:** 3 exclusive `PROMPT_*.md` under `backup/prompts/` + 4 validation docs + 13 listed audits + 2 campaign/workflow = **22 explicit index rows** (full `AUDITORIA_*` count in `docs/` is higher; use `ls`).
