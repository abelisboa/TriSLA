# REFACTOR_TRISLA_RESPONSIBILITY_GUIDE.md

> Guia obrigatório de re-arquitetura operacional TriSLA (REGRA ZERO do PROMPT MASTER).
> Nenhuma alteração de código pode começar antes deste documento existir e ser revisado.
>
> **Autor da execução:** DevOps Sênior + Engenheiro de IA + Arquiteto (sessão automatizada).
> **Modo:** evidence-first, faseado, deploy somente por digest remoto GHCR.
> **Entrypoint operacional obrigatório:** `ssh node006` → `cd /home/porvir5g/gtp5g/trisla`.
> **Namespace:** `trisla`.

---

## 0. Sumário executivo

O Portal Backend está concentrando hoje responsabilidades que pertencem a outros componentes do TriSLA:
orchestration trigger, lifecycle registration, runtime telemetry reassessment, geração de `drift_summary` e
geração de `remediation_evidence`. O Decision Engine está limitado a decisão/score/policy/risk. O SLA-Agent
existe como *layer* Kafka-driven (`apps/sla-agent-layer`), porém **não tem endpoint operacional** para
revalidação de runtime, conforme auditoria `evidencias_auditoria_responsabilidades_20260511T190246Z`
(arquivo `sla_agent/runtime_logic.txt` vazio).

Esta refatoração move cada responsabilidade ao componente correto **sem regressão de endpoints públicos** e
**sem alterar contrato JSON** das respostas — apenas adicionando metadados de delegação
(`delegated_to_sla_agent`, `decision_engine_orchestration_authority`, etc.).

Critério de sucesso global:

- `/api/v1/sla/submit` (eMBB, URLLC, mMTC) responde com o **mesmo contrato JSON** atual.
- `/api/v1/sla/revalidate-telemetry` responde com o **mesmo contrato JSON** atual.
- `drift_summary`, `remediation_evidence`, `lifecycle_state`, `tx_hash`,
  `nasp_orchestration_status`, `decision_score`, `reason_codes`, `telemetry_snapshot` preservados.
- Deploy de cada serviço alterado por **digest remoto GHCR** (jamais `:latest`, jamais por tag).

---

## 1. Diagnóstico da situação atual

### 1.1 Componentes em execução (baseline `kubectl -n trisla get deployments`)

| Deployment                       | Replicas | Imagem (digest curto) |
|----------------------------------|---------:|-----------------------|
| `trisla-portal-backend`          |    3/3   | `…@sha256:80dbb977…316e6a` |
| `trisla-portal-backend-trisla`   |    1/1   | `…@sha256:2961a3eb…cbae7d` |
| `trisla-decision-engine`         |    2/2   | `…@sha256:d5fe0b8a…04d28`  |
| `trisla-decision-engine-trisla`  |    1/1   | `…@sha256:2ba19ee1…d8c31f` |
| `trisla-sla-agent-layer`         |    1/1   | `…@sha256:397fef29…83f9f3` |
| `trisla-nasp-adapter`            |    1/1   | `…@sha256:063bddea…b02d79` |
| `trisla-bc-nssmf`                |    1/1   | `…@sha256:b0db5eef…f9f95a` |
| `trisla-sem-csmf`                |    1/1   | `…@sha256:81ac156c…04d1d`  |
| `trisla-ml-nsmf`                 |    1/1   | `…@sha256:0e6f1494…ace3e`  |

(snapshot completo: `evidencias_refactor_responsabilidades_<TS>/baseline/images.txt`).

Existem dois “tracks” paralelos para alguns serviços (`*-trisla` e o canônico). A refatoração **só** mexe nas
réplicas canônicas (`trisla-portal-backend`, `trisla-decision-engine`, `trisla-sla-agent-layer`,
`trisla-bc-nssmf`). Os “*-trisla” seguem congelados como histórico até checkpoint final.

### 1.2 Onde estão as responsabilidades hoje (evidências reais do código)

Auditoria pré-existente: `evidencias_auditoria_responsabilidades_20260511T190246Z`.

- **Portal Backend** (`apps/portal-backend/src/`)
  - `routers/sla.py` expõe `POST /api/v1/sla/submit` (linha 535) e
    `POST /api/v1/sla/revalidate-telemetry` (linha 874).
  - `routers/sla.py:288` define `_build_remediation_evidence_p2` → **Portal Backend é autoridade
    de `remediation_evidence`**.
  - `routers/sla.py:913` chama `_minimal_telemetry_drift` → **Portal Backend é autoridade
    de `drift_summary`**.
  - `routers/sla.py:700..795` constrói lifecycle (`ORCHESTRATION_REQUESTED`, `ORCHESTRATION_FAILED`,
    `lifecycle_state`) → **Portal Backend é autoridade de lifecycle**.
  - `services/nasp.py:180-290` executa orquestração no NASP Adapter e popula
    `nasp_orchestration_status` → **Portal Backend dispara orquestração**.
  - `telemetry/collector.py` + `telemetry/promql_ssot.py` consultam Prometheus diretamente → **Portal
    Backend é cliente direto de telemetria**.

- **Decision Engine** (`apps/decision-engine/src/`)
  - `engine.py`, `decision_score_mode.py`, `service.py` — fazem decisão, score contínuo, policy hard
    (reject/renegotiate), thresholds.
  - `nasp_adapter_client.py` existe mas **não dispara** trigger de orquestração no fluxo atual de submit.
  - Não emite `orchestration_payload` autoritativo.

- **SLA-Agent Layer** (`apps/sla-agent-layer/src/`)
  - Componentes presentes: `agent_core.py`, `agent_coordinator.py`, `slo_evaluator.py`,
    `domain_compliance.py`, `domain_snapshot.py`, `kafka_consumer.py`, `kafka_producer.py`,
    `system_xai.py`, `main.py`.
  - É **Kafka-driven** (consome eventos de decisão).
  - **NÃO expõe** endpoint HTTP de revalidação. Esse é o principal gap operacional desta refatoração.

- **NASP Adapter** (`apps/nasp-adapter/src/`) — executa a orquestração técnica. Continua sendo o
  *executor*, não a *autoridade de decisão*.

- **BC-NSSMF** (`apps/bc-nssmf/`) — registra lifecycle on-chain (`tx_hash`) quando provocado. Continua sendo
  o *registrador*, não o construtor de lifecycle.

### 1.3 Conclusão do diagnóstico

> O Portal Backend hoje é simultaneamente API ingress, orquestrador, builder de lifecycle, cliente de
> telemetria e gerador de evidência de remediação. Isso fere SoC e cria acoplamento entre camada de API e
> camada de runtime. A refatoração elimina esse acoplamento **sem mudar o contrato externo**.

---

## 2. Evidências atuais obrigatórias (devem ser citadas em cada fase)

| Conjunto | Caminho |
|---|---|
| Auditoria principal de responsabilidades | `evidencias_auditoria_responsabilidades_20260511T190246Z/` |
| Auditoria leve                           | `evidencias_auditoria_leve_20260509T145125Z/`            |
| Auditoria v2                              | `evidencias_auditoria_v2_20260509T145459Z/`             |
| Auditoria v3                              | `evidencias_auditoria_v3_20260509T150018Z/`             |
| Baseline desta refatoração               | `evidencias_refactor_responsabilidades_<TS>/baseline/`  |
| Backup rollback desta refatoração        | `evidencias_refactor_responsabilidades_<TS>/rollback/`  |
| Baselines anteriores                      | `evidencias_baseline_oficial/`, `evidencias_FINAL_RUNTIME_BASELINE_Q1_*/` |
| Runbook canônico                          | `docs/TRISLA_MASTER_RUNBOOK.md`                          |
| SSOT infra                                | `docs/TRISLA_INFRA_SSOT.md`                              |
| Workdir operacional                       | `docs/TRISLA_WORKDIR_OPERACIONAL.md`                     |
| Docs por módulo                           | `docs/modules/portal-backend.md`, `docs/modules/decision-engine.md`, `docs/modules/sla-agent-layer.md`, `docs/modules/sla-agent.md`, `docs/modules/bc-nssmf.md`, `docs/modules/nasp-adapter.md` |

