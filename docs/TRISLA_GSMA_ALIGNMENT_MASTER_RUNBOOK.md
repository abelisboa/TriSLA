# TriSLA — GSMA / 3GPP Alignment Master Runbook

**Documento:** fonte única de verdade (SSOT) para a migração **canonical SLA + semantic augmentation**, controlo oficial de fases, manual operacional obrigatório para laboratório, guia científico de execução e mecanismo explícito **anti-regressão** e **anti-improvisação** (disciplina interna do repositório; não substitui políticas organizacionais externas nem certificações de terceiros).

**Versão runbook:** 0.2 (hardening documental v1)

**Documentos satélite (resumo operacional):** `docs/TRISLA_GSMA_ALIGNMENT_EXECUTION_RULES.md`

**Última actualização:** 2026-05-14 — **FASE 3** mantém-se **FAIL** no sentido GSMA (script de equivalência runtime ainda não reexecutado com PASS); **infra:** plano de controlo e `trisla-portal-backend` **restaurados operacionalmente** (`kube-controller-manager-node1` na API; pods portal `Running`/`Ready`; health HTTP **200** com corpo `status=unhealthy` — ver §12-J). Evidências: `evidencias_control_plane_portal_restore_20260514T143349Z/`, `evidencias_portal_runtime_unblock_20260514T143200Z/`, `evidencias_gsma_alignment_phase3_runtime_20260514T135710Z/`.

---

## Controlo de fases (resumo) — **INVARIANTE**

| Fase | Nome | Estado | Última validação |
|------|------|--------|------------------|
| 0 | Auditoria | **PASS** (repo) | Ver §9 (FASE 0) |
| 1 | Modelagem | **PASS** (doc) | `docs/TRISLA_CANONICAL_SLA_MODEL.md` |
| 2 | Canonicalization layer | **PASS** (repo) | `evidencias_gsma_alignment_phase2_20260514T130000Z/` |
| 3 | Backward compatibility | **FAIL** (GSMA runtime gate; portal **OK** pós-recuperação CP — §12-J) | `evidencias_control_plane_portal_restore_20260514T143349Z/`, `evidencias_gsma_alignment_phase3_runtime_20260514T135710Z/` (+ estrutural `evidencias_gsma_alignment_phase3_20260514T134713Z/`) |
| 4 | Decision Engine alignment | **NOT_STARTED** | — |
| 5 | XAI alignment | **NOT_STARTED** | — |
| 6 | SLA-Agent alignment | **NOT_STARTED** | — |
| 7 | Listings update | **NOT_STARTED** | — |
| 8 | Paper validation | **NOT_STARTED** | — |
| 9 | E2E validation (node006) | **NOT_STARTED** | — |
| 10 | Scientific freeze | **NOT_STARTED** | — |

**Regra de avanço:** não avançar fase **N+1** sem **PASS** explícito na fase **N** e registo actualizado neste ficheiro (data, evidência, operador).

**Nota operacional (2026-05-14):** o **portal** voltou a ter pods **Running/Ready** e o endpoint **`/api/v1/health/global`** responde **HTTP 200** após recuperação do plano de controlo / kubelet em `node1` (§12-J; **não** marcar **FASE 3 PASS** até `docs/scripts/gsma_phase3_runtime_validate.sh` produzir evidência PASS). As **FASEs 4–10** permanecem **bloqueadas** pelo contrato GSMA até **PASS** formal da FASE 3 (§27).

**Regra de estado:** estados **PASS** / **NOT_STARTED** / **FAIL** só mudam por decisão documentada neste runbook e por evidência anexa; **não** se alteram por conveniência narrativa em chats ou PRs sem actualização do quadro e do histórico (§28).

---

## Índice (navegação)

| Secção | Conteúdo |
|--------|----------|
| §1 | Contexto científico completo |
| §2 | Architectural Invariants |
| §3 | Baseline científico congelado |
| §4 | Dependency map completo |
| §5 | Modelo canónico definitivo e coexistência |
| §6 | Backward Compatibility Guarantees |
| §7 | Estratégia anti-regressão |
| §8 | Cabeçalho do template de fase (A–H) |
| §9–§19 | FASE 0 a FASE 10 (cada uma com A–H) |
| §20 | Mandatory Gates |
| §21 | Scientific Validation Rules |
| §22 | Runtime Evidence Model |
| §23 | Deployment Rules |
| §24 | Forbidden Changes |
| §25 | Paper Alignment Rules |
| §26 | Checklist obrigatório antes de cada alteração |
| §27 | Future Execution Contract |
| §28 | Histórico de alterações do runbook |

---

## §1. Contexto científico completo

### 1.1 Por que o TriSLA inicialmente parecia “custom JSON”

- O endpoint `POST /api/v1/sla/submit` aceita `template_id` + `form_values: Dict[str, Any]` sem partição formal entre “requisito de slice/QoS” e “contexto de negócio”.
- O Portal monta `nest_template` com `sla_requirements` = **cópia integral** de `form_values` (`apps/portal-backend/src/routers/sla.py`), pelo que campos como `service_description`, `edge_processing` e `availability_target` coexistem no mesmo plano que latência/throughput quando existem.
- O SEM-CSMF aceita `IntentRequest.sla_requirements` como **dict livre** além do subconjunto modelado por `SLARequirements` (`apps/sem-csmf/src/models/intent.py`), o que é tecnicamente flexível mas editorialmente “flat JSON” quando comparado com vocabulários de referência GSMA/3GPP.

### 1.2 Por que isso reduz maturidade GSMA / leitura 3GPP (no sentido editorial)

- Literatura e relatórios GSMA/3GPP tendem a separar **perfil de slice / requisitos de serviço** de **informação contextual** (negócio, segurança, continuidade).
- SST/SD e argumentação de perfil de rede são difíceis de **defender por escrito** quando o payload mistura tudo num único dicionário sem namespaces estáveis.
- Isto não implica que o TriSLA esteja “errado” operacionalmente; implica **menor legibilidade externa** e maior custo de mapeamento para dissertação e relatórios de maturidade.

### 1.3 Por que semantic augmentation é diferencial (e distinto de “SLA canónico”)

- O diferencial TriSLA (NL + formulário rico + rastreabilidade semântica) deve permanecer **auditável** e **explicável** (XAI) sem poluir o subconjunto que alimenta contratos numéricos (BC flatten, SLOs, métricas).
- **Semantic augmentation** (descrições, prioridades, continuidade, edge, etc.) informa decisão e narrativa científica; **canonical SLA requirements** (subconjunto estável de métricas e perfil de slice) visa contratos e reprodutibilidade. São complementares; **não** são a mesma camada (ver §5.3).

### 1.4 Por que um canonical SLA model é necessário

