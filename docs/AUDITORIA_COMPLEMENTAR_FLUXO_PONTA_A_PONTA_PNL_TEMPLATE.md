# AUDITORIA COMPLEMENTAR — Fluxo Ponta a Ponta TriSLA (Menus PNL e Template)

**Data:** 2025-03-16  
**Escopo:** Lógica real do SEM-CSMF, ontologia OWL, endpoints reais, fluxo SEM → ML → Decision → BC → NASP. Sem alteração de código.  
**Objetivo:** Responder com evidência onde está cada parte do fluxo e o que o frontend pode representar já.

---

## 1. Onde está a lógica real do SEM-CSMF

| Aspecto | Localização | Evidência |
|--------|-------------|-----------|
| **Aplicação** | `apps/sem-csmf/src/main.py` | FastAPI com POST /api/v1/interpret e POST /api/v1/intents |
| **Processamento de intent** | `apps/sem-csmf/src/intent_processor.py` | IntentProcessor: validate_semantic(), generate_gst(); usa OntologyParser, SemanticMatcher |
| **NLP (inferência de slice/constraints)** | `apps/sem-csmf/src/nlp/parser.py` | NLPParser.parse_intent_text(); usado em interpret e em validate_semantic |
| **GST/NEST** | `apps/sem-csmf/src/nest_generator_db.py`, `nest_generator.py` | NESTGeneratorDB.generate_nest(gst); persistência em PostgreSQL |
| **Integração portal → SEM** | `apps/portal-backend/src/services/nasp.py` | NASPService.call_sem_csmf(intent_text=...) → POST sem_url/api/v1/interpret depois sem_url/api/v1/intents |
| **Integração portal submit** | `apps/portal-backend/src/routers/sla.py` | POST /api/v1/sla/submit → nasp_service.submit_template_to_nasp(nest_template, tenant_id) |

A lógica semântica (validação, inferência de tipo, constraints) está no SEM-CSMF; o portal-backend apenas orquestra chamadas. O frontend atual **não chama** esses endpoints.

---

## 2. Onde está a ontologia formal OWL

| Item | Localização | Evidência |
|------|-------------|-----------|
| **Arquivo OWL** | `apps/sem-csmf/src/ontology/trisla_complete.owl` | Arquivo presente no repositório |
| **Arquivo TTL (Turtle)** | `apps/sem-csmf/src/ontology/trisla.ttl` | Alternativa; loader prioriza .owl se existir |
| **Carregador** | `apps/sem-csmf/src/ontology/loader.py` | OntologyLoader: path padrão current_dir + trisla_complete.owl ou trisla.ttl; get_ontology(uri).load(); opcional sync_reasoner_pellet |
| **Uso no pipeline** | `apps/sem-csmf/src/intent_processor.py` | OntologyParser.parse_intent(intent); SemanticMatcher.match(ontology, intent) |
| **Parser ontologia** | `apps/sem-csmf/src/ontology/parser.py` | OntologyParser (usa ontology_loader) |
| **Matcher semântico** | `apps/sem-csmf/src/ontology/matcher.py` | SemanticMatcher(ontology_loader) |
| **Reasoner** | `apps/sem-csmf/src/ontology/reasoner.py` | SemanticReasoner(OntologyLoader); infer_slice_type, validate_sla_requirements |

A ontologia é carregada dinamicamente pelo SEM-CSMF em tempo de execução; não é exposta via API ao frontend. O frontend **não deve** replicar nem carregar a ontologia; apenas exibir resultados da interpretação retornados pelo backend.

---

## 3. Como a ontologia é carregada, usada ou referenciada

- **Carregamento:** OntologyLoader.load() em loader.py; path `ontology/trisla_complete.owl` ou `trisla.ttl`; owlready2 get_ontology(uri).load(); opcional apply_reasoning (Pellet).  
- **Uso:** IntentProcessor valida o intent com ontology_parser.parse_intent() e semantic_matcher.match(); a validação e a inferência (slice type, constraints) ocorrem no SEM-CSMF.  
- **Referência no frontend:** Nenhuma. O frontend não tem acesso à ontologia; deve apenas enviar texto (PNL) ou template (form_values) e exibir a resposta do backend.

---

## 4. Regras semânticas reais existentes hoje

- **Inferência de slice type:** Em main.py (interpret): NLP + fallback por palavras-chave (URLLC: "LATENCIA", "CIRURGIA"; mMTC: "IOT", "SENSOR"; eMBB: "BANDA", "BROADBAND"). Em intent_processor: NLP atualiza intent; OntologyParser + SemanticMatcher validam.  
- **Valores padrão por slice:** interpret_intent em main.py define sla_req_dict por SliceType (URLLC: latency 10ms, reliability, jitter; mMTC: device_density, coverage; eMBB: throughput, reliability).  
- **Validação semântica:** intent_processor.validate_semantic(intent, intent_text) → ontology_parser.parse_intent + semantic_matcher.match.  
- **GST/NEST:** generate_gst() e nest_generator.generate_nest(gst) com templates por slice type (intent_processor._create_gst_template).

