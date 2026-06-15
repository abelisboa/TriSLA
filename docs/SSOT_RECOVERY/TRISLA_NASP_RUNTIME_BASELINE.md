# TriSLA — NASP runtime baseline (SSOT recovery pack)

**Documento:** `docs/SSOT_RECOVERY/TRISLA_NASP_RUNTIME_BASELINE.md`  
**Data:** 2026-05-13  
**Modo:** derivado de `docs/TRISLA_MASTER_RUNBOOK.md`, `docs/TRISLA_INFRA_SSOT.md`, `docs/TRISLA_E2E_FLOW_CANONICAL.md`, `docs/TRISLA_ARCHITECTURE_EVIDENCE_PATCHED.md`, `docs/modules/*.md`, `docs/RECOVERED/PROMPTS/*`, e evidência runtime `evidencias_nasp_alignment/fase1_runtime/pods.txt` (captura via `ssh node006`).

**Nota R2:** Pastas nomeadas `evidencias_baseline_oficial/`, `evidencias_metricas_operacionais/`, `evidencias_gnb_real/` não estão presentes neste checkout; caminhos de dataset referidos em `docs/TRISLA_ARCHITECTURE_EVIDENCE_PATCHED.md` aplicam-se a clones/pacotes onde existam.

---

## (1) Arquitetura oficial congelada

- **Orquestração lógica:** Portal Backend (ingresso) → SEM-CSMF → ML-NSMF → Decision Engine (autoridade decisão/orquestração/lifecycle/governance conforme FASES 3–4) → NASP Adapter (execução `nsi/instantiate`) → BC-NSSMF + Besu (governance) → SLA-Agent (revalidate) — ver `docs/TRISLA_E2E_FLOW_CANONICAL.md` (bloco pós-refatoração 2026-05-11).
- **Domínio de execução:** RAN / TRANSPORT / CORE descritos como camada fora do submit síncrono; integração transporte NASP com `ENABLE_TRANSPORT` referida no E2E canónico.
- **NASP published architecture:** o repositório não substitui o documento externo do NASP; o **modelo validado** aqui é o **comportamento publicado pelo código + runbook** (`NASPService`, rotas SLA, adapter).

## (2) Componentes autorizados (baseline NASP-aligned)

| Papel | Componente | Evidência |
|--------|------------|-----------|
| RAN (carga / slice core) | **my5G-RANTester** (`rantester-0` em `ns-1274485`) | `evidencias_nasp_alignment/fase1_runtime/pods.txt` |
| Core | **free5GC** (AMF/SMF/UPF/NRF/UDM/UDR/… em `ns-1274485`) | idem |
| Transporte alvo | **ONOS** + **Mininet** (namespace `nasp-transport`) | idem |
| Observabilidade | **Prometheus** (stack `monitoring`) | idem |
| Orquestração TriSLA | **NASP Adapter** + serviço NASP no portal | `docs/TRISLA_ARCHITECTURE_EVIDENCE_PATCHED.md` |
| Governance | **BC-NSSMF** + **Hyperledger Besu** | idem + pods `trisla-besu`, `trisla-bc-nssmf` |
| Runtime assurance | **SLA-Agent Layer** | idem |
| Stack TriSLA control plane | portal-backend, sem-csmf, ml-nsmf, decision-engine, … | runbook + `docs/modules/*.md` |

## (3) Componentes laboratoriais / paralelos

- **`trisla-prb-simulator`:** exporta `trisla_ran_prb_utilization` (Gauge); **não** é SSOT científico para RAN real — ver política anti-regressão abaixo e `docs/AUDITORIA_PROMPT05_RAN_PRB_PIPELINE.md`.
- **`trisla-ran-ue-upf-proxy`:** derivador PRB a partir de métricas de rede; prioridade SEM-CSMF (PROMPT_116) documentada em `apps/sem-csmf/src/decision_engine_client.py`.
- **UERANSIM, srsRAN (`srsenb`, `ran-prb-exporter`), NONRTRIC:** coexistem no cluster; tratados como **laboratório / paralelo** salvo decisão explícita de baseline no Capítulo IV.
- **Deployments `*-trisla`:** variantes paralelas (portal-backend-trisla, decision-engine-trisla, …) — `docs/TRISLA_ARCHITECTURE_EVIDENCE_PATCHED.md` §Gaps.

## (4) Workflow E2E oficial

Ordem e contratos: `docs/TRISLA_E2E_FLOW_CANONICAL.md` — tabela pós-refatoração (FASE 7 precedência), entrypoint `POST /api/v1/sla/submit`, delegação `revalidate-telemetry` ao SLA-Agent com fallback in-process.

## (5) Origem oficial de telemetria RAN (nome de série)

- **Métrica canónica:** `trisla_ran_prb_utilization` (Prometheus).
- **PromQL SSOT portal/sla-agent revalidate:** `avg(trisla_ran_prb_utilization{job="trisla-ran-ue-upf-proxy"})` — `apps/portal-backend/src/telemetry/promql_ssot.py`, `apps/sla-agent-layer/src/revalidate/promql_ssot.py`.
- **Resumo / throughput slice:** queries em `PROMQL_SUMMARY` com `namespace="ns-1274485"` e `pod=~"rantester.*"` — mesmo ficheiro.
- **Consumo Decision Engine:** `telemetry_snapshot.ran.prb_utilization` — `apps/decision-engine/src/main.py`.

## (6) Interfaces válidas (HTTP)