- Uma camada canónica explícita (`service_requirements` + `semantic_context` + `slice_service_type` [+ `sst`/`sd` opcionais]) permite:
  - documentação alinhada a vocabulário GSMA/3GPP **onde aplicável**;
  - tradução estável para BC-NSSMF, ML e DE **sem reinterpretar chaves ambíguas** a cada módulo;
  - evolução de dados sem apagar histórico de experimentos nem invalidar datasets que usam o dict plano, desde que as garantias retroactivas (§6) sejam respeitadas.

### 1.5 GSMA-aligned ≠ GSMA-compliant (obrigatório)

- **GSMA-aligned** neste runbook significa: **orientação editorial e de dados** para legibilidade e mapeamento, com separação explícita entre requisitos de serviço e contexto semântico, **sem** afirmação de certificação, homologação ou conformidade total com qualquer programa GSMA.
- **GSMA-compliant** (ou equivalente) **não** é objectivo declarado deste runbook nem premissa do código existente; qualquer afirmação nesse sentido em papers, slides ou relatórios **exige** evidência externa e processo de certificação — **proibido inventar** (§24).

### 1.6 Por que a camada semântica deve ser separada (conceptualmente e, nas fases futuras, nos dados)

- Separação conceptual evita que explicações XAI confundam “latência contratual” com “prioridade de negócio”.
- Separação de dados (FASE 1–2 e seguintes) permite coexistência: o legado continua válido enquanto o canónico cresce (§6, §7).

### 1.7 Por que o runtime actual não pode sofrer regressão científica

- Baseline científico, listings e freezes dependem do pipeline observado: **SEM-CSMF → ML-NSMF → Decision Engine → NASP Adapter → BC-NSMF → SLA-Agent** (ordem orquestrada pelo Portal na prática operacional; ver §4).
- Regressão aqui significa: decisões, scores, thresholds, pesos, contratos BC, ou evidências de governação deixarem de ser **reprodutíveis** ou **comparáveis** com o baseline documentado — **FAIL** de fase e obrigação de rollback (§20, §27).

### 1.8 Por que não pode haver regressão (síntese já presente na v0.1 — mantida)

- Qualquer alteração deve ser **aditiva** ou atrás de **compatibilidade** explícita e testes E2E em `node006` com digest GHCR quando a fase o exigir.
- O quadro de fases (topo) é a **autoridade** de progresso; improvisação fora das fases é **incompatível** com este runbook (§27).

---

## §2. Architectural Invariants

As seguintes propriedades são **invariantes** do desenho TriSLA validado no laboratório, salvo nova fase explicitamente autorizada a alterá-las **e** actualização do runbook:

| Invariante | Declaração |
|------------|-------------|
| Interpretação semântica | **MUST remain:** SEM-CSMF continua a interpretar NL / intent e a enriquecer o fluxo semântico; não se remove o papel semântico em favor de “só JSON técnico”. |
| Explainability | **MUST remain:** saídas de raciocínio / domínios / metadata útil para XAI conforme pipeline actual; evoluções não podem silenciar explicabilidade sem fase dedicada (FASE 5). |
| Multidomain telemetry | **MUST remain:** contrato de telemetria e caminhos de agregação usados pelo pipeline **não** podem ser quebrados sem fase e validação; evolução = adição compatível. |
| Blockchain governance | **MUST remain:** registo BC com `tx_hash` / `block_number` no fluxo validado **não** pode ser removido nem “simulado” como substituto do real quando a fase exige evidência real. |
| Runtime assurance | **MUST remain:** SLA-Agent e estados de ciclo relevantes para assurance **não** são opcionais no sentido científico quando o cenário de freeze os inclui. |
| Decision Engine scoring | **MUST NOT change** (fórmulas / `decision_score_mode`): alteração só com nova fase científica explícita e baseline novo — **fora** do âmbito GSMA alignment salvo decisão de projeto separada. |
| Thresholds | **MUST NOT change** nas fases 2–5 deste runbook; qualquer mudança é **FAIL** arquitectural deste programa de alinhamento. |
| Weights | **MUST NOT change** (idem). |
| Datasets históricos | **MUST remain valid:** não renomear nem invalidar; novas colunas/views **opcionais** apenas. |
| Freezes | **MUST remain reproducible:** digests, fixtures e relatórios referenciados permanecem rastreáveis; não apagar evidências (§27). |

---

## §3. Baseline científico congelado

> **Nota:** hashes/digests exatos variam no tempo; antes de cada deploy de fase, o operador deve copiar para este runbook **e** para o pacote de freeze os valores **reais** do cluster.

### 3.1 Payloads válidos (contrato API — referência)

- **Request:** `SLASubmitRequest` — `template_id`, `form_values`, `tenant_id`  
  Ficheiro: `apps/portal-backend/src/schemas/sla.py`
- **Response:** `SLASubmitResponse` — `intent_id`, `service_type`, `sla_requirements`, `metadata`, BC/NASP/SLA-Agent, XAI, etc.  
  Ficheiro: `apps/portal-backend/src/schemas/sla.py`
- **O que NÃO pode mudar sem fase dedicada:** superfície mínima aceite pelo Portal para submit; remoção de `template_id` ou `form_values` é **FAIL** (§24).

### 3.2 Nest template (comportamento actual)

- `nest_template["sla_requirements"] = request.form_values` (+ `template_id`, `tenant_id`, opcionalmente `type`/`slice_type` extraídos de `form_values`).  
  Ficheiro: `apps/portal-backend/src/routers/sla.py` (função `submit_sla_template`)

### 3.3 SEM-CSMF — intent / SLA

- `SLARequirements` (latency, throughput, reliability, jitter, coverage) em `apps/sem-csmf/src/models/intent.py`
- `IntentRequest.sla_requirements: Optional[Dict[str, Any]]` — aceita dict além do modelo estrito.
- **FASE 2 (facto de repositório):** `canonical_sla` adicionado em `POST /api/v1/interpret` e em `metadata` / resposta de `POST /api/v1/intents` via `apps/sem-csmf/src/canonical_sla.py` — **adição**; não substitui `sla_requirements` enviado ao Decision Engine.

### 3.4 Endpoints (não alterar sem fase dedicada)

- `POST /api/v1/sla/submit` (Portal)
- `POST /api/v1/interpret`, `POST /api/v1/intents` (SEM-CSMF) — conforme deployment actual

### 3.5 Listings, figuras e dissertação

- **Listings aprovados** para o paper/dissertação são os congelados nas pastas de evidência e commits referenciados nos freezes; actualização formal só na **FASE 7** e **FASE 8** com PASS explícito.
- **Figuras aprovadas** seguem o mesmo princípio: não substituir figuras congeladas sem novo freeze.
- **O que NÃO pode mudar:** números reportados como resultados finais sem reexecutar o pipeline e sem novo pacote de evidência.

### 3.6 Datasets / experimentos

- **Não** renomear, **não** invalidar ficheiros de datasets existentes; novas colunas ou views devem ser **opcionais**.

### 3.7 Evidências, digests e freezes (laboratório node006)

