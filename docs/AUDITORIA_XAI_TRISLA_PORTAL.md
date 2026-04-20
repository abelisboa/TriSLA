# AUDITORIA XAI — Portal TriSLA (Explicabilidade no fluxo de criação de SLA)

**Data:** 2025-03-16  
**Escopo:** Verificar se o fluxo de criação de SLA (PNL e Template) possui explicabilidade real no backend e onde está no pipeline TriSLA. Sem alteração de código.

---

## Respostas explícitas

### A. Onde o XAI já existe hoje

| Local | Conteúdo XAI |
|-------|----------------|
| **ML-NSMF** | confidence, risk_score, risk_level, explanation (reasoning, features_importance, method SHAP/LIME/feature_importance). Gerado em `predictor.predict()` e `predictor.explain()`; retornado em POST /api/v1/predict como `prediction` + `explanation`. |
| **Decision Engine** | reasoning (justificativa da decisão), confidence (do ML), ml_risk_score, ml_risk_level; system_xai_explanation (cause, explanation, domains_evaluated) em `system_xai.py`; decision_snapshot (domains, bottleneck, sla_compliance). Gerado em `service.process_decision_from_input()` e `explain_decision()`. Retornado em POST /evaluate como DecisionResult (reasoning, confidence, metadata.decision_snapshot, metadata.system_xai_explanation). |
| **Portal-backend** | Em POST /api/v1/sla/submit: reason e justification (top level) preenchidos com `data.get("reasoning")` do Decision Engine; ml_prediction = resposta completa do /evaluate (contém reasoning, confidence, metadata). Em POST /api/v1/sla/interpret: semantic_class, profile_sla, template_id, message (interpretação semântica/ontology-style); não há confidence nem explanation formal da ontologia. |

### B. Em qual módulo é gerado

| Campo XAI | Módulo que gera |
|-----------|------------------|
| confidence | ML-NSMF (predictor); repassado ao Decision Engine (DecisionResult.confidence). |
| reason / reasoning | Decision Engine (_apply_decision_rules + engine; texto de justificativa). |
| explanation (ML) | ML-NSMF (predictor.explain: reasoning, features_importance). |
| feature importance | ML-NSMF (SHAP/LIME ou feature_importance do modelo). |
| recommended slice justification | SEM-CSMF (slice_type, semantic_class, profile_sla); portal-backend enriquece semantic_class/profile_sla. |
| admission / rejection rationale | Decision Engine (reasoning); repassado ao portal como reason/justification. |
| score breakdown | ML-NSMF (risk_score, risk_level, viability_score); Decision Engine (ml_risk_score, ml_risk_level). |
| system_xai_explanation | Decision Engine (system_xai.explain_decision: cause, explanation, domains_evaluated). |
| ontology match | SEM-CSMF (validação interna); no portal interpret apenas semantic_class e profile_sla (derivados do service_type). |

### C. Se chega ao portal-backend

| Origem | Chega ao portal-backend? | Como |
|--------|---------------------------|------|
| Decision Engine | Sim | call_decision_engine() retorna dict com decision, reason (reasoning), sla_id, timestamp, ml_prediction = resposta bruta do POST /evaluate. |
| submit_template_to_nasp() | Sim | Usa result["reason"] e result["ml_prediction"]; em sla.py response_payload recebe reason, justification = reason, ml_prediction = result.get("ml_prediction"). |
| ML-NSMF | Indiretamente | O portal chama o Decision Engine com context.ml_prediction (resposta do ML); o Decision Engine usa isso ou chama o ML de novo. A resposta do /evaluate contém confidence, ml_risk_score, ml_risk_level (do ML) e reasoning (do Decision). |
| SEM-CSMF (interpret) | Sim | call_sem_csmf() retorna resultado do SEM; sla.py monta resposta com semantic_class, profile_sla, template_id, message. |

### D. Se já chega ao frontend

| Campo | Chega ao frontend? | Observação |
|-------|---------------------|------------|
| reason / justification | Sim | SLASubmitResponse.reason e .justification; frontend atualmente não chama submit. |
| confidence | Sim (dentro de ml_prediction) | No payload de submit, em ml_prediction.confidence. |
| reasoning | Sim (dentro de ml_prediction) | ml_prediction.reasoning. |
| ml_risk_score / ml_risk_level | Sim (dentro de ml_prediction) | ml_prediction.ml_risk_score, ml_prediction.ml_risk_level. |
| system_xai_explanation | Sim (dentro de ml_prediction.metadata) | ml_prediction.metadata.system_xai_explanation (cause, explanation, domains_evaluated). |
| decision_snapshot | Sim (dentro de ml_prediction.metadata) | ml_prediction.metadata.decision_snapshot. |
| feature importance (ML) | Parcial | Gerado no ML-NSMF; no fluxo /evaluate o DecisionResult em service.py não copia ml_explanation/ml_features_importance para result.metadata; apenas engine.decide() faz isso. No path usado pelo portal (/evaluate → process_decision_from_input) não estão garantidos no JSON de resposta. |
| semantic_class / profile_sla (interpret) | Sim | Resposta de interpret já inclui; frontend não chama interpret. |