Nenhuma dessas regras deve ser duplicada no frontend; o frontend só consome a resposta do SEM-CSMF via portal-backend.

---

## 5. Endpoint real que recebe entrada natural (PNL)

| Camada | Método | Path | Payload | Quem chama |
|--------|--------|------|---------|------------|
| **Portal-backend** | POST | /api/v1/sla/interpret | `{ "intent_text": string, "tenant_id": string }` (SLAInterpretRequest) | Nenhum componente do frontend atualmente |
| **SEM-CSMF (interno)** | POST | /api/v1/interpret | `{ "intent": string, "tenant_id"?: string }` | portal-backend NASPService.call_sem_csmf(intent_text=...) |
| **SEM-CSMF (interno)** | POST | /api/v1/intents | `{ intent, intent_id, tenant_id, service_type, sla_requirements }` | portal-backend após interpret (monta payload e chama intents) |

Fluxo real: Frontend (a implementar) → POST /api/v1/sla/interpret (portal-backend) → backend chama SEM-CSMF /api/v1/interpret → depois SEM-CSMF /api/v1/intents. A resposta do /api/v1/sla/interpret é a consolidada do backend (intent_id, service_type, slice_type, semantic_class, profile_sla, template_id, sla_requirements, etc.).

---

## 6. Endpoint real que recebe template controlado (GST/NEST)

| Camada | Método | Path | Payload | Quem chama |
|--------|--------|------|---------|------------|
| **Portal-backend** | POST | /api/v1/sla/submit | `{ "template_id": string, "form_values": Dict (type/slice_type, latency, throughput, availability, ...), "tenant_id": string }` (SLASubmitRequest) | Nenhum componente do frontend atualmente |
| **Backend interno** | — | — | nest_template = { sla_requirements: form_values, tenant_id, template_id, type/slice_type } | nasp_service.submit_template_to_nasp(nest_template, tenant_id) |

Fluxo real: Frontend (a implementar) → POST /api/v1/sla/submit com template_id (ex.: urllc-basic, embb-basic, mmtc-basic) e form_values (slice type, latency, throughput, availability, etc.) → portal-backend monta nest_template e chama submit_template_to_nasp. submit_template_to_nasp executa: SEM-CSMF (call_sem_csmf com nest_template) → ML-NSMF (call_ml_nsmf) → Decision Engine (call_decision_engine) → se ACCEPT: BC-NSSMF (call_bc_nssmf), NASP Adapter (call_nasp_adapter), SLA-Agent (call_sla_agent). Resposta: decision, reason, sla_id, intent_id, nest_id, tx_hash, sem_csmf_status, ml_nsmf_status, bc_status, nasp_status, sla_agent_status, etc.

---

## 7. Fluxo real após interpretação / após submit

- **Após interpret (PNL):** Portal-backend retorna ao cliente a resposta do SEM-CSMF enriquecida (intent_id, service_type, slice_type, semantic_class, profile_sla, template_id, sla_requirements, technical_parameters, message). Não dispara automaticamente ML/Decision/BC/NASP; apenas interpretação e geração de intent/NEST no SEM-CSMF.  
- **Após submit (template):**  
  1. SEM-CSMF (call_sem_csmf com nest_template) → intent_id, nest_id.  
  2. ML-NSMF (call_ml_nsmf) → predição.  
  3. Decision Engine (call_decision_engine) → decision ACCEPT/REJECT/RENEG, reason, sla_id.  
  4. Se ACCEPT: BC-NSSMF (call_bc_nssmf) → tx_hash, sla_hash, block_number; NASP Adapter (call_nasp_adapter); SLA-Agent (call_sla_agent).  
  5. Portal-backend retorna SLASubmitResponse com todos os status e identificadores.

Ou seja: **interpret** = só SEM-CSMF (entrada → interpretação → template gerado). **submit** = pipeline completo SEM → ML → Decision → (BC + NASP + SLA-Agent se ACCEPT).

---

## 8. O que hoje já existe de ponta a ponta

- **Backend:** POST /api/v1/sla/interpret e POST /api/v1/sla/submit implementados; NASPService integra SEM-CSMF, ML-NSMF, Decision Engine, BC-NSSMF, NASP Adapter, SLA-Agent.  
- **SEM-CSMF:** /api/v1/interpret e /api/v1/intents; ontologia OWL; NLP; GST/NEST; persistência; envio para Decision Engine (I-01).  
- **Payloads e contratos:** SLAInterpretRequest, SLASubmitRequest, SLASubmitResponse e resposta de interpret definidos no portal-backend.  
- **Frontend:** Não chama interpret nem submit; PnlSlaSection e TemplateSlaSection são mock/local.

---

## 9. O que hoje ainda não existe

- **Frontend:** Chamadas a POST /api/v1/sla/interpret e POST /api/v1/sla/submit; exibição fiel “entrada → interpretação → template gerado” (PNL) e “template → decisão → blockchain/NASP” (Template).  
- **Portal-backend:** GET /api/v1/sla (listagem de SLAs para Lifecycle); agregador SLA lifecycle (SEM+ML+BC+NASP states) para tabela e para Defense Panel.  
- **Exposição da ontologia ao frontend:** Não existe nem é necessária; o frontend só exibe resultados da interpretação.

