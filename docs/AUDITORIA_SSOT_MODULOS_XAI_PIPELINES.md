# Auditoria SSOT — Módulos, XAI, Pipelines (node006)

**Data:** 2026-03-18  
**Regra:** SSOT obrigatório; nenhuma alteração sem alinhar com PROMPT MESTRE, MATRIZ TÉCNICA, Evolução.

---

## Documentos consultados

1. PROMPT MESTRE CURSOR — TRI SLA FRONTEND SCIENTIFIC REBUILD (SSOT OFICIAL)
2. MATRIZ TÉCNICA OFICIAL — Portal TriSLA Científico SLA-Centric
3. Evolução do Portal TriSLA para Portal Científico SLA-Centric

---

## FASE 0 — Auditoria total dos módulos

| Módulo | Backend | Endpoints / origem |
|--------|---------|--------------------|
| **SEM** | apps/sem-csmf | POST /api/v1/interpret → intent_id, nest_id, sla_requirements, message. Portal proxy: POST /api/v1/sla/interpret |
| **ML** | apps/ml-nsmf | Predictor: viability_score, risk_score, risk_level, confidence; explain(): features_importance, reasoning. Portal não agrega ML direto; submit passa pelo NASP. |
| **XAI** | portal-backend src/services/xai.py, src/schemas/xai.py | GET ML-NSMF /api/v1/predictions/{id} e Decision /api/v1/decisions/{id}. XAIExplanation: viability_score, features_importance, reasoning. Router: src/routers/xai.py |
| **Admission** | decision-engine | decision (ACCEPT/REJECT), reasoning, confidence, ml_risk_level. Portal: result.get("decision") em routers/sla.py submit. |
| **Lifecycle** | Não consolidado | MATRIZ: admission=Decision Engine, blockchain=BC-NSSMF, runtime=NASP Adapter. Backend atual não expõe agregador "SLA lifecycle" por SLA; /api/v1/sla/status/{sla_id} e /api/v1/sla/metrics/{sla_id} dependem de nasp_service.get_sla_status e call_metrics (nasp.py atual só tem probes). |
| **Blockchain** | bc-nssmf | apps/bc-nssmf/src/main.py: tx_hash, block_number no response. Portal: result.get("blockchain_tx_hash"), result.get("tx_hash"), result.get("bc_status"), result.get("block_number") em submit (via NASP backup). |
| **Monitoring** | portal-backend | GET /api/v1/health/global, GET /nasp/diagnostics, GET /api/v1/prometheus/summary (prometheus router). |
| **Metrics** | portal-backend | GET /metrics (Prometheus scrape). GET /api/v1/sla/metrics/{sla_id} → nasp_service.call_metrics (nasp atual sem implementação). GET /api/v1/modules/{module}/metrics → ModuleService.get_module_metrics (Prometheus). |
| **Modules** | portal-backend | GET /api/v1/modules/ (list), GET /api/v1/modules/{module}, GET /api/v1/modules/{module}/metrics, GET /api/v1/modules/{module}/status. services/modules.py: list_modules estático; get_module usa Prometheus up{job=module}; get_module_status retorna estrutura fixa (pods/deployments). |

---

## FASE 1 — XAI real (origem backend)

| Campo | Arquivo exato que gera |
|-------|------------------------|
| **confidence** | apps/ml-nsmf/src/predictor.py (predict): `confidence = 1.0 - abs(viability_score - 0.5) * 2`; decision-engine usa ml_prediction.confidence (apps/decision-engine/src/models.py, service.py, decision_snapshot.py). |
| **risk_level** | apps/ml-nsmf/src/predictor.py: `risk_level = "high"|"medium"|"low"` por risk_score. decision-engine: ml_risk_level (RiskLevel). |
| **score** | ML: viability_score e risk_score em apps/ml-nsmf/src/predictor.py. Decision: ml_risk_score no DecisionResult (engine.py). |
| **principal factor** | ML explain(): features_importance (SHAP/LIME) em predictor.py; reasoning string. Não existe campo literal "principal_factor" no backend; o mais próximo é features_importance (dict) e reasoning. |
| **feature attribution** | apps/ml-nsmf/src/predictor.py explain(): explanation["features_importance"] (SHAP/LIME). Portal XAI: xai.py chama ML predictions e decision; schemas/xai.py: features_importance, reasoning. |

