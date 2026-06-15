# TriSLA Final Runtime Baseline Q1

Gerado em:
2026-05-06T20:35:29Z

## Estado do Cluster

- node1: Ready
- node2: Ready

## Monitoring

- Prometheus healthy
- Prometheus ready
- Query API operacional

## TriSLA Runtime

- portal-backend operacional
- I1 runtime operacional
- SLA submit operacional
- telemetry_snapshot operacional
- domain_actions operacional

## Runtime Images

Portal Backend:
ghcr.io/abelisboa/trisla-portal-backend@sha256:38347a28b053cf2374b5bbc7c65ea76f168ce3b7ecea9699c52036213bef6b4d

Operator:
ghcr.io/abelisboa/prometheus-operator@sha256:c910543fea6797d13e539538cd1454478c99d17c958362e77e0c22f8ddb6f110

Prometheus:
quay.io/prometheus/prometheus:v3.7.2 quay.io/prometheus-operator/prometheus-config-reloader:v0.88.1

## SLA Runtime

- HTTP 200 confirmado
- decision preservada
- telemetry_snapshot presente
- domain_actions presente

## Observações

- health/global restaurado para healthy
- domain_actions restaurado via package Python canônico
- recuperação realizada sem loaders artificiais
- runtime digest-only ativo para portal-backend
- Prometheus recuperado após reconciliação control-plane/operator

## Evidências

evidencias_FINAL_RUNTIME_BASELINE_Q1_20260506T203529Z

---

## Pós-baseline: closed-loop temporal P0→P2 (congelado)

O documento acima permanece o **âncora histórica Q1** (imagem `sha256:38347a28…`, runtime estável à data do baseline).

A evolução **temporal mínima** sobre esse baseline foi consolidada como cadeia **P0 → P1 → P2** (sem alterar a definição do snapshot Q1 original):

| Fase | Função | Digest portal-backend de referência (ensaio) |
|------|--------|-----------------------------------------------|
| P0 | `metadata.temporal_intent_trace` no `submit` | ver `analysis/P0_PATCH_APPLIED.md` (deploy opcional; rollback para Q1) |
| P1 | `POST /api/v1/sla/revalidate-telemetry`, `drift_summary` | `sha256:b7690cd9591be1017c20070926faccfd7ce93a73687892260757a8750c9439c4` |
| P2 | `metadata.remediation_evidence` no revalidate (declarativo) | `sha256:80dbb97785290951a6c56b0c41b3f8b6648a3d244b50711341b0be4a93316e6a` |

**Freeze consolidado:** `TEMPORAL_CLOSED_LOOP_P0_P2_FREEZE`  
**SSOT consolidação:** `analysis/CLOSED_LOOP_P0_P2_FINAL_STATUS.md`, `analysis/CLOSED_LOOP_EVOLUTION_CHAIN.md`, `analysis/RUNTIME_TEMPORAL_FEATURES.md`  
**Pacote de evidências:** `analysis/evidencias_TEMPORAL_CLOSED_LOOP_P0_P2_FREEZE_20260507T020000Z/`

Nomes canónicos citados em gates (`evidencias_TEMPORAL_TRACKING_P0_FREEZE_*`, `evidencias_TEMPORAL_REVALIDATION_P1_FREEZE_*`, `evidencias_Q1_RUNTIME_FREEZE_*`): quando ausentes como pastas no repositório, o conteúdo equivalente está em `analysis/P0_*.md`, `analysis/P1_*.md`, `analysis/VALIDATION_AND_FREEZE_GATES.md` e artefactos JSON/diff associados.