Exemplos já utilizados em congelações (ajustar caminhos se o operador mover pastas):

- `evidencias_runtime_listings_20260514T011244Z` — E2E e listings (tenant `smart-port-beta`, template `semantic-embb-template`)
- `evidencias_multidomain_xai_*` — multidomínio + XAI
- `evidencias_fix_bc_nssmf_semantic_slo_*` / digest BC corrigido — governance
- `evidencias_gsma_alignment_phase2_20260514T130000Z/` — canonicalização SEM-CSMF (FASE 2)

**Política de imagens:** GHCR + **digest** (`skopeo inspect`); ver `kubectl get pods` / imagens nos relatórios de freeze (não fixar aqui um digest único como eternamente válido).

### 3.8 Orchestration flow (referência única)

`semantic SLA request → SEM-CSMF → ML-NSMF → Decision Engine → NASP Adapter → BC-NSMF → SLA-Agent` (com orquestração de NSI no adapter quando política e decisão o exigirem; detalhe em código Portal `apps/portal-backend/src/services/nasp.py`).

### 3.9 Evidência de governação (`tx_hash`, `block_number`)

- Baseline científico exige que cenários de freeze documentem **tx_hash** e **block_number** quando o BC está no caminho do cenário — valores **reais** copiados da resposta do Portal/BC, não inventados.

### 3.10 Runtime assurance evidence

- Estados `sla_agent_status`, fluxos de revalidação quando aplicável, e campos `telemetry_complete` / metadata associada devem constar do `final_response.json` ou equivalente no pacote de evidência da fase.

---

## §4. Dependency map completo

| Módulo | Consome (principal) | Produz / repassa | Depende de | Impacto de regressão |
|--------|---------------------|------------------|------------|----------------------|
| **Portal Backend** | `SLASubmitRequest`; respostas SEM/DE/BC/SLA-Agent | `nest_template`; orquestra chamadas; `SLASubmitResponse` unificado | URLs internas (`*_URL`); schemas estáveis | Quebra E2E; respostas incompletas; perda de metadata de orquestração |
| **SEM-CSMF** | `nest_template` / NL; `IntentRequest` | `service_type`, NEST, `sla_requirements`, `metadata` (+ `canonical_sla` desde FASE 2) | DB NEST; ontologia/NLP configurados | Perda de semântica; decisões errónicas downstream |
| **ML-NSMF** | Features + slice + metadata | `ml_prediction`, risco, latências | Contrato de features do DE | Drift de features; **não confundir** com mudança de pesos/thresholds |
| **Decision Engine** | Intent + telemetria + metadata | `decision`, XAI, metadata de orquestração | ML opcional; telemetria | **Crítico:** qualquer mudança de score/threshold viola invariantes |
| **NASP Adapter** | decisão ACCEPT + payload orquestração | NSI / respostas adapter | Política `orchestration_required` etc. | Falhas de provisionamento; NSI inconsistente |
| **BC-NSMF** | `register-sla` (flatten SLOs) | `tx_hash`, `block_number` | Payload SLO válido | Perda de cadeia de governação científica |
| **SLA-Agent** | pipeline + ingest / revalidação | assurance / estados | Contratos telemetria | Assurance falso negativo/positivo |

**Dependências críticas transversais:** ordem do pipeline no Portal; URLs internas; `telemetry_contract_version`; **não** introduzir “integrações” não presentes no código sem fase e sem evidência (§24).

---

## §5. Modelo canónico definitivo e coexistência

### 5.1 Documento SSOT do schema alvo

**Documento detalhado:** `docs/TRISLA_CANONICAL_SLA_MODEL.md` (v0.1 — modelagem; campos alvo e mapeamento desde `form_values`).

### 5.2 Esqueleto lógico (resumo editorial — o detalhe field-a-field está no documento canónico)

```json
{
  "slice_service_type": "...",
  "sst": null,
  "sd": null,
  "service_requirements": { },
  "semantic_context": { }
}
```

### 5.3 Semantic augmentation ≠ canonical SLA requirements

| Dimensão | Semantic augmentation | Canonical SLA requirements |
|----------|----------------------|----------------------------|
| Objetivo | Preservar intenção NL, prioridades, políticas editoriais, contexto de negócio | Subconjunto estável de métricas e perfil de slice para contratos e leitura GSMA-like |
| Onde vive hoje | Misturado em `form_values` / `sla_requirements` planos | Em evolução: FASE 2 expõe `canonical_sla` **em paralelo** no SEM-CSMF |
| Risco se confundidos | XAI ilisível; BC flatten ambíguo | Perda de compatibilidade; regressão científica |
| Regra | **Nunca** apagar augmentation para “limpar” métricas | **Nunca** forçar só canónico sem PASS da FASE 3 |

### 5.4 Campos GSMA-aligned (vocabulário)

- Significa **nomes e partição** inspirados em boas práticas de leitura GSMA/3GPP **onde faz sentido**; não significa conformidade total (§1.5).
- `sst` / `sd` permanecem **opcionais** no modelo alvo até existir mapeamento estável no laboratório (`TRISLA_CANONICAL_SLA_MODEL.md`).

### 5.5 Coexistência dos modelos

- **Legado:** `template_id` + `form_values` / `sla_requirements` plano — permanece válido (§6).
- **Canónico:** adicionado por fases; consumo alargado no DE/BC/etc. só após fases explicitamente PASS e sem violar invariantes.

---

## §6. Backward Compatibility Guarantees

| Garantia | Significado operacional |
|----------|---------------------------|
| Payload antigo | `SLASubmitRequest` com `template_id` + `form_values` continua válido até decisão contrária documentada numa fase PASS que altere o schema do Portal. |
| `template_id` | **MUST remain** no contrato de submit e na projeção para `nest_template` / `sla_requirements` onde hoje existe. |
| `form_values` | **MUST remain** como veículo principal de entrada utilizador; evoluções são aditivas. |
| Decision Engine actual | Continua a ser o motor de decisão; fases futuras podem **ler** mais campos, **não** mudar scoring/thresholds/pesos sem programa separado. |
| Orchestration actual | Fluxo NASP adapter existente mantém semântica; não introduzir “orquestração paralela inventada”. |
| Governance actual | BC-NSMF mantém papel de ancoragem; `tx_hash` / lifecycle não podem ser apagados (§24). |

---

## §7. Estratégia anti-regressão (consolidada)

1. **Backward compatibility:** manter `SLASubmitRequest` idêntico na superfície; qualquer envelope novo opcional (header, query `?canonical=1`, ou campo opcional no JSON) só após **FASE 3 PASS** e registo.
2. **Coexistência:** SEM-CSMF aceita **ambos** — dict legado e bloco canónico — durante janela de transição.
3. **Canonicalization layer:** função pura (no SEM-CSMF desde FASE 2) `legacy → canonical_model` + preservação de legado em `legacy_input` / metadata.
4. **Payload translation:** BC e módulos que esperam dict plano continuam a receber **projeção** derivada do canónico **apenas** quando a fase respectiva garantir equivalência observável.
5. **Sem alteração de thresholds/pesos:** FASEs 4–5 limitam-se a **roteamento de campos** e enriquecimento de XAI **sem** mudar fórmulas de score.
6. **Rollback:** `kubectl set image` para digest anterior por módulo tocado; reverter commits por fase; reexecutar E2E da §18 (FASE 9) quando aplicável.