Nenhuma evidência antiga pode ser apagada. Tudo novo entra em
`evidencias_refactor_responsabilidades_<TS>/`.

---

## 3. Mapa de responsabilidades — ATUAL × ALVO

### 3.1 Atual

| Responsabilidade                          | Componente atual         |
|-------------------------------------------|--------------------------|
| Northbound API (`/api/v1/sla/*`)          | Portal Backend           |
| Validação de entrada                      | Portal Backend           |
| Decisão (score, policy, risk, threshold)  | Decision Engine          |
| Orchestration trigger (decide e dispara)  | **Portal Backend**       |
| Orchestration execução técnica            | NASP Adapter             |
| Telemetry collect (PromQL SSoT)           | **Portal Backend**       |
| Telemetry refresh / revalidate            | **Portal Backend**       |
| `drift_summary`                           | **Portal Backend**       |
| `remediation_evidence` (P2)               | **Portal Backend**       |
| `lifecycle_state` build                   | **Portal Backend**       |
| Lifecycle on-chain registration (`tx_hash`)| BC-NSSMF (acionado pelo backend) |
| SLA-Agent runtime reassessment            | (não existe)             |

### 3.2 Alvo

| Responsabilidade                          | Componente alvo                            |
|-------------------------------------------|--------------------------------------------|
| Northbound API (`/api/v1/sla/*`)          | Portal Backend (inalterado)                |
| Validação de entrada                      | Portal Backend (inalterado)                |
| Decisão (score, policy, risk, threshold)  | Decision Engine (inalterado)               |
| Orchestration **decision/trigger**        | **Decision Engine** (nova autoridade)      |
| Orchestration **execução técnica**        | NASP Adapter (inalterado)                  |
| Telemetry collect base                    | Portal Backend (mantém para `/submit`)     |
| Telemetry refresh / revalidate            | **SLA-Agent** (nova autoridade)            |
| `drift_summary`                           | **SLA-Agent**                              |
| `remediation_evidence` (P2)               | **SLA-Agent**                              |
| `lifecycle_state` decision                | **Decision Engine**                        |
| Lifecycle on-chain registration (`tx_hash`)| BC-NSSMF (acionado pelo Decision Engine)  |
| SLA-Agent runtime reassessment            | **SLA-Agent** (endpoint HTTP novo, interno)|

> O Portal Backend permanece responsável apenas por **expor APIs públicas**, **validar entrada**, e
> **delegar** as ações operacionais para o componente correto. Em caso de falha do componente delegado,
> pode usar fallback temporário e marcar `delegated=false`, `fallback_reason=...`, jamais omitindo o fato.

---

## 4. Fases de refatoração (alinhadas ao PROMPT MASTER)

```
FASE 0  Baseline + freeze + backup ……………… (somente leitura)
FASE 1  Este guia ……………………………………… (somente docs)
FASE 2  Extração SLA-Agent (revalidate-telemetry) … (backend delega)
FASE 3  Decision Engine assume orchestration decision (backend delega)
FASE 4  Lifecycle registration via componente correto (backend só repassa)
FASE 5  Testes de não regressão (eMBB / URLLC / mMTC / revalidate)
FASE 6  Build & deploy por digest GHCR (cada serviço alterado)
FASE 7  Atualizar runbook + docs/modules (sem apagar histórico)
FASE 8  Relatório final FINAL_REFACTOR_REPORT.md
```

Cada fase **só inicia** depois da fase anterior produzir as evidências obrigatórias dentro de
`evidencias_refactor_responsabilidades_<TS>/`.

---

## 5. Critérios de entrada e saída por fase

### FASE 0 — Baseline & freeze

- **Entrada:** prompt master aceito; checkout do repo limpo; `git rev-parse HEAD` capturado.
- **Saída:**
  - `baseline/pods.txt`, `baseline/deployments.txt`, `baseline/services.txt`,
    `baseline/deployments.yaml`, `baseline/images.txt`, `baseline/git_status.txt`,
    `baseline/git_head.txt`, `baseline/captured_at_utc.txt`, `baseline/hostname.txt`,
    `baseline/FREEZE_SUMMARY.txt`.
  - `rollback/` contendo cópia dos arquivos críticos (portal-backend, decision-engine,
    sla-agent-layer, helm, docs principais).

### FASE 1 — Guia (este documento)

- **Entrada:** FASE 0 concluída.
- **Saída:** `docs/REFACTOR_TRISLA_RESPONSIBILITY_GUIDE.md` revisado pelo usuário.
- **Bloqueio explícito:** nenhuma alteração de código pode ocorrer antes deste guia existir.

### FASE 2 — SLA-Agent extraction

- **Entrada:** FASE 1 aprovada; backup em `rollback/` confirmado.
- **Saída:**
  - `apps/sla-agent-layer/src/` ganha rota `POST /api/v1/agent/revalidate-telemetry`
    (interna, exposta como ClusterIP).
  - Lógica de `_minimal_telemetry_drift` e `_build_remediation_evidence_p2` **co-localizada** no
    SLA-Agent (cópia idêntica a partir do backend, sem ainda apagar a do backend).
  - `apps/portal-backend/src/routers/sla.py` `/api/v1/sla/revalidate-telemetry` passa a **delegar**
    via HTTP para `SLA_AGENT_REVALIDATE_URL` (env), com fallback in-process.
  - Cada resposta carrega:
    - `metadata.delegated_to_sla_agent: true|false`
    - `metadata.delegation_target`: URL utilizada
    - `metadata.delegation_fallback_reason`: presente apenas em fallback
  - Evidências: `sla_agent/before_response.json`, `sla_agent/after_response.json`,
    `sla_agent/diff_response.txt`, `sla_agent/delegation_logs.txt`.
- **Critério bloqueante:** `diff_response.txt` deve mostrar **zero diferenças** em
  `intent_id`, `execution_id_revalidation`, `telemetry_snapshot_atual`, `drift_summary`,
  `revalidation_status`, `temporal_correlation` e `metadata.remediation_evidence`.

### FASE 3 — Decision Engine assume orchestration authority

- **Entrada:** FASE 2 aprovada.
- **Saída:**
  - Decision Engine retorna, além do payload atual, um objeto enriquecido:
    ```json
    {
      "decision": "...",
      "score": ...,
      "reason_codes": [...],
      "risk_score": ...,
      "orchestration_required": true|false,
      "lifecycle_state": "...",
      "orchestration_payload": {...}
    }
    ```
  - Portal Backend **deixa de decidir** se orquestra. Apenas executa o que o Decision Engine determinou.
  - `services/nasp.py` no backend passa a aceitar `orchestration_payload` pré-pronto vindo do DE;
    construção interna vira fallback marcado.
  - Cada `/submit` carrega `metadata.decision_engine_orchestration_authority: true|false`.
  - NASP Adapter continua sendo o executor real (`POST /nasp/orchestrate` ou equivalente).
- **Critério bloqueante:** `diff_submit.txt` mostra zero diferenças em
  `decision`, `decision_score`, `reason_codes`, `telemetry_snapshot`,
  `nasp_orchestration_status`, `lifecycle_state`, `orchestration_reference`,
  `failure_reason`, `failure_code`.

### FASE 4 — Lifecycle registration via componente correto

- **Entrada:** FASE 3 aprovada.
- **Saída:**
  - Decision Engine emite `lifecycle_event` para BC-NSSMF.
  - BC-NSSMF registra (`tx_hash` preservado, schema preservado).
  - Backend deixa de construir lifecycle como autoridade; vira passagem.
  - Evidências: `governance/lifecycle_before.json`, `governance/lifecycle_after.json`,
    `governance/tx_hash.txt`.
- **Critério bloqueante:** `tx_hash`, `lifecycle_state`, `metadata.blockchain_status` preservados.

### FASE 5 — Testes de não regressão

