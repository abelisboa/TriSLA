# TriSLA - Architecture & Prototype Evidence (SSOT)

## 1. Arquitetura e Mapeamento 3GPP

### Mapeamento validado (implementacao observada)
- CSMF -> `sem-csmf`
- NSMF -> `ml-nsmf` + `decision-engine`
- NSSMF -> `nasp-adapter` + `bc-nssmf`

Evidencias (codigo/repositorio):
- `apps/sem-csmf/src/main.py` (`module: sem-csmf`)
- `apps/ml-nsmf/src/main.py` (`module: ml-nsmf`)
- `apps/decision-engine/src/main.py` (`/evaluate`)
- `apps/nasp-adapter/src/main.py` (`/api/v1/nsi/instantiate`, `/api/v1/3gpp/gate`)
- `apps/bc-nssmf/src/main.py` (`/api/v1/register-sla`, `tx_hash`, `block_number`)

---

## 2. Cadeia SLA (Formalizacao observada)

Pipeline funcional identificado:
- `POST /api/v1/sla/submit` no `portal-backend`
- chamada para NASP orchestration (`nasp_service.submit_template_to_nasp`)
- enriquecimento por telemetria (`telemetry_snapshot`)
- retorno com decisao e metadados
- tentativa de registro blockchain (`tx_hash`, `block_number`) quando aplicavel

Evidencias:
- `apps/portal-backend/src/routers/sla.py`
- `apps/portal-backend/src/services/nasp.py`
- `apps/portal-backend/src/schemas/sla.py`
- `apps/bc-nssmf/src/main.py`

---

## 3. Sequencia Operacional (base para figura)

Sequencia real detectada:

User/Portal -> SEM-CSMF -> ML-NSMF -> Decision Engine -> NASP Adapter -> Network/Infra -> Telemetry (Prometheus) -> Decision metadata -> BC-NSSMF -> SLA Agent Layer

---

## 4. Interfaces TriSLA (inferidas)

- SI: Portal -> SEM (`/interpret`, `/submit`)
- MI: SEM -> ML/Decision (via fluxo backend/services)
- DI: Decision endpoint (`/evaluate`)
- NI: Decision/Portal -> NASP (`/api/v1/nsi/instantiate`)
- TI: Network telemetry -> Decision context (`telemetry_snapshot`)
- GI: Decision/Portal -> Blockchain (`tx_hash`, `block_number`)

---

## 5. Closed Loop

Implementado via:
- `metadata.telemetry_snapshot`
- consultas Prometheus (SSOT em `apps/portal-backend/src/telemetry/promql_ssot.py`)

### 5.1 Fechamento temporal mínimo (P0→P2), congelado

Além do snapshot de telemetria na decisão, o **portal-backend** expõe uma cadeia **observacional** (sem enforcement automático nem orquestração de remediação no runtime desta fase):

| Peça | Onde | Papel |
|------|------|--------|
| `metadata.temporal_intent_trace` | Resposta `POST /api/v1/sla/submit` | Correlação de `intent_id`, `execution_id`, marcas temporais e lifecycle (P0). |
| `drift_summary` | Resposta `POST /api/v1/sla/revalidate-telemetry` | Deltas numéricos entre `reference_telemetry_snapshot` e nova leitura Prometheus (P1). |
| `metadata.remediation_evidence` | Mesma resposta do revalidate | Recomendação declarativa apenas: `recommendation`, `severity`, `affected_domains`, `suggested_action`, `revalidation_required` (P2). |

**Freeze consolidado da cadeia:** `TEMPORAL_CLOSED_LOOP_P0_P2_FREEZE`  
**Documentação operacional:** `docs/TRISLA_MASTER_RUNBOOK.md` (secção Closed-loop temporal), `analysis/CLOSED_LOOP_P0_P2_FINAL_STATUS.md`, `analysis/RUNTIME_TEMPORAL_FEATURES.md`

Evidencias (código):
- `apps/portal-backend/src/telemetry/collector.py`
- `apps/portal-backend/src/telemetry/promql_ssot.py`
- `apps/portal-backend/src/routers/sla.py` (`submit`, `revalidate_telemetry`, helpers de drift e remediation evidence)
- `apps/portal-backend/src/schemas/sla.py` (`SLARevalidateTelemetryRequest` / `Response`)
- `apps/decision-engine/src/engine.py` (consumo de `telemetry_snapshot`)

Nota:
- NWDAF nao aparece como modulo dedicado no runtime avaliado; inferencia operacional ocorre via telemetria + regras/modelo.
- P2 **não** implementa execução automática de remediação, callback NASP dedicado, Kafka obrigatório, scheduler nem armazenamento externo de evidências.

---

## 6. Prototipo Real (runtime)

### Kubernetes (`kubectl -n trisla get deploy`)
- `kafka`
- `trisla-bc-nssmf`
- `trisla-decision-engine`
- `trisla-decision-engine-trisla`
- `trisla-ml-nsmf`
- `trisla-nasp-adapter`
- `trisla-portal-backend`
- `trisla-portal-backend-trisla`
- `trisla-sem-csmf`
- `trisla-sem-csmf-trisla`
- `trisla-sla-agent-layer`
- (e demais servicos de suporte)

### RAN / Transport / Core (evidencia de ambiente real)
- ONOS: `nasp-transport/onos-*` Running
- Mininet: processo `python3 /tmp/mininet-fase2.py` + shells `mininet:*`
- Core 5G (free5GC namespace): `amf`, `smf`, `upf` Running em `ns-1274485`

---

## 7. Reprodutibilidade (estado atual observado)

- CORE em GHCR + digest: **sim (no escopo CORE definido)**  
- Sem v1/v2: **nao** (existem variantes paralelas em outros fluxos/campanhas)  
- Dataset canonizado unico: **parcial** (ha multiplos datasets finais no workdir)  
- Execution trace (`execution_id`/telemetry): **sim** no fluxo principal

---

## 8. Gaps remanescentes

- Consolidar texto formal da cadeia SLA em um unico bloco "canonical architecture".
- Produzir figura de sequencia NASP-ready baseada na cadeia validada acima.
- Congelar baseline operacional sem variantes paralelas (ou delimitar escopo estrito de experimento).
- Consolidar dataset canonico unico para campanha cientifica.

---

## 9. Conclusao

TriSLA apresenta:
- Arquitetura 3GPP funcionalmente mapeavel
- Pipeline E2E implementado (SEM/ML/Decision/NASP/BC/Agent)
- Prototipo real em Kubernetes com evidencias de RAN/Transport/Core

Status para "Architecture & Prototype" de nivel journal:
- **tecnicamente forte**, com **gaps de consolidacao/reprodutibilidade formal** ainda necessarios para afirmacao "100% pronto" sem ressalvas.