---

## §8. Fases 0 a 10 — template obrigatório (A–H)

Cada fase segue o mesmo esqueleto:

- **A.** Objetivo científico  
- **B.** Ficheiros permitidos / proibidos  
- **C.** Regras da fase  
- **D.** Critérios PASS  
- **E.** Critérios FAIL  
- **F.** Evidências obrigatórias  
- **G.** Rollback  
- **H.** Dependências futuras  

---

## §9. FASE 0 — Auditoria — **PASS (repositório)**

### A. Objetivo científico

- **Por que existe:** sem inventário de schema e dependências, qualquer “alinhamento GSMA” degenera em mudanças ad hoc.
- **Problema que resolve:** falta de mapa de colagem entre Portal, SEM-CSMF, DE, BC e SLA-Agent.
- **Risco que evita:** refactors que partem integrações sem compreender contratos.

### B. Ficheiros permitidos / proibidos

| Pode alterar | Não pode alterar (sem nova fase) |
|--------------|-----------------------------------|
| Documentação (`docs/**`), índices de auditoria | Thresholds, pesos, `decision_score_mode`, Helm de produção sem processo |

### C. Regras da fase

- Auditoria **estática** no Git primeiro; pacote `node006` opcional mas recomendado com paths limitados.
- **Proibido:** `grep evidencias_*` recursivo sem limite (risco de encher disco no laboratório).

### D. Critérios PASS

- Tabela de ficheiros-chave documentada (mantida neste runbook).
- Achados reprodutíveis a partir dos paths do repositório.

### E. Critérios FAIL

- Inventário incompleto que omita Portal submit ou SEM-CSMF intent.
- Evidência gerada por comandos que corrompem armazenamento do nó.

### F. Evidências obrigatórias

- Repo: secção “Achados” abaixo; opcional `evidencias_gsma_alignment_audit_<TS>/` em `node006` com `final_response.json`, refs de código, export OpenAPI se existir.

### G. Rollback

- N/A (documental); remover docs incorrectos se necessário.

### H. Dependências futuras

- **FASE 1** depende do inventário da FASE 0.

### Achados (ficheiros-chave) — conteúdo preservado da v0.1

| Área | Evidência (repo) |
|------|------------------|
| Request submit | `apps/portal-backend/src/schemas/sla.py` (`SLASubmitRequest`) |
| Nest template | `apps/portal-backend/src/routers/sla.py` (`nest_template`, log `[SLA SUBMIT]`) |
| Response | `apps/portal-backend/src/schemas/sla.py` (`SLASubmitResponse`) |
| SEM-CSMF intent | `apps/sem-csmf/src/models/intent.py`, `apps/sem-csmf/src/main.py`, `decision_engine_client.py` |
| Revalidação | `SLARevalidateTelemetryRequest` em `apps/portal-backend/src/schemas/sla.py` |

### Artefactos esperados em disco (laboratório) — preservado

Gerar em `node006` sob `evidencias_gsma_alignment_audit_<TS>/` (quando a fase operacional for executada):

- cópia de `final_response.json` de um E2E;
- grep/refs de código (**sem** `grep evidencias_*` recursivo sem limite — risco de encher disco);
- schemas exportados (`jq` OpenAPI se existir).

### Riscos — preservado

- Confundir `sla_requirements` Pydantic estrito com dict livre no mesmo pipeline.

### Status — preservado

**PASS** para auditoria estática no Git; **PENDENTE** geração do pacote `evidencias_gsma_alignment_audit_*` no `node006` (executar script dedicado com paths limitados).

---

## §10. FASE 1 — Modelagem — **PASS (documento)**

### A. Objetivo científico

- Definir modelo canónico e mapeamento desde `form_values` sem tocar no runtime.

### B. Ficheiros permitidos / proibidos

| Pode alterar | Não pode alterar |
|--------------|------------------|
| `docs/TRISLA_CANONICAL_SLA_MODEL.md`, este runbook | Código de módulos do pipeline sem fase própria |

### C. Regras da fase

- Apenas documentação; nenhum deploy obrigatório.

### D. Critérios PASS

- Documento v0.1 publicado e referenciado.

### E. Critérios FAIL

- Modelo que contradiz BC flatten actual sem plano de coexistência.

### F. Evidências obrigatórias

- `docs/TRISLA_CANONICAL_SLA_MODEL.md`

### G. Rollback

- Reverter commit do doc.

### H. Dependências futuras

- **FASE 2+** dependem da existência do modelo alvo.

### Entregável e validação — preservados

- `docs/TRISLA_CANONICAL_SLA_MODEL.md` (v0.1)
- Revisão interna: campos cobrem listing científico e BC flatten sem contradição.

### Status — preservado

**PASS**

---

## §11. FASE 2 — Canonicalization layer — **PASS (repositório)**

### A. Objetivo científico

- Implementar transformação `semantic input → canonical SLA → semantic_context` **sem** remover o payload antigo.

### B. Ficheiros permitidos / proibidos

| Pode alterar | Não pode alterar |
|--------------|------------------|
| `apps/sem-csmf/src/canonical_sla.py`, `apps/sem-csmf/src/main.py`, testes SEM-CSMF associados | Decision Engine, ML-NSMF, NASP Adapter, BC-NSMF, SLA-Agent, Helm (conforme âmbito registado na FASE 2) |

### C. Regras da fase

- Alterações **aditivas** em metadata/resposta; **não** substituir `sla_requirements` enviado ao DE.
- Sem alteração de thresholds, pesos ou scoring.

### D. Critérios PASS

- `py_compile` nos ficheiros tocados.
- Testes unitários locais PASS.
- Payload legado inalterado na superfície.

### E. Critérios FAIL

- Remoção de `template_id` / `form_values` do fluxo.
- Mudança de decisão observável por causa da canonicalização (deveria ser impossível se só metadata).

### F. Evidências obrigatórias

- Pasta: `evidencias_gsma_alignment_phase2_20260514T130000Z/`
  - `canonical_payload_legacy_embb.json`, `canonical_payload_legacy_urllc.json`, `canonical_payload_legacy_mmtc.json`, `canonical_payload_native.json`
  - `validation_report.md`

### G. Rollback

- Reverter commits que toquem `apps/sem-csmf/src/canonical_sla.py`, `apps/sem-csmf/src/main.py` e `apps/sem-csmf/tests/test_canonical_sla.py`; ajustar este runbook se se desfizer a fase.
- Em cluster: `kubectl set image` para digest anterior **apenas** da imagem `sem-csmf` quando aplicável.