Executar de dentro de um pod com acesso a `localhost:18001` (ingress) ou via `kubectl port-forward` para
`trisla-portal-backend`:

1. `GET  /api/v1/health/global` → 200.
2. `POST /api/v1/sla/submit` payload eMBB.
3. `POST /api/v1/sla/submit` payload URLLC.
4. `POST /api/v1/sla/submit` payload mMTC.
5. `POST /api/v1/sla/revalidate-telemetry` com `intent_id` de #2 e #3.

Para cada resposta validar (`jq`):

- `decision in ["ACCEPT","REJECT","RENEGOTIATE"]`.
- `metadata.telemetry_snapshot` existe e não é vazio.
- `reason_codes` é lista não vazia.
- `drift_summary` existe quando aplicável (revalidate).
- `metadata.remediation_evidence` existe quando aplicável (revalidate).
- `tx_hash` existe quando `decision == "ACCEPT"`.
- `metadata.delegated_to_sla_agent == true` em revalidate (após FASE 2).
- `metadata.decision_engine_orchestration_authority == true` em submit (após FASE 3).

Saídas em `tests/*.json` + `tests/validation_summary.txt`.

### FASE 6 — Build & deploy por digest

- **Apenas após FASE 5 verde.**
- Serviços a (re)buildar: `portal-backend`, `decision-engine`, `sla-agent-layer`, opcionalmente
  `bc-nssmf` se a FASE 4 tocar nele.
- Regras na seção 9.

### FASE 7 — Documentação e runbook

- Atualizar (sem deletar histórico):
  - `docs/REFACTOR_TRISLA_RESPONSIBILITY_GUIDE.md` (este, sessão "execução" no fim)
  - `docs/TRISLA_MASTER_RUNBOOK.md` (anexar seção “Refactor de responsabilidades — <TS>”)
  - `docs/TRISLA_E2E_FLOW_CANONICAL.md` (se existir; senão criar)
  - `docs/modules/portal-backend.md`, `docs/modules/decision-engine.md`,
    `docs/modules/sla-agent-layer.md`, `docs/modules/sla-agent.md`, `docs/modules/bc-nssmf.md`.

### FASE 8 — Relatório final

`evidencias_refactor_responsabilidades_<TS>/analysis/FINAL_REFACTOR_REPORT.md` com:
resumo executivo, alterações, não-alterações, antes/depois, evidências de build, evidências de teste,
riscos remanescentes, rollback aplicado se houver, impacto no paper, próximas fases.

---

## 6. Testes de não regressão (consolidado)

```bash
# de dentro de um pod com acesso a 18001 ou via port-forward ao trisla-portal-backend
BACKEND=${BACKEND:-http://localhost:18001}

curl -sf $BACKEND/api/v1/health/global | tee tests/health.json

for slice in embb urllc mmtc; do
  curl -sf -X POST $BACKEND/api/v1/sla/submit \
       -H 'Content-Type: application/json' \
       -d @payloads/submit_${slice}.json \
       | tee tests/submit_${slice}.json
done

curl -sf -X POST $BACKEND/api/v1/sla/revalidate-telemetry \
     -H 'Content-Type: application/json' \
     -d @payloads/revalidate.json \
     | tee tests/revalidate.json
```

Validação automática (`tests/validation_summary.txt`):

```bash
for f in tests/submit_*.json; do
  jq -r '
    .decision as $d
    | .metadata.telemetry_snapshot as $ts
    | .metadata.nasp_orchestration_status as $orch
    | "\(input_filename) decision=\($d) telemetry=\(($ts|length>0)) orch=\($orch)"
  ' "$f"
done >> tests/validation_summary.txt
```

Qualquer linha com `telemetry=false` em ACCEPT, ou `decision` fora de
`{ACCEPT,REJECT,RENEGOTIATE}` em qualquer slice, **bloqueia** a fase 5.

---

## 7. Plano de rollback

Acionado se qualquer fase quebrar (critérios bloqueantes 2/3/4 falham, ou rollout fica unhealthy):

1. **Parar imediatamente** — não avançar para próxima fase.
2. Restaurar imagem anterior por **digest baseline**:
   ```bash
   kubectl -n trisla set image deployment/<deployment> \
     <container>=ghcr.io/abelisboa/<svc>@<digest-do-baseline-images.txt>
   kubectl -n trisla rollout status deployment/<deployment> --timeout=240s
   ```
3. Restaurar arquivos de código:
   ```bash
   cp -a evidencias_refactor_responsabilidades_<TS>/rollback/portal-backend/routers/sla.py \
         apps/portal-backend/src/routers/sla.py
   # repetir para os demais arquivos da pasta rollback/
   ```
4. Registrar erro em `evidencias_refactor_responsabilidades_<TS>/rollback/ROLLBACK_REPORT.md`:
   data, fase, sintoma, evidência (`kubectl logs`, `kubectl describe`, payload reproduzido).
5. **Nunca** mascarar a falha. **Nunca** continuar para a próxima fase com sintoma aberto.

Digests-baseline para rollback (snapshot FASE 0, ver `baseline/images.txt`):

- `trisla-portal-backend`         → `sha256:80dbb97785290951a6c56b0c41b3f8b6648a3d244b50711341b0be4a93316e6a`
- `trisla-decision-engine`        → `sha256:d5fe0b8a327dd1415403ccd99cd3e99bc85a7c222ede7ab016f98408da304d28`
- `trisla-sla-agent-layer`        → `sha256:397fef296ced041745eb9170524a875ac83e1c96e09f0c7248c49d051983f9f3`
- `trisla-bc-nssmf`               → `sha256:b0db5eef2128baddee2c1c3ea72fb5fec421afb1d87407e5f4a6aadd75f9f95a`
- `trisla-nasp-adapter`           → `sha256:063bddea5a6fcb38d8de504f91cc63b9ab13d5369dff43b6742cc5ae3ab02d79`

---

## 8. Regras de build (somente em `ssh node006`)

```bash
TS=$(date -u +%Y%m%dT%H%M%SZ)
SVC=portal-backend          # ou: decision-engine, sla-agent-layer, bc-nssmf
IMG="ghcr.io/abelisboa/trisla-${SVC}:${TS}"
DCTX="apps/${SVC}"

podman build --format docker -t "${IMG}" -f "${DCTX}/Dockerfile" "${DCTX}"
podman push "${IMG}"

# Digest remoto (preferido)
DIGEST=$(skopeo inspect \
  --authfile ~/.config/containers/auth.json \
  docker://${IMG} | jq -r .Digest)

# Fallback se skopeo falhar por token GHCR (registrar evidência):
[ -z "${DIGEST}" ] && DIGEST=$(podman inspect "${IMG}" | jq -r '.[0].Digest // empty')

echo "${SVC} ${TS} ${IMG} ${DIGEST}" >> evidencias_refactor_responsabilidades_${OUT_TS}/deploy/digests.txt
```

Proibido:
- `:latest`;
- deploy por tag;
- build em outro host que não `node006`;
- esquecer de gravar o digest em `deploy/digests.txt`.

---

## 9. Regras de deploy por digest remoto GHCR

```bash
DEP=trisla-${SVC}                     # ex.: trisla-portal-backend
CTN=${SVC}                            # nome do container do pod (ver deployments.yaml)
kubectl -n trisla set image deployment/${DEP} \
  ${CTN}=ghcr.io/abelisboa/trisla-${SVC}@${DIGEST}
kubectl -n trisla rollout status deployment/${DEP} --timeout=240s
kubectl -n trisla get deployment/${DEP} -o yaml \
  > evidencias_refactor_responsabilidades_${OUT_TS}/deploy/${DEP}_after.yaml
kubectl -n trisla get deployment -o jsonpath='{range .items[*]}{.metadata.name}{" => "}{.spec.template.spec.containers[*].image}{"\n"}{end}' \
  > evidencias_refactor_responsabilidades_${OUT_TS}/deploy/images_after.txt
```

Proibido:
- `kubectl edit` interativo;
- alterar Helm `values.yaml` sem grava-lo em `deploy/`;
- aplicar manifest sem registrar diff prévio.

