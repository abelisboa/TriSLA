# FASE D.5 — Encadeamento científico real Interpret + Submit no Menu 2

**Data:** 2026-03-16  
**Referência:** `@PROMPTS/CURSOR_PROMPT_DEFINITIVO_FRONTEND_TRISLA.md`  
**Objetivo:** Menu 2 usar em sequência `POST /api/v1/sla/interpret` e `POST /api/v1/sla/submit`, sem alterar backend.

---

## 1. Fluxo (FASE 1)

Ao clicar **Interpretar**:

1. Chamar **POST /api/v1/sla/interpret** com payload atual: `{ intent_text, tenant_id }`.
2. Com os dados retornados, chamar **POST /api/v1/sla/submit** com payload derivado do interpret:
   - `template_id`: valor de `interpret.template_id`
   - `form_values`: `interpret.sla_requirements` enriquecido com `type` / `slice_type` / `service_type` (valor de `interpret.service_type` ou `interpret.slice_type`)
   - `tenant_id`: mesmo do interpret (ex.: `default`)

Nenhuma alteração no backend; somente frontend.

---

## 2. Payload interpret

**Request:** `POST /api/v1/sla/interpret`

```json
{
  "intent_text": "cirurgia remota com latência ultrabaixa",
  "tenant_id": "default"
}
```

**Resposta (exemplo real):** cf. `docs/FASE_D3_PAYLOAD_AUDIT_MENU2.md`

```json
{
  "intent_id": "...",
  "service_type": "URLLC",
  "semantic_class": "Serviço crítico de saúde remota",
  "profile_sla": "Latência ≤ 10 ms | Disponibilidade ≥ 99.999% | Alta confiabilidade",
  "template_id": "urllc-basic",
  "sla_requirements": {
    "latency": "10ms",
    "throughput": null,
    "reliability": 0.99999,
    "jitter": "5ms",
    "coverage": null
  },
  "sla_id": "...",
  "status": "accepted",
  "tenant_id": "default",
  "nest_id": "...",
  "slice_type": "URLLC",
  "message": "SLA interpretado pelo SEM-CSMF com sucesso."
}
```

---

## 3. Payload submit

**Request:** `POST /api/v1/sla/submit` (derivado do interpret)

```json
{
  "template_id": "urllc-basic",
  "form_values": {
    "latency": "10ms",
    "reliability": 0.99999,
    "jitter": "5ms",
    "type": "URLLC",
    "slice_type": "URLLC",
    "service_type": "URLLC"
  },
  "tenant_id": "default"
}
```

**Resposta (exemplo):** schema real do backend `SLASubmitResponse`

- **Campos principais:** decision, reason, justification, intent_id, service_type, sla_requirements, ml_prediction, blockchain_tx_hash, tx_hash, sla_hash, timestamp, status.
- **Auxiliares:** sla_id, nest_id, sem_csmf_status, ml_nsmf_status, bc_status, sla_agent_status, block_number.

---

## 4. Campos usados nos painéis (FASE 2–5)

| Painel | Campos | Origem |
|--------|--------|--------|
| **Semantic Interpretation** | semantic_class, profile_sla, template_id, recommended slice (service_type/slice_type) | interpret |
| **Technical SLA Profile** | latency, throughput, reliability, jitter, coverage (apenas presentes) | interpret.sla_requirements |
| **Explainable AI Reasoning** | confidence, risk_score, risk_level, reason | submit.reason/justification + submit.ml_prediction (confidence, risk_score, risk_level) |
| **Domain Viability** | domain_viability | submit (se presente) |
| **Blockchain Governance** | tx_hash, sla_hash, bc_status | submit |
| **Admission Decision** | decision, status | submit |

- **ml_prediction:** auditado no frontend; extração de `confidence`, `risk_score`, `risk_level` somente quando presentes (dados reais).
- Campos ausentes não são renderizados (nunca mostrar null).

---

## 5. Technical Response Payload (FASE 6)

O JSON expandível exibe dois blocos separados:

- **interpret:** payload completo da resposta de `POST /api/v1/sla/interpret`.
- **submit:** payload completo da resposta de `POST /api/v1/sla/submit` (ou `{}` se submit não tiver sido chamado).

---

## 6. Build, push, deploy, validação (FASE 8–12)

- Build: `podman build --format docker -t ghcr.io/abelisboa/trisla-portal-frontend:${TS} -f apps/portal-frontend/Dockerfile apps/portal-frontend`
- Push: `podman push ghcr.io/abelisboa/trisla-portal-frontend:${TS}`
- Digest: `skopeo inspect ... docker://ghcr.io/abelisboa/trisla-portal-frontend:${TS} | jq -r .Digest`
- Deploy: `helm upgrade trisla-portal helm/trisla-portal -n trisla --set frontend.image.repository=... --set frontend.image.digest=${REMOTE_DIGEST} --set frontend.image.tag="" --reuse-values`
- Validar: rollout status, deployment image, pod imageID.

---

## 7. Regra final

- Nenhuma alteração no backend.
- Somente frontend e somente payload real.
