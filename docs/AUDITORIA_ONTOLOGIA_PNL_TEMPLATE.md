# Auditoria Ontologia-First — SEM + PNL + Template (sem regressão)

**Data:** 2026-03-18  
**Regra:** Ontologia primeiro; nunca inventar campos.

---

## FASE 0–1 — Origem backend de cada campo do PNL

| Campo | Origem real (arquivo) | Observação |
|-------|------------------------|------------|
| **intent_id** | SEM-CSMF `apps/sem-csmf/src/main.py` (POST /api/v1/interpret): `intent_id = str(uuid.uuid4())`; retornado em `return {"intent_id": intent_id, ...}`. Portal-backend `routers/sla.py`: `result.get("intent_id") or result.get("id")`. | Gerado no SEM ao interpretar. |
| **nest_id** | SEM-CSMF `main.py`: `nest = await nest_generator.generate_nest(gst)`; `nest.nest_id` em `nest_generator_db.py` (`nest_id = f"nest-{gst['intent_id']}"`). Retornado em `return {..., "nest_id": nest.nest_id}`. Portal-backend: `result.get("nest_id")`. | Gerado pelo NESTGenerator (GST→NEST). |
| **sla_id** | Portal-backend `routers/sla.py`: `sla_id = result.get("intent_id") or result.get("id")` (alias de intent_id para compatibilidade). | Não é campo distinto no SEM; portal unifica. |
| **technical_parameters** | Portal-backend `routers/sla.py`: `result.get("technical_parameters", {})`; se vazio, preenchido por **defaults por slice type** (URLLC/EMBB/MMTC) no próprio router. SEM-CSMF /interpret **não retorna** technical_parameters; retorna sla_requirements. Parâmetros técnicos editáveis vêm do portal (defaults) ou de `extrair_parametros_tecnicos(intent_text)` em `utils/text_processing.py`. | Híbrido: SEM (sla_requirements) + portal (defaults + parser local). |
| **message** | Portal-backend `routers/sla.py` linha 125: **fixo** `"SLA interpretado pelo SEM-CSMF com sucesso. Ajuste os parâmetros técnicos na próxima etapa."` SEM-CSMF retorna `"message": "Intent interpretado e NEST gerado com sucesso"` (main.py 285). Portal **sobrescreve** com mensagem fixa. | XAI: mensagem real do fluxo (portal ou SEM); nunca inventar score/confidence. |
| **sla_requirements** | SEM-CSMF `main.py`: `validated_intent.sla_requirements.model_dump()` (ontologia + NLP). Portal-backend: `result.get("sla_requirements", {})`; pode ser mesclado com `parametros_extraidos` de `extrair_parametros_tecnicos`. | Ontologia + parser (NLP) no SEM; portal pode enriquecer. |

---

## FASE 2 — Ontologia real localizada

- **SEM-CSMF:**
  - **Ontology loader:** `apps/sem-csmf/src/ontology/loader.py` — OntologyLoader, carrega `trisla_complete.owl` ou `trisla.ttl`.
  - **Parser:** `apps/sem-csmf/src/ontology/parser.py` — OntologyParser, parse_intent, validação semântica.
  - **Matcher:** `apps/sem-csmf/src/ontology/matcher.py` — SemanticMatcher, match intent↔ontologia.
  - **Reasoner:** `apps/sem-csmf/src/ontology/reasoner.py` — SemanticReasoner, `validate_sla_requirements(slice_type, sla_requirements)` (latency, throughput, reliability, etc.).
  - **Constraintes semânticas:** reasoner valida SLA por slice_type; matcher levanta `ValueError` se intent não conforme à ontologia.
- **technical_parameters:** No SEM, o fluxo produz **sla_requirements** (model_dump do Intent); **technical_parameters** como objeto explícito é **construído no portal-backend** (defaults por slice type ou merge com parser local). Ontologia influencia sla_requirements; technical_parameters é representação sugerida no portal.

---

## FASE 3 — XAI real

- **message:** Origem real = portal-backend (string fixa) ou, se o portal repassar a resposta do SEM, SEM-CSMF (`"Intent interpretado e NEST gerado com sucesso"`). Frontend deve **apenas exibir** o campo `message` retornado pela API; nunca criar score fake, confidence fake ou justification inventada.

---

## FASE 4 — Template real (POST /api/v1/sla/submit)

- **Payload real:** SLASubmitRequest (template_id, form_values, tenant_id) → portal-backend monta nest_template e chama nasp_service.submit_template_to_nasp.
- **Resposta:** SLASubmitResponse — decision, reason, justification, sla_id, intent_id, nest_id, service_type, sla_requirements, ml_prediction, blockchain_tx_hash, tx_hash, sla_hash, status, sem_csmf_status, ml_nsmf_status, bc_status, sla_agent_status, block_number, timestamp (todos do result do NASP).
- **Frontend:** Renderizar apenas esses campos (StructuredPayload/dl); sem JSON bruto dominante; sem inventar prediction/decision.

---

## FASE 5 — Observabilidade /modules ainda não usada