Tabela resumida em `docs/TRISLA_ARCHITECTURE_EVIDENCE_PATCHED.md` §1 (interpret, submit, sem interpret/intents, adapter instantiate, DE evaluate, prometheus proxy, sla-agent ingest/revalidate).

## (7) Namespaces válidos (snapshot 2026-05-13)

- **`trisla`:** módulos TriSLA.
- **`ns-1274485`:** free5GC + **rantester** (baseline RANTester/free5GC).
- **`monitoring`:** Prometheus stack.
- **`nasp-transport`:** ONOS / Mininet.
- **`ueransim`, `srsran`, `nonrtric`, `ran-test`:** laboratório / O-RAN — classificação em `evidencias_nasp_alignment/fase1_runtime/runtime_classification.md`.

## (8) PromQL SSOT

| Chave | Expressão |
|--------|-----------|
| RAN_PRB | `avg(trisla_ran_prb_utilization{job="trisla-ran-ue-upf-proxy"})` |
| RAN_LATENCY | `avg(trisla_ran_latency_ms)` |
| ran_prb_instant | `trisla_ran_prb_utilization` |

Variantes documentadas em manifests embutidos em `docs/TRISLA_INFRA_SSOT.md` (filtrar por `job="trisla-prb-simulator"` vs `job!="trisla-prb-simulator"`) — risco de **cérebro duplo** entre deployments; não inventar novas queries sem auditoria.

## (9) Política de deploy

- **Digest-only GHCR:** `docs/TRISLA_MASTER_RUNBOOK.md` (bloco FASE 6–7); proibido `:latest` em baseline congelado.
- **SSH:** operações de cluster via **`ssh node006`** (regra operacional do projeto).

## (10) Regras anti-regressão

1. Não remover fallbacks documentados no runbook (revalidate in-process, legacy orchestrate, BC degraded, …).
2. Não alterar schema `SLASubmitResponse` / contratos metadata sem E2E.
3. **Simulador PRB não é SSOT** para baseline científico NASP-aligned: baseline RAN = **rantester + free5GC**; simulador apenas laboratório controlado.
4. Qualquer mudança de PromQL ou prioridade SEM-CSMF (`SEM_PRB_JOB_PRIORITY`) exige evidência antes/depois e teste de instant query por `job`.
5. Não reintroduzir média global sem `job` na expressão SSOT do portal (ver `TRISLA_RAN_SSOT_POLICY.md`).

## (11) Sequência oficial do workflow

Ver §4 e diagrama ASCII em `docs/TRISLA_E2E_FLOW_CANONICAL.md`.

## (12) Serviços obrigatórios (mínimo lógico submit)

Portal-backend, SEM-CSMF, ML-NSMF, Decision Engine, NASP Adapter, BC-NSSMF, Besu (governance), Prometheus (telemetria); SLA-Agent conforme política `SLA_AGENT_REQUIRED_FOR_ACCEPT`.

## (13) Dependências runtime

- kube-prometheus em `monitoring`.
- Core namespace ativo para `container_*` / deteção: script `scripts/detect_core_namespace.sh` (runbook).
- Kafka / OTEL / Tempo conforme deployments `trisla` (observabilidade estendida).

## (14) Regras de validação

- Health: `GET /api/v1/health/global` (portal-backend) — ver runbook (port-forward).
- PRB: instant query Prometheus com discriminação por `job`.
- Core: UPF Running no namespace detetado.

## (15) Fluxo Decision Engine

SEM-CSMF chama `POST …/evaluate`; entrada inclui `telemetry_snapshot`; PRB logado — `apps/decision-engine/src/main.py` + `docs/modules/decision-engine.md`.

## (16) Fluxo NASP Adapter

Portal executa `POST …/api/v1/nsi/instantiate` quando fluxo ACCEPT e políticas de authority — `apps/portal-backend/src/services/nasp.py`, `docs/modules/nasp-adapter.md`.

## (17) Fluxo BC-NSSMF

Registo pós-orquestração; campos `tx_hash`, `block_number`, `governance_registration` — runbook + `docs/modules/bc-nssmf.md`.

## (18) Fluxo SLA-Agent

`POST /api/v1/agent/revalidate-telemetry`; portal delega — `docs/modules/sla-agent-layer.md`, E2E canónico.

## (19) Fluxo revalidation

Portal `POST /api/v1/sla/revalidate-telemetry` → SLA-Agent; metadata `delegated_to_sla_agent`, `delegation_fallback_reason` — E2E + runbook FASE 6 PASSO 10.

## (20) Limitações conhecidas

- **Transporte:** Mininet em `Error` no snapshot; ONOS parcialmente saudável — `pods.txt`.
- **PRB multi-fonte:** proxy + simulador + (opcional) NASP gauge — média `avg()` dilui sinal; SEM prioriza proxy e aceita `0.0` como valor válido (ver `evidencias_nasp_alignment/fase2_prb/prb_lineage.md`).
- **UERANSIM `trisla-gtp-endpoint`:** pod em `Error` no snapshot.
- **Variantes `*-trisla`:** risco de configuração divergente (PromQL por deployment).
- **Evidências congeladas R2:** nem todos os pacotes `evidencias_*` listados na arquitetura existem neste workspace.

---

**Referências explícitas exigidas pelo prompt:** NASP (modelo código+runbook), **my5G-RANTester**, **ONOS**, **Mininet**, **free5GC**, **Prometheus**, **Besu**, **NASP Adapter** — todas discriminadas acima.