### H. Dependências futuras

- **FASE 3** valida equivalência comportamental com payloads reais e fixtures congeladas.

### Ficheiros alterados (código) — preservado da v0.1

- `apps/sem-csmf/src/canonical_sla.py` — função pura `canonicalize_sla_request(payload: dict) -> dict` (contrato: `slice_service_type`, `sst`, `sd`, `service_requirements`, `semantic_context`, `legacy_input` com `template_id` + `form_values`).
- `apps/sem-csmf/src/main.py` — `POST /api/v1/interpret` inclui `canonical_sla` na resposta; `POST /api/v1/intents` injeta `metadata["canonical_sla"]` antes da chamada ao Decision Engine e repete `canonical_sla` na metadata da `IntentResponse` (campos existentes inalterados).
- `apps/sem-csmf/tests/test_canonical_sla.py` — testes unitários mínimos (eMBB / URLLC / mMTC legado, legado plano, `form_values` aninhado, payload nativo).

### Validação — preservada

- `python3 -m py_compile` nos ficheiros tocados — **PASS** (execução local).
- `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'` — **PASS** (6 testes).

### Riscos — preservados

- **Tamanho de metadata:** o bloco `canonical_sla` duplica parte do dict legado em `legacy_input.form_values`; em payloads muito grandes, o corpo HTTP para o Decision Engine cresce (mitigação futura: truncar ou referenciar hash — fora do âmbito desta fase).
- **Consumidores do DE:** se algum cliente assumir um schema fechado de `metadata`, campos novos podem ser ignorados (comportamento esperado em JSON aditivo).

### Status — preservado

**PASS** (implementação e testes locais no Git; **sem** build/deploy obrigatório desta fase e **sem** FASE 3 concluída).

---

## §12. FASE 3 — Backward compatibility / equivalence — **FAIL (2026-05-14 — runtime bloqueado pelo Portal)**

### Tentativa de validação runtime em `node006` (2026-05-14)

- **Script:** `docs/scripts/gsma_phase3_runtime_validate.sh` (port-forward `svc/trisla-portal-backend`, dois POSTs `/api/v1/sla/submit` consecutivos com o mesmo corpo `SLASubmitRequest`, captura kubectl, rollback YAML).
- **Evidência:** `evidencias_gsma_alignment_phase3_runtime_20260514T135710Z/` (sincronizada para o repositório local).
- **Resultado técnico:** **FAIL** — `kubectl port-forward` recusado: *pod is not running* / réplicas `trisla-portal-backend` em **Completed**, **Pending** ou **ContainerStatusUnknown** (ver `runtime/pods.txt`, `logs/port_forward.log`).
- **Nota de desenho:** o Portal só aceita `SLASubmitRequest`; o script compara **duas submissões consecutivas com o mesmo JSON** para equivalência operacional sob o mesmo contrato (não existe segundo endpoint “canónico” no submit).

### Registo obrigatório de execução (anti-improvisação)

- **Resultado:** **FAIL** (não se satisfazem os Mandatory Gates de equivalência **runtime**: decisão, score, XAI, orquestração, governação, assurance com prova de `curl` / pipeline completo).
- **Motivo (actualizado):** foi executado `ssh node006` e o script `docs/scripts/gsma_phase3_runtime_validate.sh`; o **port-forward para `trisla-portal-backend` falhou** porque não há pod **Running/Ready** por detrás do `Service` (réplicas Completed/Pending/Unknown — evidência em `evidencias_gsma_alignment_phase3_runtime_*/runtime/pods.txt`). Na primeira tentativa (workspace sem cluster), os compares estavam `NOT_EXECUTED` em `evidencias_gsma_alignment_phase3_20260514T134713Z/`.
- **Sub-resultado estrutural:** **PASS** parcial — `canonicalize_sla_request` preserva `legacy_input` de forma coerente com o legado; observação de código sobre `SLAEvaluateInput` documentada em `structural_equivalence.json` e `validation_report.md` (isto **não** substitui E2E).
- **Bloqueio:** **FASE 4–10 permanecem por executar** neste ciclo; **proibido** avançar FASE 4 sem **PASS** explícito da FASE 3 com evidência de runtime (Future Execution Contract).

### A. Objetivo científico

- Garantir que **todos** os `template_id` / `form_values` atuais produzem o mesmo comportamento observável (decisão, BC, SLA-Agent) dentro de tolerância documentada.

### B. Ficheiros permitidos / proibidos

| Pode alterar | Não pode alterar sem revisão explícita |
|--------------|----------------------------------------|
| Testes E2E/fixtures, scripts de bateria, docs de tolerância | Thresholds, pesos, scoring |

### C. Regras da fase

- Executar contra `node006` com digests registados.
- Nenhuma remoção de campos legados.

### D. Critérios PASS

- Matriz de templates × decisões × BC × SLA-Agent dentro da tolerância escrita **e** equivalência de decisão/score/XAI/orquestração/governance/assurance entre execução com e sem `canonical_sla` em metadados, **demonstrada** com artefactos JSON reais (não `NOT_EXECUTED`).

### E. Critérios FAIL

- Qualquer template suportado deixa de obter decisão/BC/agent equivalente **ou** ausência de prova runtime quando a fase foi declarada como tentativa de PASS completo.

### F. Evidências obrigatórias

- `evidencias_gsma_alignment_phase3_20260514T134713Z/` — apenas equivalência estrutural / `NOT_EXECUTED` nos compares runtime (workspace sem cluster).
- `evidencias_gsma_alignment_phase3_runtime_20260514T135710Z/` — tentativa **real** em `node006` (kubectl + artefactos); submits **não** executados por indisponibilidade do Portal.
- `evidencias_control_plane_portal_restore_20260514T143349Z/` — auditoria + recuperação (kubelet `node1`, `kube-controller-manager` na API, health HTTP 200; §12-J).
- Scripts: `docs/scripts/gsma_phase3_generate_evidence.py` (estrutural); `docs/scripts/gsma_phase3_runtime_validate.sh` (runtime em `node006`).

### G. Rollback

- N/A para código (nenhuma alteração de módulos do pipeline neste passo). **Reexecução:** apagar ou arquivar a pasta `evidencias_*` incorrecta e gerar nova com `TS` após E2E real.

### H. Dependências futuras

- **FASE 4** **bloqueada** até novo **PASS** da FASE 3 com evidência de cluster.

### I. Desbloqueio portal runtime (2026-05-14 — manhã) — **histórico**

- Registo da análise inicial: `DiskPressure` / taint em `node1`, `kubectl replace --force` do Deployment, ausência intermitente de `kube-controller-manager` na API e ReplicaSets órfãos — ver `evidencias_portal_runtime_unblock_20260514T143200Z/final_report.md`.
- **Actualização:** a sequência operacional **bem-sucedida** e o estado **actual** do portal após recuperação do plano de controlo estão em **§12-J** (`evidencias_control_plane_portal_restore_20260514T143349Z/`).