- **Backend expõe:** GET /api/v1/modules/, GET /api/v1/modules/{module}, GET /api/v1/modules/{module}/metrics, GET /api/v1/modules/{module}/status.
- **Frontend atual:** Monitoring usa PROMETHEUS_SUMMARY, GLOBAL_HEALTH, MODULES (lista). Metrics usa CORE_METRICS_REALTIME, TRANSPORT_METRICS, RAN_METRICS (portal-backend não expõe core-metrics/realtime; pode 404).
- **Defense / Lifecycle:** Podem ser enriquecidos com /modules/{module}/status e /modules/{module}/metrics quando houver feeds reais (sem inventar).

---

## SEM auditado

- **Semantic parser:** `apps/sem-csmf/src/nlp/parser.py` (NLPParser, parse_intent_text).
- **Ontology service:** OntologyLoader, OntologyParser, SemanticReasoner, SemanticMatcher.
- **Intent mapper:** IntentProcessor (validate_semantic, generate_gst); Intent → Ontology → GST → NEST.
- **Template builder:** NESTGenerator (nest_generator.py, nest_generator_db.py) — GST → NEST.

---

## PNL e Template no frontend

- **PNL:** InterpretResponse usa apenas intent_id, nest_id, sla_id, status, created_at, service_type, slice_type, message, technical_parameters, sla_requirements. Todos existem na resposta do backend; exibição em cards com StructuredPayload; sem score/confidence inventados.
- **Template:** SubmitResponse e exibição em cards (Decisão, Identidade, Requisitos e predição, Blockchain) com campos reais; sla_requirements e ml_prediction em ObjectDl (sem <pre> dominante).

**Conclusão:** PNL e Template já renderizam apenas campos reais; nenhuma alteração de regressão necessária para esta auditoria.

---

## Aviso — Portal-backend e SEM-CSMF

O router `routers/sla.py` usa `nasp_service = NASPService()` (de `src.services.nasp`) e chama `call_sem_csmf`, `submit_template_to_nasp`, `get_sla_status`, `call_metrics`. O ficheiro **atual** `src/services/nasp.py` contém apenas métodos de probe (`check_sem_csmf`, `check_bc_nssmf`). A implementação completa de `call_sem_csmf` (e dos outros) existe em `src_backup_20251208_081013/services/nasp.py`. Em ambiente onde o interpret/submit funcionam, ou existe outra versão do nasp em uso, ou um adapter (ex.: NASP adapter) que o portal chama. **Não foi alterado o backend** (regra do utilizador).

---

## FASE 6 — Build

- `rm -rf .next` e `npm run build` executados em `apps/portal-frontend`. Build concluído com sucesso.
- Rotas geradas: /, /administration, /defense, /metrics, /monitoring, /pnl, /sla-lifecycle, /template, /api/v1/[...path].

---

## FASE 7 — Deploy (comandos)

```bash
# Tag para o registry (ajustar REGISTRY conforme o ambiente)
export REGISTRY=your-registry
docker tag trisla-portal-frontend:latest $REGISTRY/trisla-portal-frontend:latest
docker push $REGISTRY/trisla-portal-frontend:latest

# Rollout (ajustar namespace e nome do deployment)
kubectl rollout restart deployment/trisla-portal-frontend -n <namespace>
kubectl rollout status deployment/trisla-portal-frontend -n <namespace>
```

---

## FASE 8 — Validação do pod (REMOTE_DIGEST = imageID do pod)

Após o rollout:

```bash
kubectl get pods -n <namespace> -l app.kubernetes.io/name=portal-frontend -o jsonpath='{.items[0].status.containerStatuses[0].imageID}'
```

**Digest da imagem construída localmente (build desta auditoria):**

- Image ID: `22fc0f0fb30d`
- Digest: `sha256:5e49c729996bb739afd0836431b1d6f24e94e3e5579262e9e7cbd32550030b00`

Validar que o imageID do pod corresponde a este digest (ou ao digest da imagem que foi pushed após tag).

---

## Saída final (checklist)

| # | Item | Estado |
|---|------|--------|
| 1 | Origem backend de cada campo (intent_id, nest_id, sla_id, technical_parameters, message, sla_requirements) | Documentada em FASE 0–1 |
| 2 | Ontologia localizada (loader, parser, matcher, reasoner; trisla_complete.owl / trisla.ttl) | FASE 2 |
| 3 | SEM auditado (parser NLP, ontology service, intent mapper, template/NEST builder) | Secção «SEM auditado» |
| 4 | PNL corrigido (apenas campos reais; sem score/confidence fake) | Já conforme |
| 5 | Template corrigido (apenas campos reais do SLASubmitResponse) | Já conforme |
| 6 | Build | OK (Next.js build + grep em .next) |
| 7 | Digest | sha256:5e49c729996bb739afd0836431b1d6f24e94e3e5579262e9e7cbd32550030b00 |
| 8 | Pod | Validar com imageID após push + rollout |
| 9 | Screenshot | Validar manualmente após deploy (PNL + Template) |