---

## 10. O que o frontend pode representar já

- **Menu 2 — Criar SLA PNL:** Enviar intent_text + tenant_id para POST /api/v1/sla/interpret; exibir na tela: frase natural, intent_id, service_type/slice_type, semantic_class, profile_sla, template_id, sla_requirements (e technical_parameters se presente), mensagem de sucesso/erro. Não inventar interpretação no cliente; apenas mostrar a resposta do backend.  
- **Menu 3 — Criar SLA Template:** Enviar template_id + form_values (slice type, latency, throughput, availability, etc.) + tenant_id para POST /api/v1/sla/submit; exibir: decisão (ACCEPT/REJECT/RENEG), reason, sla_id, intent_id, nest_id, tx_hash, sem_csmf_status, ml_nsmf_status, bc_status, nasp_status, sla_agent_status. Não inventar decisão nem estados; apenas representar o retorno real.

---

## 11. O que depende de backend ou agregação futura

- Contagem de SLAs (total, active, approved, monitored) para Home.  
- Lista de SLAs para SLA Lifecycle (GET /api/v1/sla ou equivalente com colunas Estado, Admission, Blockchain, NASP, Runtime).  
- Painel SLA-Aware Full Defense agregado (admission, prediction, semantic validation, blockchain, deployment, observability) por SLA.  
- Nenhuma dessas pendências impede o frontend de representar corretamente os fluxos PNL e Template com os endpoints atuais.

---

## 12. Como a criação real do SLA chega à orquestração/implantação NASP

- **Submit (template):** submit_template_to_nasp() chama em sequência: call_sem_csmf → call_ml_nsmf → call_decision_engine. Se decision == "ACCEPT": call_bc_nssmf, call_nasp_adapter, call_sla_agent. call_nasp_adapter usa NASP Adapter (trisla-nasp-adapter:8085) para registro/orquestração. Ou seja, a criação real do SLA, após decisão de aceite, chega ao BC-NSSMF (registro em blockchain), NASP Adapter (orquestração/implantação) e SLA-Agent.  
- **Interpret (PNL):** Não dispara orquestração; apenas gera intent e NEST no SEM-CSMF. Para levar ao NASP, o usuário deve usar o resultado da interpretação no menu Template (ou um fluxo futuro “usar template gerado”) e submeter via /api/v1/sla/submit.

---

## 13. Fluxo real ponta a ponta (resumo)

```
PNL (Menu 2):
  Frontend → POST /api/v1/sla/interpret { intent_text, tenant_id }
  → Portal-backend → SEM-CSMF POST /api/v1/interpret { intent }
  → SEM-CSMF: NLP + Ontology (loader/reasoner/parser/matcher) → GST/NEST
  → SEM-CSMF POST /api/v1/intents (interno)
  → Resposta ao frontend: intent_id, service_type, slice_type, semantic_class, profile_sla, template_id, sla_requirements, etc.

Template (Menu 3):
  Frontend → POST /api/v1/sla/submit { template_id, form_values, tenant_id }
  → Portal-backend submit_template_to_nasp():
     SEM-CSMF (nest_template) → ML-NSMF → Decision Engine
     → Se ACCEPT: BC-NSSMF, NASP Adapter, SLA-Agent
  → Resposta ao frontend: decision, reason, sla_id, intent_id, nest_id, tx_hash, sem_csmf_status, ml_nsmf_status, bc_status, nasp_status, sla_agent_status, etc.
```

---

## 14. Papel exato do frontend em PNL e Template

- **PNL:** Coletar frase natural e tenant_id; chamar POST /api/v1/sla/interpret; exibir entrada → interpretação → template gerado (campos retornados), sem replicar ontologia nem lógica semântica.  
- **Template:** Coletar template_id e form_values (slice type, latency, throughput, availability, etc.) e tenant_id; chamar POST /api/v1/sla/submit; exibir decisão e estados reais (SEM, ML, BC, NASP, SLA-Agent), sem inventar dados.  
- **Limites atuais:** Listagem de SLAs e painel Defense agregado não existem no backend; não exibir dados fictícios para esses blocos.

---

## 15. Distinção existente / derivável / pendente

| Item | Existente | Derivável | Pendente |
|------|-----------|-----------|----------|
| Interpretação PNL | ✅ Backend + SEM-CSMF | — | Frontend apenas consome |
| Resposta interpret (campos) | ✅ intent_id, service_type, slice_type, semantic_class, profile_sla, template_id, sla_requirements | — | — |
| Submit template | ✅ Backend + pipeline completo | — | Frontend apenas consome |
| Resposta submit (campos) | ✅ decision, reason, sla_id, tx_hash, status por módulo | — | — |
| Lista SLAs (Lifecycle) | — | — | ✅ Agregador backend |
| Contagem SLAs (Home) | — | — | ✅ Agregador backend |
| Defense Panel agregado | — | — | ✅ Agregador backend |
| Ontologia no frontend | Não exposta | — | Não necessária |

---

*Fim da Auditoria Complementar. Nenhum código foi alterado.*