### J. Recuperação plano de controlo + kubelet (`node1`) — **2026-05-14 (infra OK; FASE 3 GSMA ainda FAIL)**

- **Auditoria:** `kubectl` via `node006`; manifests em `node1`; SSH a `node2` indisponível a partir do bastion (evidência `node2/ssh_unreachable.txt` no pacote).
- **Control plane (API):** `kube-controller-manager-node1` **Running** em `kube-system` (junto com `kube-apiserver-*`, `kube-scheduler-node1`); ver `validation/post_fix_snapshot.txt`.
- **Causa raiz (kubelet):** `/etc/kubernetes/kubelet.conf` em `node1` apontava **`https://192.168.10.15:6443`**; sob carga, **timeouts TLS** ao apiserver remoto impediam sincronização de **ConfigMaps/Secrets** — pods `trisla-portal-backend` presos em **ContainerCreating** (`Pulling` sem progresso aparente).
- **Correção mínima:** alterar o `server:` para **`https://127.0.0.1:6443`** (apiserver local em `node1`); backup **`/etc/kubernetes/kubelet.conf.bak.20260514T144912Z`**; `systemctl restart kubelet`. Detalhe: `node1/kubelet_api_endpoint_change.txt`.
- **Portal:** réplicas `app=trisla-portal-backend` em **Running** / **Ready** `1/1` (RS `868d57fc8`); `curl` a `http://127.0.0.1:18001/api/v1/health/global` via port-forward em `node006` → **HTTP 200** com JSON `status: unhealthy` (`validation/health_global.txt` — dependências de serviço, **não** usado como PASS GSMA).
- **Residual:** `Deployment.status.observedGeneration` pode permanecer desalinhado de `metadata.generation` (`collisionCount` observado); se persistir, **Helm upgrade --reuse-values** ou intervenção controlada no objecto — ver `final_report.md` do pacote.
- **Rollback kubelet:** `sudo cp /etc/kubernetes/kubelet.conf.bak.20260514T144912Z /etc/kubernetes/kubelet.conf && sudo systemctl restart kubelet` em `node1`.
- **FASE 3 GSMA:** **permanece FAIL** até nova execução **PASS** de `docs/scripts/gsma_phase3_runtime_validate.sh` com evidência; **permitido** re-tentar equivalência runtime real com o portal actual.

---

## §13. FASE 4 — Decision Engine alignment — **NOT_STARTED (bloqueada — depende de FASE 3 PASS)**

### A. Objetivo científico

- Consumir `service_requirements` canónicos onde existirem; manter leitura de dict legado.

### B. Ficheiros permitidos / proibidos

| Pode alterar | Não pode alterar |
|--------------|------------------|
| `apps/decision-engine/**` (roteamento de leitura de campos) | `decision_score_mode` fórmulas, thresholds, pesos |

### C. Regras da fase

- **Restrições explícitas:** **Não** alterar pesos, thresholds, nem fórmulas de `decision_score_mode`.

### D. Critérios PASS

- Equivalência de decisão em bateria de regressão (sem drift de score).

### E. Critérios FAIL

- Drift de score ou mudança de decisão explicada apenas por “leitura canónica”.

### F. Evidências obrigatórias

- Relatório de comparação antes/depois com os mesmos inputs.

### G. Rollback

- `git revert` + imagem digest anterior do DE.

### H. Dependências futuras

- **FASE 5** (XAI) pode depender da separação canónica vs semântica no DE.

---

## §14. FASE 5 — XAI alignment — **NOT_STARTED**

### A. Objetivo científico

- Separar causas canónicas vs semânticas na explicação (ex.: campos adicionais em `metadata` sem mudar scores).

### B. Ficheiros permitidos / proibidos

| Pode alterar | Não pode alterar |
|--------------|------------------|
| Camadas de apresentação XAI, metadata explicativa | Scoring, thresholds, pesos |

### C. Regras da fase

- Zero mudança numérica de decisão.

### D/E. PASS / FAIL

- PASS: XAI mais clara com mesmos scores.
- FAIL: qualquer alteração de score/threshold.

### F. Evidências

- Comparativo de strings/estruturas XAI antes/depois + mesmos números.

### G. Rollback

- Idem fases anteriores.

### H. Dependências futuras

- **FASE 8** (paper) beneficia desta separação.

---

## §15. FASE 6 — SLA-Agent alignment — **NOT_STARTED**

### A. Objetivo científico

- Rastrear canonical SLA + contratos de telemetria em ingest/revalidação onde aplicável.

### B. Ficheiros permitidos / proibidos

| Pode alterar | Não pode alterar |
|--------------|------------------|
| `apps/sla-agent-layer/**`, schemas de revalidação relacionados, docs de fase | Thresholds, pesos, scoring do DE; contratos de telemetria **removidos** em vez de estendidos |

### C. Regras da fase

- Alterações **aditivas** a estados/metadata de assurance; sem quebrar ingest existente.
- Revalidação temporal continua a respeitar o contrato `SLARevalidateTelemetryRequest` (Portal) sem exigir NASP/BC quando o schema diz que não aplica.

### D. Critérios PASS

- `sla_agent_status` e fluxos de revalidação documentados com payloads reais; `canonical_sla` visível nos pontos de log/metadata **apenas** se a fase decidir consumi-lo (opcional até aqui).

### E. Critérios FAIL

- Perda de rastreio de telemetria obrigatória ao contrato; regressão de `telemetry_complete` em cenários onde era true.

### F. Evidências obrigatórias

- `evidencias_gsma_alignment_phase6_<TS>/` com logs de agente, respostas de revalidação, e diff de metadata relevante.

### G. Rollback

- Reverter commits do SLA-Agent; `kubectl set image` para digest anterior do serviço afectado.

### H. Dependências futuras

- **FASE 7** (listings) pode referenciar assurance; **FASE 10** depende de baseline runtime completo.

---

## §16. FASE 7 — Listings update — **NOT_STARTED**

### A. Objetivo científico

- Actualizar Listing 1–3 (e derivados) para estrutura GSMA-aligned **com** valores de runtime real.

### B. Ficheiros permitidos / proibidos

| Pode alterar | Não pode alterar |
|--------------|------------------|
| Listings LaTeX/Markdown, figuras derivadas, `docs/paper/**` conforme política do repo | Números de listings congelados sem novo E2E e sem FASE 8/9 quando exigido |

### C. Regras da fase

- Valores **reais** de runtime (referência a `evidencias_*` com timestamps); proibir números “ilustrativos” sem fonte.

### D. Critérios PASS

- Listings 1–3 (e derivados acordados) actualizados com labels *legacy* / *canonical* / *semantic* onde aplicável.

### E. Critérios FAIL

- Listings que contradizem o runbook ou o código sem explicação de versão/commit.

### F. Evidências obrigatórias