**Resumo:** XAI real vem de ML-NSMF (predictor.py predict+explain) e Decision Engine (reasoning, confidence, ml_risk_level). Portal-backend xai.py agrega de ML e Decision; não inventar score/confidence no frontend.

---

## FASE 2 — Decision pipeline (origem real)

| Campo | Origem real |
|-------|-------------|
| **decision** | decision-engine: DecisionResult.action (ACCEPT/REJECT). Portal: routers/sla.py submit → result.get("decision"). decision_snapshot.py: snapshot["decision"] = decision_result.action.value. |
| **viability_score** | ML-NSMF predictor.predict() → prediction["viability_score"]. decision-engine ml_client recebe e usa; DecisionResult não guarda viability_score como campo top-level; está em ml_prediction. Portal SLASubmitResponse: ml_prediction (dict) pode conter viability_score se NASP repassar. |
| **domain viability** | decision-engine decision_snapshot.py: domains_snapshot (RAN, Transport, Core) com métricas e status "evaluated". Não existe campo único "domain_viability" na API do portal; está dentro do snapshot/evidência do Decision Engine. |

---

## FASE 3 — Blockchain pipeline (origem real)

| Campo | Origem real |
|-------|-------------|
| **tx_hash** | apps/bc-nssmf/src/main.py: receipt.transactionHash.hex() em register e update; retorno "tx_hash". Portal: result.get("blockchain_tx_hash") or result.get("tx_hash") (schemas/sla.py SLASubmitResponse). Backup nasp: blockchain_result.get("tx_hash"). |
| **block** | bc-nssmf: receipt.blockNumber. Portal: block_number (SLASubmitResponse). |
| **bc_status** | Portal schemas/sla.py: bc_status (CONFIRMED | PENDING | ERROR). Backup nasp: blockchain_status = "CONFIRMED" if data.get("status") == "ok" else "PENDING". |

---

## FASE 4 — Lifecycle pipeline (origem real)

| Campo | Origem real |
|-------|-------------|
| **runtime** | MATRIZ: NASP Adapter. Backend atual não expõe endpoint único "runtime" por SLA; /api/v1/sla/status/{sla_id} e /api/v1/sla/metrics/{sla_id} seriam a fonte (implementação em nasp backup: get_sla_status, call_metrics). |
| **admission** | Decision Engine: decision (ACCEPT/REJECT). Presente em POST /api/v1/sla/submit → decision. |
| **blockchain state** | bc_status, tx_hash, block_number no response do submit (e no backup nasp register_in_blockchain). |

**Gap:** Não existe agregador "SLA lifecycle" por SLA (tabela SLA ID | Slice Type | Estado | Admission | Blockchain | NASP | Runtime) no backend atual; seria necessário agregar SEM + ML + BC + NASP states (conforme MATRIZ).

---

## FASE 5 — Comparar com frontend antigo

- Screenshots antigas: usar como referência científica; nada inventado.
- Frontend atual (portal-frontend src/app): PNL, Template, Monitoring, Metrics, Defense, Administration, sla-lifecycle.
- Regra: reexpor somente o que o backend ainda produz (ver FASE 1–4). Se um campo antigo não existir mais no backend, não exibir como real; documentar "origem perdida" ou "não exposto pela API atual".

---

## FASE 6 — PNL e Template (campos reais)

- **PNL (interpret):** intent_id, nest_id, sla_id, service_type, slice_type, status, created_at, message, technical_parameters, sla_requirements (todos com origem em routers/sla.py + SEM). Sem score/confidence fake.
- **Template (submit):** decision, reason, justification, sla_id, intent_id, nest_id, service_type, timestamp, sla_requirements, ml_prediction, blockchain_tx_hash, tx_hash, sla_hash, status, sem_csmf_status, ml_nsmf_status, bc_status, sla_agent_status, block_number (schemas/sla.py SLASubmitResponse). Renderizar apenas estes; se ml_prediction contiver viability_score/confidence/risk_level (quando NASP repassar), exibir como "dados do pipeline".
- **Campos antigos sem origem atual:** Se no frontend antigo existiam "principal_factor" ou "domain_viability" como campo único, hoje só existem via features_importance/reasoning e domains_snapshot no Decision Engine; documentar como "não expostos na API do portal" ou "disponíveis apenas via XAI/decision internos".