---

## 10. Matriz de riscos

| # | Risco | Probab. | Impacto | Mitigação | Quando aciona rollback |
|---|---|---|---|---|---|
| R1 | Quebra do contrato `/api/v1/sla/submit` (campos faltando) | Baixa | Alto | `diff_submit.txt` zero-diff bloqueante (FASE 3) | Diff > 0 em campos críticos |
| R2 | Quebra do contrato `/api/v1/sla/revalidate-telemetry` | Baixa | Alto | `diff_response.txt` zero-diff bloqueante (FASE 2) | Diff > 0 em `drift_summary`, `revalidation_status` |
| R3 | SLA-Agent indisponível durante FASE 2 | Média | Médio | Backend faz fallback in-process e marca `delegated_to_sla_agent=false`, `fallback_reason="sla_agent_unreachable"` | Erro 5xx persistente > 30s |
| R4 | Decision Engine não emitir `orchestration_payload` | Média | Médio | Backend faz fallback `_build_orchestration_payload` atual; marca `decision_engine_orchestration_authority=false` | DE responder sem `orchestration_required` em > 1% dos submits canários |
| R5 | BC-NSSMF falhar registro lifecycle | Média | Médio | Manter código atual de retry no caminho do backend até FASE 4 estabilizar | `tx_hash` ausente em ACCEPT consistentemente |
| R6 | Rollout demorar > 240s | Média | Alto | `rollout status --timeout=240s` falha → rollback automático manual | Timeout |
| R7 | Tag GHCR sem digest remoto disponível | Baixa | Médio | Usar `podman inspect` como fallback documentado | Não há digest mesmo após retry |
| R8 | Telemetria diverge entre Portal Backend e SLA-Agent | Média | Médio | SLA-Agent reusa **exatamente** `promql_ssot.py` e `collector.py` do backend (cópia idêntica) | Diff > 0 em `telemetry_snapshot.ran/transport/core` |
| R9 | `*-trisla` deployments paralelos ficarem fora de sincronia | Baixa | Baixo | Não tocar nas réplicas `*-trisla` nesta refatoração | — (escopo congelado) |
| R10 | Evidências antigas perdidas | Baixa | Alto | Política: **nunca** apagar `evidencias_*`; criar novo TS | — |

---

## 11. O que NÃO deve ser alterado

- Contratos JSON públicos (`SLASubmitRequest`, `SLASubmitResponse`,
  `SLARevalidateTelemetryRequest`, `SLARevalidateTelemetryResponse`).
- Endpoints públicos do Portal Backend (mesmos paths, mesmos métodos, mesmos status codes).
- Schemas em `apps/portal-backend/src/schemas/sla.py` (qualquer campo novo é **adicionado**, jamais
  removido/renomeado).
- Decision Engine policy thresholds (sem justificativa formal + evidência).
- Helm chart `helm/trisla/Chart.yaml` versão major; apenas `appVersion` ou imagens podem mudar.
- Deployments paralelos `*-trisla` (congelados).
- Evidências antigas (`evidencias_*` pre-existentes).
- Runbook canônico (apenas anexar nova seção, nunca sobrescrever histórico).

---

## 12. Como atualizar runbook e evidências (regra operacional)

- **Sempre** gerar novo `TS=$(date -u +%Y%m%dT%H%M%SZ)` para cada execução.
- **Nunca** reaproveitar diretório de evidência de fase anterior — uma fase, um diretório por TS.
- Em cada update no runbook usar bloco anexável com o TS:

  ```md
  ## Refactor de responsabilidades — <TS>
  - Fase: <N>
  - Evidências: evidencias_refactor_responsabilidades_<TS>/
  - Build digests: deploy/digests.txt
  - Rollout: deploy/rollout_status.txt
  - Diff JSON: <fase>/diff_*.txt
  ```

- Em cada `docs/modules/<mod>.md`, anexar seção "Refactor TS=<...>".

---

## 13. Estado da execução (auto-atualizado)