- `evidencias_gsma_alignment_phase7_<TS>/` com PDF/LaTeX build log ou equivalente e pointers para freezes.

### G. Rollback

- Reverter commits de listings; restaurar pacote de listings anterior no repositório de dissertação.

### H. Dependências futuras

- **FASE 8** valida narrativa científica dos listings; **FASE 10** pode congelar listings finais.

---

## §17. FASE 8 — Paper validation — **NOT_STARTED**

### A. Objetivo científico

- Coerência Secção IV, GSMA/3GPP (no sentido editorial), dissertação, runtime.

### B. Ficheiros permitidos / proibidos

| Pode alterar | Não pode alterar |
|--------------|------------------|
| Texto da dissertação/paper, tabelas de mapeamento, `docs/**` relevantes | Afirmações de certificação GSMA/TMF/NWDAF sem evidência externa |

### C. Regras da fase

- Usar apenas vocabulário **GSMA-aligned** no sentido do §1.5; distinguir sempre runtime observado vs alvo canónico.

### D. Critérios PASS

- Secção IV (ou equivalente) reconciliada com runbook + evidências; revisão por checklist do §25.

### E. Critérios FAIL

- Mistura de *canonical* e *semantic* sem rótulos; “API dump” sem ancoragem em ficheiro/commit.

### F. Evidências obrigatórias

- `evidencias_gsma_alignment_phase8_<TS>/` com PDF da revisão, comentários resolvidos, e lista de commits referenciados.

### G. Rollback

- Reverter alterações de texto para commit de paper anterior; manter rascunhos fora do branch principal se necessário.

### H. Dependências futuras

- **FASE 9** valida que o texto não promete capacidades inexistentes no runtime; **FASE 10** congela pacote final.

---

## §18. FASE 9 — E2E validation (node006) — **NOT_STARTED**

### A. Objetivo científico

- Fluxo completo com digest GHCR no laboratório:

`semantic SLA request → SEM-CSMF → ML-NSMF → DE → NASP → BC-NSMF → SLA-Agent`

### B. Ficheiros permitidos / proibidos

| Pode alterar | Não pode alterar |
|--------------|------------------|
| Scripts de teste, relatórios de evidência | Estados PASS de fases anteriores sem evidência nova |

### C. Regras da fase

- `ssh node006` conforme política do laboratório; digests via `skopeo inspect`; **nunca** `:latest` como prova científica.

### D. Critérios PASS

- Gates mínimos abaixo satisfeitos **e** documentados no pacote de evidência.

### E. Critérios FAIL

- Qualquer gate abaixo falha sem explicação registada e plano de rollback.

### F. Evidências obrigatórias

- `evidencias_gsma_alignment_e2e_<TS>/` com `final_response.json`, manifests de digest, logs relevantes.

### G. Rollback

- `kubectl set image …@sha256:<anterior>` por serviço afectado.

### H. Dependências futuras

- **FASE 10** congela o que a FASE 9 provou.

### Gates mínimos — conteúdo preservado da v0.1

- `decision`: ACCEPT (cenário de teste acordado)
- `bc_status`: COMMITTED ou REGISTERED
- `tx_hash` ≠ null, `block_number` ≠ null
- `sla_agent_status`: OK
- `telemetry_complete`: true (quando aplicável)

---

## §19. FASE 10 — Scientific freeze — **NOT_STARTED**

### A. Objetivo científico

- Pacote `evidencias_gsma_alignment_final_<TS>/` com manifest, digests, relatório de validação, listings finais.

### B. Ficheiros permitidos / proibidos

| Pode alterar | Não pode alterar |
|--------------|------------------|
| Manifest de freeze, índice de evidências, `README` do pacote final | Conteúdo de evidências já congeladas (não editar; criar novo `TS`) |

### C. Regras da fase

- Imutabilidade lógica do pacote: cópias WORM ou política de “append-only” no storage do laboratório.

### D. Critérios PASS

- `evidencias_gsma_alignment_final_<TS>/` contém manifest (digests, SHAs de ficheiros), relatório de validação, e pointers para listings.

### E. Critérios FAIL

- Freeze sem digest ou sem `final_response.json` de referência quando o cenário exige E2E.

### F. Evidências obrigatórias

- O próprio pacote `evidencias_gsma_alignment_final_<TS>/` **é** a evidência; duplicar metadados no runbook (caminho + data).

### G. Rollback

- Não “descongelar”; abrir nova linha temporal `final_<TS2>/` se necessário corrigir.

### H. Dependências futuras

- Trabalhos pós-freeze exigem **nova** linha de fases ou addendum ao runbook (§27).

### Status — preservado

**NOT_STARTED**

---

## §20. Mandatory Gates

| Gate | Quando é obrigatório | Falha implica |
|------|----------------------|----------------|
| `py_compile` | Qualquer fase com alteração de código Python tocada | FAIL até corrigir sintaxe |
| Testes unitários / integração locais | Quando a fase os definir (ex.: FASE 2) | FAIL de fase |
| E2E laboratório | FASE 9 e qualquer release que declare equivalência runtime | FAIL de release |
| `decision` = ACCEPT | Cenário de baseline acordado | FAIL ou cenário inválido |
| BC COMMITTED / REGISTERED | Quando BC está no caminho | FAIL de governação |
| `tx_hash` | Presença quando BC aplicável | FAIL de evidência |
| `block_number` | Presença quando BC aplicável | FAIL de evidência |
| SLA-Agent OK | Quando assurance faz parte do cenário | FAIL de assurance |
| `telemetry_complete` | Quando telemetria faz parte do cenário | FAIL de completude |
| Sem mudança de thresholds | Todas as fases deste runbook até decisão explícita em contrário | FAIL arquitectural |
| Sem score drift | Fases 3–5 e releases científicos | FAIL de regressão |

---

## §21. Scientific Validation Rules

### Equivalência

- **Definição operacional:** dois runs são equivalentes se **decisão**, **scores expostos** (se presentes), **metadata de orquestração relevante**, **tx_hash** (se BC), e **SLA-Agent** coincidem dentro da tolerância documentada na FASE 3.

### Comparação de payloads

- Usar diff estrutural (ex.: `jq` + sort keys) com normalização de timestamps; **nunca** ignorar campos de governação.

### Comparação de decisões e scores

- Comparar primeiro a decisão categórica; depois números (`confidence`, componentes se expostos); qualquer delta exige explicação **não** atribuível a thresholds/pesos.

### XAI

- Validar que strings/estruturas de explicação referenciam inputs reais (sem hallucinação de campos inexistentes no payload).

### Orchestration e governance

- Validar `nasp_orchestration_*` / campos equivalentes só contra o que o código em `apps/portal-backend/src/services/nasp.py` e adapter realmente suportam.

### Runtime assurance

- Validar `sla_agent_status`, revalidação e snapshots de telemetria contra o contrato `telemetry_contract_version` vigente no commit referenciado.

---

## §22. Runtime Evidence Model

