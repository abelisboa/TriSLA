# TriSLA Final Audit For Paper

Auditoria factual do repositório e runtime, voltada para seções **Architecture** e **Prototype**.

Escopo auditado:
- Código em `apps/`
- Documentação em `docs/`
- Runtime Kubernetes em namespace `trisla`

## 1) Interfaces Reais

Tabela baseada em endpoints/de chamadas HTTP observadas no código.

| Module A | Module B | Endpoint | Payload (evidência) | Response (evidência) |
|---|---|---|---|---|
| Portal Frontend | Portal Backend | `POST /api/v1/sla/interpret` | `SLAInterpretRequest`: `intent_text`, `tenant_id` (`apps/portal-backend/src/schemas/sla.py`) | resposta de interpretação (campos semânticos) via `apps/portal-backend/src/routers/sla.py` |
| Portal Frontend | Portal Backend | `POST /api/v1/sla/submit` | `SLASubmitRequest`: `template_id`, `form_values`, `tenant_id` (`apps/portal-backend/src/schemas/sla.py`) | `SLASubmitResponse` com `decision`, `ml_prediction`, `tx_hash`, `block_number`, `metadata` (`apps/portal-backend/src/schemas/sla.py`) |
| Portal Backend | SEM-CSMF | `POST /api/v1/interpret` | `{"intent": intent_text, "tenant_id": tenant_id}` (`apps/portal-backend/src/services/nasp.py`) | JSON usado para `service_type` e latências (`apps/portal-backend/src/services/nasp.py`) |
| Portal Backend | SEM-CSMF | `POST /api/v1/intents` | `intent_payload` com `service_type`, `intent`, `tenant_id`, `sla_requirements`, `metadata` opcional (`apps/portal-backend/src/services/nasp.py`) | `sem_result` (pipeline decisão/orquestração consolidado no backend) (`apps/portal-backend/src/services/nasp.py`) |
| Portal Backend | NASP Adapter | `POST /api/v1/nsi/instantiate` | `orch_payload` (`nsiId`, perfil/sla e metadados de orquestração) (`apps/portal-backend/src/services/nasp.py`) | `nasp_orchestration_response` com `success`, `nsi_id`, `http_status` (`apps/portal-backend/src/services/nasp.py`) |
| SEM-CSMF | Decision Engine | `POST /evaluate` | `DECISION_ENGINE_URL` default `...:8082/evaluate` + payload de decisão (`apps/sem-csmf/src/decision_engine_client.py`) | resposta de decisão consumida e repassada por SEM-CSMF (`apps/sem-csmf/src/decision_engine_client.py`) |
| Decision Engine | ML-NSMF | `POST /api/v1/predict` | features extraídas de `DecisionInput` (`apps/decision-engine/src/ml_client.py`) | `prediction` e `explanation` (`apps/ml-nsmf/src/main.py`, `apps/decision-engine/src/ml_client.py`) |
| Portal Backend | Prometheus API (via router local) | `GET /api/v1/prometheus/*` | queries de telemetria (`apps/portal-backend/src/telemetry/collector.py`, `promql_ssot.py`) | valores para `telemetry_snapshot` (`apps/portal-backend/src/routers/sla.py`) |
| Portal Backend | SLA-Agent Layer (opcional) | URL em `SLA_AGENT_PIPELINE_INGEST_URL` | payload com `intent_id`, `sla_id`, `decision`, `lifecycle`, latências (`apps/portal-backend/src/routers/sla.py`) | status de ingestão/SLO em `metadata_out["sla_agent_ingest"]` (`apps/portal-backend/src/routers/sla.py`) |

Observação:
- Além das rotas acima, existem endpoints adicionais em `nasp-adapter`, `bc-nssmf`, `sla-agent-layer`, `sem-csmf`, todos listados via decorators `@app.post/@app.get/@router.post`.

## 2) Pipeline Real (Cadeia SLA)

Sequência reconstruída por chamadas explícitas no código:

1. **User/Frontend** envia `POST /api/v1/sla/interpret` e/ou `POST /api/v1/sla/submit` para `portal-backend`.
2. `portal-backend` interpreta via `SEM-CSMF /api/v1/interpret`.
3. `portal-backend` envia intent técnico via `SEM-CSMF /api/v1/intents`.
4. `SEM-CSMF` aciona `Decision Engine /evaluate`.
5. `Decision Engine` chama `ML-NSMF /api/v1/predict`.
6. `portal-backend` coleta telemetria e popula `metadata.telemetry_snapshot`.
7. Se decisão for `ACCEPT`, `portal-backend` tenta orquestração via `NASP Adapter /api/v1/nsi/instantiate`.
8. Resultado final retorna no `SLASubmitResponse` com campos de decisão e blockchain (`tx_hash`, `block_number`) quando presentes.