| Fase | Status | TS | Observação |
|---|---|---|---|
| FASE 0 — Baseline & freeze | concluída | `20260511T191645Z` | `evidencias_refactor_responsabilidades_20260511T191645Z/baseline/` + `rollback/` (196 arquivos) |
| FASE 1 — Guia | concluída | `20260511T191645Z` | este documento |
| FASE 2 — SLA-Agent extraction | **concluída — code-only, zero-diff** | `20260511T191645Z` | 9 novos arquivos em `apps/sla-agent-layer/src/revalidate/` (742 linhas); +421 em `routers/sla.py` (fallback preservado); +23 em `sla-agent/main.py` (endpoint `POST /api/v1/agent/revalidate-telemetry`); +3 em requirements (httpx). Evidências: `sla_agent/PHASE2_REPORT.md`, `sla_agent/diff_response.txt` (TOTAL_DIFF_COUNT=0). Pendência: deploy/digest GHCR fica para FASE 6 |
| FASE 3 — DE orchestration authority | **concluída — code-only** | `20260511T191645Z` | DE: `orchestration_authority.py` + `service.py` (enrich metadata pós-S30). Portal: `nasp.py` consome `orchestration_required` / `orchestration_intent`; `sla.py` adiciona `de_initial_lifecycle_state` + `lifecycle_state_source`. Evidências: `decision_engine/PHASE3_REPORT.md`, `decision_engine/analysis/zero_regression_check.txt`, `patches/phase3_full.patch`. Sem build/deploy/Helm. Pendência: rollout digest (FASE 6) |
| FASE 4 — Lifecycle via componente correto | **concluída — code-only** | `20260511T191645Z` | DE: `lifecycle_authority.py` (novo) + `service.py` (chama enrich pós-FASE 3) — adiciona `metadata.lifecycle_event` + `metadata.governance_event` + flags `decision_engine_lifecycle_authority` / `decision_engine_governance_authority`. BC-NSSMF: `governance_lineage.py` (novo) + `main.py` (resposta `governance_registration` additive em `/api/v1/register-sla`, novo endpoint canônico `/api/v1/governance-event` com fallback determinístico). Portal: `routers/sla.py` apenas repassa (`portal_lifecycle_role=relay`, `portal_governance_role=relay`); `sla_lifecycle`/`lifecycle_state` preservados, agora etiquetados como `lifecycle_pipeline_state_source=portal_backend_pipeline_composite`. Evidências: `governance/PHASE4_REPORT.md`, `governance/analysis/public_contract_diff.txt` (PUBLIC_CONTRACT_BREAKING_CHANGES=0), `governance/analysis/zero_regression_check.txt`, `governance/patches/phase4_full.patch`, `governance/governance_registration_flow.md`, `governance/tx_hash_flow.md`. Sem build/deploy/Helm/manifests. Pendência: wiring efetivo do endpoint `/api/v1/governance-event` (FASE 6/7) e captura direta do bloco `governance_registration` em `services/nasp.py` (escopo proibido nesta fase). |
| FASE 5 — Testes não regressão | **concluída — code-only, integração local** | `20260511T191645Z` | Validação estática (`py_compile` portal SLA router, DE service+authority modules, BC-NSSMF main+governance_lineage, pacote `sla-agent-layer/src/revalidate`). Contratos: `integration/analysis/public_contract_validation.txt` — PUBLIC_CONTRACT_BREAKING_CHANGES=0, NEW_REQUIRED_TOP_LEVEL_FIELDS=0, ADDITIVE_METADATA_ONLY=true. Cenários integrados: `integration/tests/*_integrated.json` + `integrated_scenario_validation.txt`. Cruzamento FASE 2+3+4: `cross_phase_validation.txt` (mock HTTP `_delegate_revalidate_to_sla_agent`, drift_summary/remediation_evidence preservados no payload; BC degraded `governance_registration_fallback=true`). Resumo zero-regressão: `zero_regression_summary.txt` — PHASE2_ZERO_DIFF=confirmed, PHASE3/4 breaking=0, READY_FOR_BUILD_DEPLOY=true. Script mestre: `integration/tests/run_phase5_validation.py` (PYTHONPATH=`apps/portal-backend`). Sem build/push/deploy/rollout/Helm. Pendência: FASE 6 (digest GHCR) após aprovação operacional. |
| FASE 6 — Build & deploy por digest | **concluída — runtime real, digest-only** | `20260511T202935Z` | Build/push/deploy dos 4 serviços alterados via `ssh node006`. Digests GHCR (resolvidos com `podman push --digestfile` após falha de skopeo HTTP 403): portal-backend `sha256:5629970f640120bb4c65eea4eea5b3f356f87ab66ce94b6a5cdf3f93f7283152`; decision-engine `sha256:0658cd8b51bb424998c2de8edfe704ba1711225bc4451fec36b60eabc07db073`; sla-agent-layer `sha256:7d0fa8d8bc8ff3c888e2696e525c7f9470bc613ebee0023a617b0c11498c789e`; bc-nssmf `sha256:57b79430d8b79803bc8c65e277597b58e0ace605c095bd45a3883847a7ec0099`. Rollout sequencial OK (DE → BC → SLA-Agent → Portal). Pods alvo Running 1/1, 2/2, 1/1, 3/3. Health 200. Submits eMBB/URLLC/mMTC retornaram com `portal_lifecycle_role=relay` + `portal_governance_role=relay` + `decision_engine_*_authority=true` em runtime. Delegação SLA-Agent ATIVADA via `kubectl set env` (`SLA_AGENT_REVALIDATE_URL=http://trisla-sla-agent-layer:8084/api/v1/agent/revalidate-telemetry`); `delegated_to_sla_agent=true` confirmado em chamada `/sla/revalidate-telemetry`. Sem `:latest`, sem Helm, sem alteração de thresholds. Evidências: `deploy/PHASE6_REPORT.md`, `deploy/runtime/digest_validation.txt`, `deploy/rollback/ROLLBACK_REPORT.md`. |
| FASE 7 — Docs e runbook | **concluída — freeze oficial, baseline pós-refatoração** | `20260511T191645Z` | Freeze runtime captado em `freeze/runtime/` (pods, deployments, services, deployments YAML, images_post_refactor.txt, active_digests_summary.txt, portal_backend_sla_agent_env.txt). Ownership matrix em `freeze/ownership/runtime_responsibility_matrix.md` (autoridade × executor × fallback). Runbooks SSOT atualizados com bloco POST-REFACTOR FREEZE: `docs/TRISLA_MASTER_RUNBOOK.md`, `docs/TRISLA_E2E_FLOW_CANONICAL.md` (sequência operacional reescrita), `docs/TRISLA_INFRA_SSOT.md` (digests/envs/endpoints). Module docs atualizados (autoridade/fallback/delegation/interfaces): `docs/modules/portal-backend.md`, `decision-engine.md`, `sla-agent-layer.md`, `bc-nssmf.md`. Fallback matrix em `freeze/rollback/fallback_matrix.md`; recovery playbook em `freeze/rollback/runtime_recovery_playbook.md`. Consistência documental: `freeze/analysis/legacy_authority_claims.txt` (22 ocorrências classificadas em `freeze/analysis/documentation_consistency_report.md` — 13 OK / 7 HISTORICAL_REFERENCE / 2 NEEDS_UPDATE não bloqueantes). Baseline pós-refatoração: `freeze/analysis/post_refactor_baseline_summary.md`. Relatório final: `freeze/PHASE7_REPORT.md`. Política: legacy fallback paths preservados; nada removido; sem Helm, sem rollout, sem alteração de contratos públicos, sem alteração de thresholds. Readiness: ambiente pronto para futura cleanup phase (não iniciada). |
| FASE 8 — Canary stabilization + Legacy observability | **concluída — runtime canário estável, zero remoção** | `20260511T191645Z` | Snapshot runtime em `stabilization/runtime/` (pods/images/events). Digest drift = NONE (4/4 alvos idênticos a FASE 6/7). Delegação SLA-Agent: 12/12 requests reais com `delegated_to_sla_agent=true`, `processed_by_sla_agent=true`, `delegation_success_rate=1.0`, `fallback_rate=0.0`, `timeout_rate=0.0` (`stabilization/tests/revalidate_batch.jsonl`, `stabilization/delegation/sla_agent_delegation_validation.txt`). Authority em runtime: 3/3 submits (eMBB/URLLC/mMTC) com `portal_lifecycle_role=relay`, `portal_governance_role=relay`, `decision_engine_orchestration_authority=true`, `decision_engine_lifecycle_authority=true`, `decision_engine_governance_authority=true`, `lifecycle_event.lifecycle_authority=decision-engine`, `governance_event.event_authority=decision-engine`, `governance_event_id` populado (`stabilization/tests/submit_*_stabilization.json`, `stabilization/analysis/runtime_authority_validation.txt`). Fallbacks: 0 ativações em logs (`--tail=500` por deployment) e em respostas; 0 `ERROR/CRITICAL/Traceback` nos 4 alvos (`stabilization/fallbacks/fallback_activation_report.md`). Legado: 215 ocorrências classificadas — 7 ACTIVE_FALLBACK, 8 REQUIRED_LEGACY, 6 DO_NOT_REMOVE, **0 POSSIBLE_CLEANUP** (`stabilization/legacy/legacy_cleanup_candidates.md`). Consistência runtime↔docs↔ownership↔digests↔fallback matrix: STABLE (`stabilization/analysis/runtime_consistency_report.md`). Relatório final: `stabilization/PHASE8_REPORT.md`. Sem cleanup, sem remoção, sem alteração de Helm/contratos/thresholds/imagens. Readiness para cleanup: **AINDA NÃO** — janela curta e cenário ACCEPT não exercitado nesta amostra. |
| FASE 9 — Accept-path observability + NASP/BC validation | **concluída — sem ACCEPT reproduzível, bloqueador pré-existente classificado, zero remoção** | `20260511T191645Z` | Snapshot pré-fase em `accept_path/runtime/`. Campanha controlada de 13 submits (5 eMBB + 5 mMTC + 3 URLLC com requisitos relaxados) sob restrição "no code change / no thresholds / no helm / no rollout" produziu: **0 ACCEPT**, 8 RENEGOTIATE, 5 REJECT. `threshold_decision=ACCEPT` em 13/13 (score-mode médio 0.833, melhor 0.846), mas override por `_merge_slice_multidomain_severity` por `slice_aware_multidomain.core_risk=1.0` (gate `*_CORE_RENEGOTIATE` em eMBB/URLLC; `MMTC_CORE_CAPACITY_REJECT` em mMTC). Bloqueador identificado como **EXPECTED_LIMITATION pré-existente** em `apps/decision-engine/src/trisla09_slice_aware_helpers.py` (mismatch de unidades cpu/memória entre coletor portal e helper de DE) — **NÃO induzido pelas FASES 2–6** (`accept_path/analysis/no_accept_blocker.md`). Validação arquitetural mesmo sem ACCEPT: 13/13 com `decision_engine_orchestration_authority=true`, `decision_engine_lifecycle_authority=true`, `decision_engine_governance_authority=true`, `portal_*_role=relay`, `governance_event_id` populado pelo DE (FASE 4). NASP: `NOT_EXERCISED_DUE_TO_NO_ACCEPT` (`accept_path/nasp/nasp_accept_path_validation.md`). BC-NSSMF: `governance_registration_status=SKIPPED_NO_ACCEPT` em 13/13 (não fallback degraded — cadeia "BC só após ACCEPT" preservada, `accept_path/governance/bc_governance_accept_validation.md`). SLA-Agent pós-decisão (revalidate contra intent de RENEG): `delegated_to_sla_agent=true`, `delegation_fallback_reason=null`, drift/remediation presentes (`accept_path/sla_agent/sla_agent_after_accept_validation.md`). Logs `--tail=1000` × 4 deployments sem ERROR/CRITICAL/Traceback. Cleanup readiness: **CLEANUP_READY = false** (critério ACCEPT não atendido — `accept_path/analysis/cleanup_readiness_after_accept_path.md`). Sem build/push/deploy/rollout/Helm/thresholds/contratos alterados; sem máscara de ACCEPT. Relatório final: `accept_path/PHASE9_REPORT.md`. Próxima fase recomendada: **fase de correção dedicada** sobre `trisla09_slice_aware_helpers.py` (fora do ciclo de cleanup), seguida por novo ciclo FASE 6→7→8→9 antes de qualquer cleanup. |
| FASE 10 — Slice-aware calibration audit | **concluída — root cause CONFIRMED, plano de correção registrado, zero alteração** | `20260511T191645Z` | Pipeline matemático e ranges em `calibration_audit/math/pipeline_equations.md`. Trace de variáveis críticas (`cpu_utilization`, `memory_utilization`, `core_risk`, helper inputs, thresholds slice-aware) em `calibration_audit/code/core_risk_variable_trace.txt`. Comparação runtime↔helper (13/13 amostras FASE 9) em `calibration_audit/tests/runtime_vs_helper_comparison.jsonl` — `mismatch_magnitude_ratio` (helper/portal) ≈ **3.5×10⁹** em todas as amostras; `computed_core_risk_with_helper_inputs=1.0` em todas; `computed_core_risk_if_mem_were_percent ≤ 0.011` em todas; `would_change_to_accept=true` em **13/13**. Análise de unidade em `calibration_audit/analysis/unit_mismatch_analysis.md`: **HELPER_UNIT_MISMATCH = CONFIRMED** (`apps/sem-csmf/src/decision_engine_client.py:254-259` escreve `process_resident_memory_bytes` em bytes no campo `core.memory_utilization` que o helper interpreta como `%`); CPU OK (`_clamp_cpu_percent` em [0,100]); contract gap em `apps/portal-backend/src/telemetry/contract_v2.py` (chave `core.memory_utilization` não declarada em `TELEMETRY_UNITS_V2`). Override logic em `calibration_audit/analysis/override_logic_trace.md`: `_merge_slice_multidomain_severity` é monotônico em severidade e está correto — atua como amplificador do bug upstream, não fonte. Reprodução offline com o helper real importado via `importlib` (`calibration_audit/tests/_offline_reproduction.py`, output `offline_reproduction.json` + `offline_reproduction_console.txt`, narrativa em `offline_reproduction.md`): eMBB/mMTC/URLLC com input em bytes reproduzem RENEG/REJECT/RENEG **idênticos ao runtime**; substituindo apenas `memory_utilization` por % (~0.95) todos viram ACCEPT. Classificação final em `calibration_audit/analysis/root_cause_classification.md`: causa raiz = `HELPER_UNIT_MISMATCH` (primária) + `TELEMETRY_SNAPSHOT_MAPPING` (gap contratual) + `MULTIPLE_FACTORS` (cooperação produtor/contrato/consumidor); origem temporal **pré-existente às FASES 2–6** — caminho slice-aware foi apenas exposto pelo refactor. Plano de correção (sem implementar) em `calibration_audit/analysis/proposed_fix_plan.md`: PR-1 contrato v2 (declarar `core.memory_utilization=%`), PR-2 SEM-CSMF normalizar bytes→% via limite de memória do container/node (com flag de rollback), PR-3 defesa em profundidade no helper (validar range, sinalizar `INPUT_DEGRADED_*` sem saturar), estratégia de validação (offline → cluster → re-rodar FASE 9), rollback por digest/env, campanhas FASE 5/6/8/9 marcadas para re-execução. Runtime baseline pré-fase: `calibration_audit/runtime/pods_before_phase10.txt`, `deployments_before_phase10.txt`, `images_before_phase10.txt` (digests inalterados desde FASE 6/7/8/9). Relatório final: `calibration_audit/PHASE10_REPORT.md`. **Zero alteração**: nenhum código, threshold, manifest, Helm, rollout ou contrato público modificado. **Cleanup permanece proibida**. Próxima fase recomendada: **FASE 11 (Correção de calibração)** seguindo `proposed_fix_plan.md`, com novo ciclo FASE 5→6→7→8→9 antes de qualquer cleanup. |
| FASE 11 — Calibration fix (3 PRs controlados, code-only) | **concluída — code-only, offline ACCEPT recuperado, zero alteração de runtime** | `20260511T191645Z` | Três PRs sequenciais e rastreáveis sob `evidencias_.../calibration_fix/`: **PR-1** (`apps/portal-backend/src/telemetry/contract_v2.py`) declara `core.memory_utilization=%` e `core.memory_ratio=ratio_0_1` em `TELEMETRY_UNITS_V2` + cria `TELEMETRY_RANGES_V2` opcional (`pr1_contract/contract_semantics.md`, `contract_update_diff.patch` 39 linhas, sintaxe OK, risco zero). **PR-2** (`apps/sem-csmf/src/decision_engine_client.py`) substitui escrita de bytes em `memory_utilization` por percentual 0..100 derivado de `node_memory_MemTotal_bytes` (fallbacks `machine_memory_bytes` + env `SEM_CSMF_CORE_MEMORY_TOTAL_BYTES`), com **kill switch dinâmico** `SEM_CSMF_MEMORY_UTIL_NORMALIZE=false` (branch `legacy_passthrough` para rollback sem rebuild) e logs defensivos `memory_normalization_source`, `raw_memory_bytes`, `normalized_memory_utilization`; preserva `memory_bytes` (`pr2_normalization/normalization_logic.md`, `normalization_diff.patch` 149 linhas, sintaxe OK). **PR-3** (`apps/decision-engine/src/trisla09_slice_aware_helpers.py`) adiciona `_percent_or_degraded` com 4 faixas (None→0, 0..100 OK, 100..1000 clamp+advisory, >1000 degraded+mismatch), condiciona hard gate `MMTC_CORE_CAPACITY_REJECT` e gate `*_CORE_RENEGOTIATE` a `*_gate_trusted=True`, propaga `memory_unit_mismatch_detected`/`fallback_normalization_applied`/`degraded_inputs`/`reason_codes_advisory` (aditivos), preserva assinatura pública e chaves pré-existentes (`pr3_helper_defense/helper_defense_logic.md`, `helper_defense_diff.patch` 144 linhas, sintaxe OK). Validação offline (`tests/_offline_revalidation.py`, `offline_revalidation.json`, `offline_revalidation_console.txt`, `offline_revalidation.md`) com helper real importado via importlib × 3 amostras canônicas FASE 9 (eMBB i=1, mMTC i=6, URLLC i=11) × 5 cenários: **ACCEPT em 12/12 cenários benignos** (incl. input em bytes c/ defesa PR-3, PR-2 normalized, degraded None, 50% real), **RENEGOTIATE em 3/3 cenários no threshold (mem=80)** — sensibilidade do gate preservada. Validação matemática (`analysis/post_fix_math_validation.md`) confirma: ANTES core_risk=1.0 saturado → DEPOIS core_risk coerente (eMBB 0.0019, mMTC 0.0025, URLLC 0.009); decisão final ACCEPT alinhada ao `threshold_decision=ACCEPT` do score_mode. Não-regressão arquitetural (`analysis/architecture_non_regression.md`): 7/7 eixos arquiteturais consolidados (orchestration/lifecycle/governance/SLA-Agent/NASP/BC/severity-merge) **não tocados**; API pública/schemas Pydantic inalterados; consumidores indiretos de `core.memory_utilization` (`engine.py:392`, `ml_client.py:230,264-266`, `drift.py`, `i1_routes.py`) recebem valor mais coerente (% em vez de bytes OOD) — side-benefit, sem regressão. Cluster runtime **intocado**: digests permanecem inalterados desde FASES 6/7/8/9/10. Snapshots de rollback em `rollback/` (baselines `*_before.py` dos 3 arquivos + `git_diff_before_phase11.patch`); rollback granular em 3 níveis: kill switch env, restauração por digest GHCR, restauração por arquivo. Cleanup readiness: **CLEANUP_READY = false** (mantido — só muda após FASE 12 deploy + ACCEPT real exercitado em runtime com NASP+BC+tx_hash). Relatório final: `calibration_fix/PHASE11_REPORT.md`. Sem build/push/deploy/rollout/Helm/thresholds/orchestration/governance/APIs alteradas. Próxima fase recomendada: **FASE 12 — Recalibration deploy & validation** (build+push GHCR por digest dos 3 serviços, set image via ssh node006, smoke test, re-run campanha FASE 9, validar ACCEPT real com NASP+BC, atualizar FASE 7 SSOT). |
| FASE 12 — Recalibration deploy & ACCEPT-path validation | **concluída — runtime real por digest, ACCEPT recuperado, NASP+BC+tx_hash exercitados** | `20260512T014335Z` | Build/push/deploy dos 3 serviços alterados na FASE 11 via `ssh node006`, exclusivamente por digest GHCR (sem `:latest`). Digests resolvidos com `podman push --digestfile`: `trisla-sem-csmf=sha256:793de9ab2415db95e92ae139cbc24913f94d13f6675aecd5873ba72f7052b2fe`; `trisla-decision-engine=sha256:64146e3ce1e9a7b52e159b81afa46f11b08e19c1ae96c69f7f122146de3fdf66`; `trisla-portal-backend=sha256:67d17395f5045a5455f850c6858bea5de08239bfd43b31b16bdc6cddb426ece3` (`calibration_deploy/digest/digests.txt`, `runtime/digest_validation.txt` ALL MATCH). Rollout sequencial (sem-csmf → decision-engine → portal-backend) `successfully rolled out` em todos. Bc-nssmf, sla-agent-layer e nasp-adapter **não rebuildados** (não alterados na FASE 11; mantêm digests FASE 6/7). Smoke `GET /health/global` HTTP 200; smoke submit eMBB já retornou `decision=ACCEPT` com `slice_aware_multidomain.core_risk=0.001986` (vs 1.0 saturado em FASE 9), `tx_hash=0x7fad9738…`, `block_number=4268354`, `nasp_orchestration_status=SUCCESS`, todas as autoridades preservadas. Campanha ACCEPT-path com payloads FASE 9 reusados: **3/3 ACCEPT em 3 submits** (stop em 3 ACCEPTs reais; stop bem dentro do budget de 30 — `accept_path/submit_campaign_after_fix.jsonl`, `accept_1_after_fix.json`, `accept_2_after_fix.json`, `accept_3_after_fix.json`). `core_risk` por ACCEPT: 0.001944 / 0.002274 / 0.004187 (todos `<< 0.80` — gate de RENEG não dispara); slice-aware `EMBB_MULTIDOMAIN_FEASIBLE` × 3; severity merge **não** override; `tx_hash` real e único por ACCEPT (`0x7b9fd0fe…`, `0x8eb0756e…`, `0x8e15c8bd…`) com `block_number` incremental (4268405 / 4268409 / 4268413), `governance_registration_status=REGISTERED`, `governance_registration_authority=bc-nssmf`, `governance_registration_fallback=False`. NASP: `nasp_orchestration_attempted=True` + `nasp_orchestration_status=SUCCESS` + `nsi_id` em 3/3 (`nasp/nasp_after_fix_validation.md`). BC: 3/3 commits reais sem fallback (`governance/bc_after_fix_validation.md`). Autoridades: `decision_engine_orchestration_authority=True`, `decision_engine_lifecycle_authority=True`, `decision_engine_governance_authority=True`, `portal_*_role=relay` em 3/3 — modelo pós-refatoração das FASES 3/4/7 **empiricamente validado**. SLA-Agent pós-ACCEPT (revalidate-telemetry contra `intent_id` do ACCEPT_1, sem e com `reference_telemetry_snapshot`): `delegated_to_sla_agent=True`, `processed_by_sla_agent=True`, `delegation_target=http://trisla-sla-agent-layer:8084/api/v1/agent/revalidate-telemetry`, `fallback_used=None` (0/2), drift_summary 6 campos comparados na chamada com referência (`sla_agent/revalidate_after_accept_after_fix.json`, `revalidate_with_reference.json`, `sla_agent_after_accept_validation.md`). Comparação FASE 9 vs FASE 12: `analysis/calibration_runtime_validation.md` (ACCEPT 0→3, core_risk 1.0→~10⁻³, NASP/BC nunca→3/3). Cleanup readiness: **`CLEANUP_READY = true`** pela primeira vez desde o início do refactor — 6/6 critérios satisfeitos (`analysis/cleanup_readiness_after_phase12.md`); cleanup **NÃO iniciado** nesta fase por restrição explícita do prompt; fallbacks preservados (kill switch SEM-CSMF, defesa `_percent_or_degraded`, fallback Portal local de revalidate, fallback BC degraded). Rollback completo disponível: YAMLs em `rollback/{sem_csmf,decision_engine,portal_backend}_deployment_before.yaml` + digests pré-FASE-12 documentados; nenhum rollback foi necessário. Relatório final: `calibration_deploy/PHASE12_REPORT.md`. Sem alteração de Helm/thresholds/orchestration/governance/severity-merge/APIs. Próxima fase recomendada: **fase de cleanup controlada** (sob nova autorização) que preserve fallbacks, kill switches, defesa em profundidade e re-execute digest deploy + nova campanha ACCEPT após cada remoção. |
| FASE 13 — Final scientific freeze | **concluída — read-only freeze, paper-readiness produzido, cleanup adiado** | `20260512T0143Z+` | Pacote oficial de evidências consolidado sob `final_freeze/` sem qualquer alteração de código/Helm/threshold/runtime. Snapshot final do runtime via `ssh node006`: `final_freeze/runtime/{pods_final.txt,deployments_final.txt,services_final.txt,deployments_final.yaml,images_final.txt,events_final.txt}` mostrando **zero digest drift** desde FASE 12 (sem-csmf/DE/portal nos digests FASE 12; bc-nssmf/sla-agent-layer/nasp-adapter nos digests FASE 6; canonical READY 1/1, 2/2, 3/3, 0 restarts nos pods novos, eventos só normais de rollout); validação em `final_freeze/runtime/final_runtime_validation.md` (ALL MATCH; orphan `*-trisla` pods classificados como não-ativos, escopo de cleanup futura). Índice mestre: `final_freeze/evidence_index/MASTER_EVIDENCE_INDEX.md` (mapeia objetivo, evidência principal, resultado, status e PHASE*_REPORT.md das FASES 0–13 com cross-reference por concern). Resumo científico: `final_freeze/scientific_summary/FINAL_SCIENTIFIC_SUMMARY.md` (12 seções: o que estava errado, como foi corrigido, runtime real, não-regressão, ACCEPT recuperado, NASP, BC, tx_hash, SLA-Agent, calibração, limitações, o que NÃO remover). Matriz final de responsabilidades: `final_freeze/scientific_summary/FINAL_RESPONSIBILITY_MATRIX.md` (20 linhas authority × executor × evidência cobrindo semantic interpretation, decision scoring, orchestration authority/execution, lifecycle/governance authority + registration, runtime reassessment, telemetry refresh, drift_summary, remediation_evidence, tx_hash, fallbacks). Paper alignment: `final_freeze/paper_alignment/PAPER_UPDATE_NOTES.md` orienta futura atualização (Portal=relay, DE=authority, SLA-Agent=runtime reassessment executor, BC-NSSMF=governance registration executor, ACCEPT-path com evidência real, calibration fix como maturação experimental — não resultado científico primário, **não** apresentar cleanup como feito, **DECLARAR** digest-only runtime lineage, hard "do not" list). Cleanup readiness freeze: `final_freeze/cleanup_readiness/CLEANUP_READINESS_FINAL.md` reafirma `CLEANUP_READY=true` (6/6 gates FASE 12), lista 10 componentes que **NÃO** podem ser removidos (fallback revalidate Portal, kill switch `SEM_CSMF_MEMORY_UTIL_NORMALIZE`, defesa `_percent_or_degraded`, `memory_bytes` echo, `TELEMETRY_RANGES_V2`, `_merge_slice_multidomain_severity`, fallback BC degraded, digests FASE 6 inalterados, SSOT, fallback matrix), 5 fallbacks que **devem permanecer**, recomendação para cleanup incremental (re-baseline → orphan deployments → orphan pods → audit → per-removal digest deploy + ACCEPT campanha → SSOT update → só então paper). Rollback final consolidado: `final_freeze/rollback/FINAL_ROLLBACK_MAP.md` cobre histórico de digests pré-FASE-6 / FASE 6 / FASE 12 / FASE 13 atual, rollback por digest GHCR de cada um dos 3 serviços FASE 12, rollback de env `SLA_AGENT_REVALIDATE_URL` (FASE 6), rollback do kill switch `SEM_CSMF_MEMORY_UTIL_NORMALIZE` (FASE 11 PR-2), rollback de arquivos FASE 11 (`calibration_fix/rollback/*_before.py`), referência ao FASE 6 `deploy/rollback/ROLLBACK_REPORT.md` e aos YAMLs FASE 12 `calibration_deploy/rollback/*_deployment_before.yaml`, decision tree por sintoma, nota de idempotência. Relatório final: `final_freeze/PHASE13_REPORT.md`. Cleanup **NÃO iniciado**; paper **NÃO atualizado**; fallbacks **preservados**; código/Helm/threshold/orchestration/governance/contratos **intactos**. Próxima fase válida (uma das duas, sob nova autorização): **paper update phase** (aplicar guidance do `PAPER_UPDATE_NOTES.md`) ou **dedicated cleanup phase** (incremental, digest-deploy-validated, começando por orphan `*-trisla` e ReplicaSets antigos). |
| FASE 14 — (futura) Cleanup OU Paper update | pendente | — | só sob autorização explícita |