| Artefacto | Significado | Onde aparece tipicamente |
|-----------|-------------|---------------------------|
| `telemetry_snapshot` | Captura agregada para DE / metadata | Portal → SEM / DE metadata |
| `t0` / `t1` | Marcas temporais de fase (admission, interpret) | Respostas Portal / logs |
| Lifecycle metadata | Estado do ciclo de SLA | `SLASubmitResponse`, metadata DE |
| Orchestration metadata | Tentativa/resultado NASP | `metadata` unificado Portal |
| Governance metadata | BC tx, block | `tx_hash`, `block_number` |
| Runtime assurance metadata | SLA-Agent, `telemetry_complete` | `SLASubmitResponse` |

**Regra:** não apagar estes campos do modelo de evidência científica; evoluções são **aditivas**.

---

## §23. Deployment Rules

1. **Laboratório node006:** acesso via `ssh node006` apenas quando a política institucional o permitir; sempre registar quem, quando, e qual digest.
2. **GHCR:** imagens referenciadas por **digest** (`skopeo inspect docker://…@sha256:…` ou tag resolvida para digest).
3. **Nunca** usar `:latest` como prova científica de reproducibilidade.
4. **Rollout:** `kubectl set image deployment/<svc> <ctr>=registry/image@sha256:…`.
5. **Rollback:** `kubectl set image` para digest anterior; manter manifest com ambos.
6. **Scientific freeze:** pacote imutável `evidencias_gsma_alignment_final_<TS>/` com manifest de digests e hashes de ficheiros.

---

## §24. Forbidden Changes

| Proibição | Motivo |
|-----------|--------|
| Alterar thresholds | Invariante de scoring científico |
| Alterar pesos | Idem |
| Alterar scoring / `decision_score_mode` fórmulas | Fora do âmbito salvo programa explícito |
| Alterar datasets históricos in-place | Perde cadeia científica |
| Invalidar ou apagar evidências congeladas | Impede auditoria |
| Remover payload legado (`template_id`, `form_values`) | Viola §6 |
| Remover metadata antiga necessária a XAI/orquestração | Regressão de explicabilidade |
| Remover `tx_hash` / lifecycle BC da narrativa de resultados | Regressão de governação |
| Remover `telemetry_snapshot` quando o contrato exige | Regressão de multidomain |
| Inventar conformidade GSMA | Viola §1.5 |
| Inventar suporte TMF, NWDAF, ou orquestração inexistente | Anti-invenção; só o que está no código + docs do repo |

---

## §25. Paper Alignment Rules

### Secção IV (dissertação / paper)

- Deve distinguir claramente: **(i)** pipeline observado no laboratório, **(ii)** modelo de dados legado, **(iii)** modelo canónico alvo, **(iv)** limitações (sem certificação GSMA).
- Usar vocabulário **GSMA-aligned** apenas no sentido editorial deste runbook.

### Canonical vs semantic

- Tabelas e figuras devem etiquetar dados como *legacy flat*, *canonical service requirements*, ou *semantic context* — nunca misturar sem rótulo.

### Listings

- Listings devem refletir **código ou payloads reais** congelados; evitar “pseudo-code JSON” que não exista no repositório.

### Evitar “custom JSON” pejorativo sem nuance

- O legado é “flat JSON”; o paper deve explicar **porque** surgiu e **como** o canónico ajuda, sem desvalorizar o que foi validado cientificamente.

### Evitar “API dump”

- Não colar OpenAPI inteiro como resultado científico; usar excertos mínimos com referência a ficheiro e commit.

### Estilo NASP-level

- Descrever interfaces e responsabilidades com a mesma precisão que em documentação de integração enterprise: contrato, erro, retry, idempotência — **só** onde for factual no código.

---

## §26. Checklist obrigatório antes de cada alteração de código

- [ ] Li a secção da fase neste runbook (§9–§19 conforme fase).
- [ ] Confirmei baseline, gates (§20) e rollback (fase correspondente).
- [ ] Não alterei thresholds nem pesos nem fórmulas de scoring.
- [ ] Actualizei este runbook com ficheiros tocados, digest (se deploy), e resultado PASS/FAIL.
- [ ] Anexei ou referenciei evidências em `evidencias_gsma_alignment_*` sem apagar freezes anteriores.
- [ ] Não introduzi integrações ou conformidades não suportadas pelo repositório (§24).

---

## §27. Future Execution Contract

1. **Qualquer alteração** ao pipeline GSMA-aligned **deve** começar pela leitura deste runbook e pela identificação da **fase** correspondente.
2. **Qualquer nova fase** (ex.: 11+) **deve** ser adicionada a este documento com o mesmo esqueleto A–H antes da execução.
3. **Nenhum deploy** que afecte o baseline científico **pode** ocorrer sem actualização do runbook (data, digest, resultado).
4. **Nenhuma evidência** congelada pode ser descartada; apenas arquivar com novo `TS` se necessário.
5. **Qualquer FAIL** de gate obrigatório **interrompe** o avanço de fases até resolução ou rollback explícito.
6. **Qualquer regressão** comprovada exige **rollback** de código e/ou imagem e registo no histórico (§28).
7. **Chats / LLMs** não são fonte de verdade: apenas este runbook + commits + evidências em disco.

---

## §28. Histórico de alterações do runbook

| Data | Autor | Alteração |
|------|-------|-----------|
| 2026-05-14 | Cursor | Criação inicial: FASE 0–1 PASS (auditoria repo + `TRISLA_CANONICAL_SLA_MODEL.md`); FASE 2–10 NOT_STARTED |
| 2026-05-14 | Cursor | FASE 2 PASS (canonicalização SEM-CSMF + evidências `evidencias_gsma_alignment_phase2_20260514T130000Z/`); actualização do quadro de fases |
| 2026-05-14 | Cursor | FASE 3 runtime **FAIL** em `node006`: evidências `evidencias_gsma_alignment_phase3_runtime_20260514T135710Z/`; `trisla-portal-backend` sem pod Ready (port-forward falhou); script `docs/scripts/gsma_phase3_runtime_validate.sh`; **FASEs 4–10** continuam bloqueadas |
| 2026-05-14 | Cursor | Desbloqueio portal **FAIL (infra)**: `evidencias_portal_runtime_unblock_20260514T143200Z/` — mitigação de disco/taints em `node1`; bloqueio actual: **sem `kube-controller-manager` na API**, ReplicaSets do portal não criados; §12-I; FASE 3 continua **FAIL** |
| 2026-05-14 | Cursor | Recuperação CP + kubelet `node1` (`kubelet.conf` → `https://127.0.0.1:6443`); `kube-controller-manager-node1` na API; portal **Running/Ready**; health **HTTP 200** (`evidencias_control_plane_portal_restore_20260514T143349Z/`); §12-J; **FASE 3 GSMA** mantém-se **FAIL** até script runtime PASS |

**Fim do documento SSOT (v0.2).**