---

## Gaps documentados

| Gap | Descrição |
|-----|-----------|
| **NASP atual** | src/services/nasp.py só tem check_sem_csmf, check_bc_nssmf. call_sem_csmf, submit_template_to_nasp, get_sla_status, call_metrics existem em src_backup_20251208_081013/services/nasp.py. /submit, /status, /metrics dependem desses métodos. |
| **Lifecycle agregado** | Backend não expõe tabela SLA lifecycle (Admission, Blockchain, NASP, Runtime por SLA); MATRIZ indica necessidade de agregador. |
| **XAI no submit** | SLASubmitResponse tem ml_prediction (dict); pode conter viability_score, confidence, risk_level se o pipeline NASP repassar; frontend pode exibir sem inventar. |
| **Modules status** | get_module_status retorna estrutura fixa (pods/deployments); em produção poderia consultar Kubernetes API. |

---

## FASE 7 — Build absoluto (executado no node006)

Comandos executados em **node006**:

```bash
cd /home/porvir5g/gtp5g/trisla/apps/portal-frontend
rm -rf .next
npm run build
grep -r "pnl\|template\|api" .next/static 2>/dev/null | head -20
```

**Resultado:** Build concluído com sucesso. Rotas: /, /administration, /defense, /metrics, /monitoring, /pnl, /sla-lifecycle, /template, /api/v1/[...path].

---

## FASE 8 — Deploy absoluto (node006)

Docker build executado no **node006**:

```bash
cd /home/porvir5g/gtp5g/trisla/apps/portal-frontend
docker build --no-cache -t trisla-portal-frontend:latest .
```

**Image ID (node006):** `ecf92779667f`  
**Digest (node006):** `sha256:35c1a9a4a86a3cd052f8b553359e4d3b08422bf08cd66eadbcb92365c2898044`

Push e rollout (executar no ambiente com registry e kubectl configurados):

```bash
docker tag trisla-portal-frontend:latest $REGISTRY/trisla-portal-frontend:latest
docker push $REGISTRY/trisla-portal-frontend:latest
kubectl rollout restart deployment/trisla-portal-frontend -n <namespace>
kubectl rollout status deployment/trisla-portal-frontend -n <namespace>
```

---

## FASE 9 — Validar pod

Após o rollout:

```bash
kubectl get pods -n <namespace> -l app.kubernetes.io/name=portal-frontend -o jsonpath='{.items[0].status.containerStatuses[0].imageID}'
```

**REMOTE_DIGEST** deve coincidir com o imageID do pod (ex.: `sha256:35c1a9a4a86a3cd052f8b553359e4d3b08422bf08cd66eadbcb92365c2898044`).

---

## Saída final obrigatória (checklist)

| # | Item | Estado |
|---|------|--------|
| 1 | Módulo por módulo auditado | SEM, ML, XAI, Admission, Lifecycle, Blockchain, Monitoring, Metrics, Modules (este doc) |
| 2 | XAI real localizado | ML predictor.py + decision_snapshot + portal xai.py |
| 3 | Admission localizado | decision-engine; decision em submit response |
| 4 | Blockchain localizado | bc-nssmf main.py; tx_hash, block_number, bc_status em submit |
| 5 | Lifecycle localizado | Parcial: admission e bc no submit; runtime/agregado em gap |
| 6 | Gaps documentados | NASP atual vs backup; lifecycle agregado; modules status |
| 7 | Build | OK — executado no node006 |
| 8 | Digest | `sha256:35c1a9a4a86a3cd052f8b553359e4d3b08422bf08cd66eadbcb92365c2898044` (node006) |
| 9 | Screenshot | Validar manualmente após deploy (PNL, Template, Lifecycle) |