Resumo: Os campos de submit (reason, justification, ml_prediction com reasoning, confidence, metadata.system_xai_explanation, metadata.decision_snapshot) **chegam** na resposta da API. O frontend hoje não consome submit nem interpret, então **não exibe** nenhum deles.

### E. Quais campos estão disponíveis

- **POST /api/v1/sla/interpret (resposta):** intent_id, service_type, slice_type, semantic_class, profile_sla, template_id, sla_requirements, technical_parameters, status, message, nest_id, created_at. (Sem confidence nem explanation formal de ontologia.)
- **POST /api/v1/sla/submit (resposta):** decision, reason, justification, sla_id, intent_id, nest_id, tx_hash, sem_csmf_status, ml_nsmf_status, bc_status, sla_agent_status, nasp_status (implícito), timestamp, ml_prediction. Dentro de **ml_prediction**: reasoning, confidence, ml_risk_score, ml_risk_level, slos, domains, metadata (decision_snapshot, system_xai_explanation). **Não** garantidos no payload atual (dependem do path): metadata.ml_explanation, metadata.ml_features_importance.

### F. Quais campos precisam apenas ser exibidos

Basta o frontend consumir e exibir (sem inventar):

- **Interpret:** semantic_class, profile_sla, template_id (slice recomendado), message, sla_requirements.
- **Submit:** reason / justification (motivo aceitação/rejeição); ml_prediction.reasoning; ml_prediction.confidence; ml_prediction.ml_risk_score / ml_risk_level (score breakdown); ml_prediction.metadata.system_xai_explanation (explanation, cause, domains_evaluated); sem_csmf_status, ml_nsmf_status, bc_status, sla_agent_status (status de orquestração).

### G. Quais campos ainda não existem ou não estão expostos

| Campo | Status |
|-------|--------|
| ontology_consistency / ontology match explícito (interpret) | SEM-CSMF retorna em create_intent (IntentResponse.ontology_consistency); no path interpret do SEM e na montagem da resposta do portal em sla.py não há campo explícito. **Pendência backend:** expor em /api/v1/sla/interpret se desejado. |
| confidence na interpretação (PNL) | Não retornado na resposta atual de interpret. **Pendência.** |
| ml_explanation / ml_features_importance no retorno do /evaluate | Gerados no ML e disponíveis no Decision Engine (MLPrediction); em process_decision_from_input não são copiados para result.metadata. **Pendência backend:** incluir metadata.ml_explanation e metadata.ml_features_importance na resposta do POST /evaluate. |
| recommended_slice_justification (texto livre) | Equivalente a semantic_class + profile_sla + template_id; já existente. |

---

## Validação: submit_template_to_nasp() e explicação do Decision Engine

- **submit_template_to_nasp()** chama **call_decision_engine()**, que faz POST para `{decision_url}/evaluate` e recebe o corpo da resposta (DecisionResult).
- **call_decision_engine()** retorna: `decision`, `reason` = data.get("reasoning") or data.get("reason"), `sla_id`, `timestamp`, `ml_prediction` = **data** (resposta completa).
- **submit_template_to_nasp()** inclui em seu retorno: `reason` = result da decisão, `ml_prediction` = resultado bruto do /evaluate.
- **sla.py** em submit_sla_template monta `response_payload` com `reason` = result.get("reason"), `justification` = reason, `ml_prediction` = result.get("ml_prediction").

Conclusão: **Sim.** submit_template_to_nasp() já recebe e repassa a explicação do Decision Engine (reasoning) e a resposta completa (ml_prediction), que contém reasoning, confidence, metadata.system_xai_explanation e metadata.decision_snapshot. O frontend só precisa exibir esses campos.

---

## Matriz: Menu × Campo XAI × Fonte × Endpoint × Disponibilidade × Status