Resumo pedido:

`User -> Portal Backend -> SEM-CSMF -> Decision Engine -> ML-NSMF -> (NASP Adapter/orquestração) -> Network -> Telemetry -> resposta final`

## 3) Protótipo Implementado (Runtime Atual)

Fonte: `kubectl -n trisla get deploy -o wide` e `kubectl -n trisla get pods -o wide`.

Deployments observados no namespace `trisla`:

- `kafka`
- `trisla-analytics-adapter`
- `trisla-bc-nssmf`
- `trisla-besu`
- `trisla-blockchain-exporter`
- `trisla-decision-engine`
- `trisla-decision-engine-trisla`
- `trisla-iperf3-server`
- `trisla-ml-nsmf`
- `trisla-nasp-adapter`
- `trisla-network-exporter`
- `trisla-otel-collector`
- `trisla-portal-backend`
- `trisla-portal-backend-trisla`
- `trisla-portal-frontend`
- `trisla-prb-simulator`
- `trisla-ran-ue-upf-proxy`
- `trisla-sem-csmf`
- `trisla-sem-csmf-trisla`
- `trisla-sla-agent-layer`
- `trisla-tempo`
- `trisla-traffic-exporter`
- `trisla-ui-dashboard`

Pods relevantes em execução:
- `trisla-portal-backend-*`, `trisla-sem-csmf-*`, `trisla-ml-nsmf-*`, `trisla-decision-engine-*`, `trisla-nasp-adapter-*`, `trisla-bc-nssmf-*`, `trisla-sla-agent-layer-*`.

## 4) Reprodutibilidade

- Repo URL: `https://github.com/abelisboa/TriSLA.git`
- Commit auditado: `d3af0457a857895aa8e63f8cdd703f50d68769dd`

Dataset paths (`*dataset*.csv`) encontrados:

- `evidencias_resultados_trisla_final/dataset/dataset_v3_ssot.csv`
- `evidencias_baseline_oficial/dataset_final_trisla_e2e.csv`
- `processed/final_dataset.csv`
- `processed/final_dataset_v2.csv`
- `processed/final_dataset_v3.csv`
- `evidencias_resultados_trisla_baseline_v11/dataset/dataset_trisla_final.csv`
- `evidencias_resultados_trisla_baseline_v13/dataset/final_dataset_v6.csv`
- `evidencias_resultados_trisla_baseline_v13_1/dataset/final_dataset_v6_1.csv`
- `evidencias_resultados_trisla_baseline_v13_2/dataset/final_dataset_v6_2_raw.csv`
- `evidencias_resultados_trisla_baseline_v13_2/dataset/final_dataset_v6_2_clean.csv`
- `evidencias_resultados_trisla_baseline_v13_2/dataset/final_dataset_v6_2_by_slice.csv`
- `evidencias_prompt8_audit_v2_20260420T212259Z/dataset_final_validado.csv`
- `evidencias_prompt9_slice_aware/dataset_final_v9.csv`
- e outros históricos listados no comando de auditoria.

## 5) Gaps Finais (Objetivos e Verificáveis)

- **Interface formal ausente no código:** não há nomenclatura explícita SI/MI/DI/GI/TI como contrato arquitetural; comunicação está em rotas REST e env vars.
- **Pipeline distribuído parcialmente indireto:** `portal-backend` não chama `decision-engine /evaluate` diretamente no caminho principal; delega ao SEM-CSMF (`apps/portal-backend/src/services/nasp.py`).
- **Múltiplas variantes paralelas no runtime:** coexistem deployments `*-trisla` junto de variantes base para módulos centrais (ex.: `portal-backend`, `sem-csmf`, `decision-engine`).
- **Dataset canônico único não está imposto por estrutura:** coexistem múltiplos `final_dataset*`/`dataset*` em diferentes campanhas.
- **Documentação consolidada da cadeia fim-a-fim ainda dispersa:** evidências existem, mas estão fragmentadas entre runbooks, auditorias e scripts.

---

Uso recomendado no paper:
- **Architecture:** usar a tabela de interfaces e pipeline real desta auditoria.
- **Prototype:** usar lista de deployments/pods e commit remoto para rastreabilidade.
