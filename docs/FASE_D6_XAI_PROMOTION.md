# FASE D.6 — Promoção total do submit real para painéis científicos principais

**Data:** 2026-03-17  
**Referência:** `@PROMPTS/CURSOR_PROMPT_DEFINITIVO_FRONTEND_TRISLA.md`  
**Objetivo:** Promover dados reais já presentes em submit/ml_prediction para a UI principal do Menu 2. Sem alterar backend.

---

## 1. Explainable AI Reasoning (FASE 1)

- **Fonte:** `submit.ml_prediction`
- **Mapeamento:**
  - `confidence` → **Confidence**
  - `ml_risk_score` → **Risk Score**
  - `ml_risk_level` → **Risk Level**
  - `reasoning` (ou `reason`) → **Reason** (fallback: `submit.reason` / `submit.justification`)
- O painel é renderizado sempre que existir pelo menos um desses campos (dados reais).

---

## 2. Admission Decision (FASE 2)

- **Fonte:** submit raiz
- **Campos:** `decision`, `status`
- **Painel:** Admission Decision

---

## 3. Blockchain Governance (FASE 3)

- **Fonte:** submit raiz
- **Campos:** `tx_hash`, `sla_hash`, `bc_status`
- **Painel:** Blockchain Governance

---

## 4. Domain Viability (FASE 4)

- **Renderizar** somente se existir:
  - `domain_viability` (submit raiz ou ml_prediction), ou
  - `viability_score` (submit raiz ou ml_prediction)
- Se não existir: painel não é renderizado.

---

## 5. Technical SLA Profile (FASE 5)

- **Formatação:**
  - `reliability`: valor numérico 0–1 → ex.: `0.99999` → **99.999%**
  - `latency`: ex.: **10ms**
  - `jitter`: ex.: **5ms**
  - `throughput`, `coverage`: exibidos como recebidos (dados reais).

---

## 6. Ordem final dos painéis (FASE 6)

1. Semantic Interpretation  
2. Technical SLA Profile  
3. Explainable AI Reasoning  
4. Admission Decision  
5. Blockchain Governance  
6. Domain Viability (se existir)  
7. Technical Response Payload  

---

## 7. JSON técnico (FASE 7)

- Mantido expandível (interpret + submit em blocos separados).

---

## 8. Regra final

- Nenhuma alteração no backend.  
- Somente frontend e somente dados reais.