---

## 14. Notas de ambiente (importantes)

- O baseline foi coletado a partir de `hostname=node1`. O **PROMPT MASTER** determina `ssh node006` como
  entrypoint operacional obrigatório para qualquer ação que altere o cluster
  (build, push, set-image, rollout, kubectl apply). Esta fase (0+1) é
  exclusivamente *read-only no cluster* + criação local de docs e backups, então o desvio é
  registrado e não viola a regra.
- A partir da FASE 2 toda execução de `podman build`, `podman push`, `skopeo inspect`,
  `kubectl set image` e `kubectl rollout` **deve** ser feita após `ssh node006`. Caso seja necessário
  executar daqui, anotar `HOST_USED=node1` em `deploy/host.txt` com a justificativa, e gerar evidência
  comparativa com o esperado em `node006`.

---

**FIM DO GUIA OBRIGATÓRIO.** Fases 0–13 concluídas. **FASE 13 (Final scientific freeze)** consolidou o baseline oficial pós-refatoração + pós-correção de calibração em `evidencias_refactor_responsabilidades_20260511T191645Z/final_freeze/` em modo **READ-ONLY / NO CODE CHANGE**: snapshot final do runtime via `ssh node006` (`pods_final.txt`, `deployments_final.txt`, `images_final.txt`, `events_final.txt`, `deployments_final.yaml`, `services_final.txt`) confirma zero digest drift desde FASE 12 (sem-csmf/DE/portal nos digests FASE 12; bc-nssmf/sla-agent-layer/nasp-adapter nos digests FASE 6 preservados) com canonical READY 1/1, 2/2, 3/3 e 0 restarts nos pods da nova ReplicaSet — `runtime/final_runtime_validation.md` ALL MATCH. Cinco entregáveis principais foram produzidos: (1) `evidence_index/MASTER_EVIDENCE_INDEX.md` — índice mestre cobrindo FASES 0–13 com objetivo, evidência principal, resultado, status e PHASE*_REPORT.md de cada uma, mais cross-reference por concern (autoridade, fallback, runtime digests, ACCEPT, NASP, BC, SLA-Agent, calibração); (2) `scientific_summary/FINAL_SCIENTIFIC_SUMMARY.md` — 12 seções consolidando o que estava errado, como foi corrigido, evidência de runtime real (digest-only), não-regressão (7/7 eixos arquiteturais), ACCEPT recuperado (3/3, core_risk 1.0→~10⁻³), NASP (3/3 SUCCESS com nsi_id), BC (3/3 REGISTERED, fallback=False), tx_hash real on-chain (3 hashes únicos, block numbers 4268405/4268409/4268413), SLA-Agent (delegated/processed, fallback rate 0), calibração (offline + runtime), limitações remanescentes, e 10 componentes/fallbacks que **NÃO** podem ser removidos; (3) `scientific_summary/FINAL_RESPONSIBILITY_MATRIX.md` — 20 linhas authority × executor × evidência cobrindo semantic interpretation (SEM-CSMF), decision scoring (DE), orchestration authority (DE)/execution (NASP), lifecycle authority (DE)/pipeline propagation (Portal=relay), governance event (DE)/registration (BC-NSSMF), runtime reassessment (SLA-Agent), telemetry refresh, drift_summary, remediation_evidence, tx_hash propagation, public API (Portal=relay), calibration safety (PRs 1/2/3), e 4 fallbacks com seu owner; aggregated runtime invariants documentados; (4) `paper_alignment/PAPER_UPDATE_NOTES.md` — orientação detalhada para futura atualização do paper (Portal=relay, DE=authority, SLA-Agent=runtime reassessment executor, BC-NSSMF=governance registration executor, ACCEPT-path com evidência empírica, calibration fix apresentado como **maturação experimental** e não resultado científico primário, **não** declarar cleanup como feito, **declarar** digest-only runtime lineage com os 5 digests canônicos, reproducibility appendix com ponteiros para evidence_index/summary/matrix, hard "do not" list); (5) `cleanup_readiness/CLEANUP_READINESS_FINAL.md` — `CLEANUP_READY=true` reafirmado (6/6 gates FASE 12 satisfeitos), 10 componentes que devem permanecer (fallback revalidate Portal, kill switch `SEM_CSMF_MEMORY_UTIL_NORMALIZE`, defesa `_percent_or_degraded`, `memory_bytes` echo, `TELEMETRY_RANGES_V2`, `_merge_slice_multidomain_severity`, fallback BC degraded, digests FASE 6, SSOT, fallback matrix), 5 fallbacks que devem permanecer ativos, recomendação para cleanup incremental (re-baseline → orphan deployments → orphan pods → audit → per-removal digest deploy + ACCEPT campanha por remoção → só depois paper); (6) `rollback/FINAL_ROLLBACK_MAP.md` — histórico de digests pré-FASE-6 → FASE 6 → FASE 12 → atual, comandos de rollback por digest para cada serviço FASE 12, rollback de envs (`SLA_AGENT_REVALIDATE_URL`, `SEM_CSMF_MEMORY_UTIL_NORMALIZE`), rollback de arquivos FASE 11 (`calibration_fix/rollback/*_before.py`), referências aos relatórios FASE 6 (`deploy/rollback/ROLLBACK_REPORT.md`) e FASE 12 (`calibration_deploy/rollback/*.yaml`), decision tree por sintoma, nota de idempotência. Relatório final: `final_freeze/PHASE13_REPORT.md`. Cleanup **NÃO iniciado**; paper **NÃO atualizado**; fallbacks **preservados**; código/Helm/threshold/orchestration/governance/severity-merge/contratos **intactos**; sem `:latest`. Próxima ação válida (uma das duas, **sob nova autorização explícita**): **paper update phase** (aplicar `PAPER_UPDATE_NOTES.md` à dissertação e ao paper IEEE pendente) ou **dedicated cleanup phase** (incremental, digest-deploy-validated, começando por orphan `*-trisla` deployments e ReplicaSets antigos; cada remoção seguida por digest deploy + nova campanha ACCEPT que precisa replicar os critérios de aceitação da FASE 12). Não iniciar nenhuma das duas sem nova autorização.