| Menu | Campo XAI | Fonte | Endpoint | Disponibilidade | Status |
|------|-----------|--------|----------|------------------|--------|
| Criar SLA PNL (2) | semantic interpretation | SEM-CSMF + portal | POST /api/v1/sla/interpret | semantic_class, profile_sla, message | Disponível; exibir |
| Criar SLA PNL (2) | ontology match | SEM-CSMF | interpret | Implícito em semantic_class/profile_sla | Parcial; ontology_consistency não exposto |
| Criar SLA PNL (2) | slice recomendado | SEM-CSMF + portal | POST /api/v1/sla/interpret | service_type, slice_type, template_id | Disponível; exibir |
| Criar SLA PNL (2) | confiança (interpretação) | — | — | Não existente | Pendência backend |
| Criar SLA PNL (2) | justificativa da decisão | N/A (interpret não decide) | — | — | N/A |
| Criar SLA Template (3) | semantic interpretation | portal | POST /api/v1/sla/submit | semantic_class, profile_sla na resposta | Disponível; exibir |
| Criar SLA Template (3) | ontology match | portal | submit | semantic_class, profile_sla | Disponível; exibir |
| Criar SLA Template (3) | slice recomendado | submit response | submit | service_type | Disponível; exibir |
| Criar SLA Template (3) | confiança | Decision Engine (ML) | submit → ml_prediction.confidence | ml_prediction.confidence | Disponível; exibir |
| Criar SLA Template (3) | justificativa da decisão | Decision Engine | submit → reason, ml_prediction.reasoning | reason, justification, ml_prediction.reasoning | Disponível; exibir |
| Criar SLA Template (3) | motivo aceitação/rejeição | Decision Engine | submit → reason, system_xai | reason, ml_prediction.metadata.system_xai_explanation | Disponível; exibir |
| Criar SLA Template (3) | status de orquestração | submit response | submit | sem_csmf_status, ml_nsmf_status, bc_status, sla_agent_status | Disponível; exibir |
| Criar SLA Template (3) | feature importance | ML-NSMF | submit → ml_prediction.metadata | metadata.ml_features_importance não garantido no /evaluate | Pendência backend |
| Criar SLA Template (3) | score breakdown | ML + Decision | submit → ml_prediction | ml_risk_score, ml_risk_level | Disponível; exibir |
| Criar SLA Template (3) | system XAI (cause, domains) | Decision Engine | submit → ml_prediction.metadata | system_xai_explanation | Disponível; exibir |

---

## Resumo por módulo auditado

### ML-NSMF (apps/ml-nsmf)

- **Endpoints:** POST /api/v1/predict retorna `prediction` (risk_score, risk_level, viability_score, confidence, timestamp) e `explanation` (reasoning, features_importance, method).
- **XAI:** confidence, risk_score, risk_level, explanation.reasoning, explanation.features_importance (SHAP/LIME ou feature_importance). Logging XAI em xai_logging.py; Kafka trisla-ml-xai.
- **Uso no pipeline:** Portal não chama o ML diretamente; Decision Engine chama o ML ou recebe context.ml_prediction do portal. A resposta do Decision Engine inclui confidence e ml_risk_*; ml_explanation/ml_features_importance não estão garantidos no retorno do /evaluate no path atual.

### Decision Engine (apps/decision-engine)

- **Endpoint:** POST /evaluate (SLAEvaluateInput) → DecisionResult.
- **XAI:** reasoning, confidence, ml_risk_score, ml_risk_level; metadata.decision_snapshot; metadata.system_xai_explanation (cause, explanation, domains_evaluated). explain_decision() em system_xai.py; build_decision_snapshot em decision_snapshot.py.
- **Uso no portal:** call_decision_engine() retorna decision, reason (reasoning), ml_prediction = resposta completa. submit_template_to_nasp() repassa tudo; sla.py expõe reason, justification, ml_prediction.

### Portal-backend (apps/portal-backend)

- **sla.py:** interpret retorna semantic_class, profile_sla, template_id, message (sem confidence/explanation de ontologia). submit retorna reason, justification, ml_prediction (e status por módulo).
- **nasp.py:** submit_template_to_nasp() recebe explicação do Decision Engine via retorno de call_decision_engine() e repassa no result.
- **Schemas:** SLASubmitResponse tem reason, justification, ml_prediction; SLASubmitResponse não declara campos aninhados de XAI (são opcionais dentro de ml_prediction).

---

## Conclusão

- **Onde o XAI existe:** ML-NSMF (confidence, explanation, features_importance); Decision Engine (reasoning, confidence, system_xai_explanation, decision_snapshot); portal-backend (reason, justification, ml_prediction na resposta de submit; semantic_class, profile_sla em interpret).
- **O que já chega ao frontend na API:** reason, justification, ml_prediction (com reasoning, confidence, ml_risk_score, ml_risk_level, metadata.system_xai_explanation, metadata.decision_snapshot). Interpret: semantic_class, profile_sla, template_id, message.
- **O que só precisa ser exibido:** Todos os campos acima; frontend não deve inventar explicação.
- **Pendências:** (1) confidence/ontology_consistency em interpret; (2) metadata.ml_explanation e metadata.ml_features_importance na resposta do /evaluate (backend).

*Fim da Auditoria XAI. Nenhum código foi alterado.*
