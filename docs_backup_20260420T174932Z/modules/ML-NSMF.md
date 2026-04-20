# ML-NSMF — FINAL STATE (PRODUCTION)

## Overview

The ML-NSMF module is the intelligence core of TriSLA.

It now supports full decision space:
- ACCEPT
- RENEGOTIATE
- REJECT

with continual learning enabled.

---

## Model

- Type: RandomForestRegressor
- Versioning: enabled (registry/)
- Current model: model_v2.pkl

---

## Dataset

- Real data + controlled stress
- Size: 110 rows
- Balanced distribution

---

## Decision Capability

- ACCEPT: ✔
- RENEGOTIATE: ✔
- REJECT: ✔

---

## Continual Learning

- Automatic retraining every 6h
- Validation gates:
  - R² > 0.9
  - all classes present
  - distribution constraints

- Safe promotion:
  - fallback model preserved
  - promotion only if validated

---

## Engineering Status

The ML module is:

- operational
- adaptive
- production-ready

---

## SLA-aware v3 (local validation — 2026-03-23)

### Multi-domain view

- Domínios lógicos: **RAN** (latência, `slice_type`, escala), **Transport** (jitter, perda, throughput, banda), **Core** (CPU/memória).
- `prb_utilization` **não** está no dataset consolidado atual — documentado em `artifacts/multidomain_contribution.json` (`missing_columns_documented`).
- Auditoria: `scripts/trisla_audit_multidomain_contribution.py` → `artifacts/multidomain_contribution.json`, `artifacts/multidomain_feature_importance.csv`.

### Slice-adjusted risk (preserva bruto)

- Módulo: `apps/ml-nsmf/src/slice_risk_adjustment.py`
- Resposta HTTP (`/api/v1/predict`): `raw_risk_score`, `slice_adjusted_risk_score`, `risk_score` (= bruto), `risk_level` derivado do ajustado.
- Campos XAI parciais em `slice_domain_xai` (domínio dominante, top fatores).

### Features derivadas v3

- `domain_pressure_score`, `transport_instability_score`, `core_pressure_score`, `throughput_efficiency_score`, `sla_stringency_score`, `slice_domain_fit_score`
- Construção: `scripts/trisla_v3_features.py` + `scripts/trisla_build_ml_dataset.py` (dados reais).
- **RTT** não disponível no dataset legado → não incluído (sem dados inventados).

### Dataset balanceado (v3)

- Pipeline: stress renovado (`scripts/trisla_generate_stress_dataset.py`) → merge (`scripts/trisla_merge_datasets.py`) → balance (`scripts/trisla_balance_dataset.py`).
- Saída: `artifacts/ml_training_dataset_v3.csv`, relatório `artifacts/dataset_balance_report.json`.
- Regra: não remover linhas reais; apenas stress pode ser reduzido. Com N pequeno, o teto de 55% por classe pode não ser atingível se os dados reais concentrarem uma classe.

### Treino local v3 (sem promover registry)

- Script: `scripts/trisla_train_real_model_v3.py`
- Artefatos: `artifacts/viability_model_v3.pkl`, `artifacts/scaler_v3.pkl`, `artifacts/model_evaluation_v3.json`, `artifacts/model_metadata_v3.json`, `artifacts/model_decision_matrix_v3.csv`.
- **Status local atual:** gate de promoção **não** passou (R² teste ~0.27, N=110, alta variância; classes preditas concentradas). É necessário **mais amostras reais** e/ou revisão de stress antes de promover.
- `registry/current_model.txt` e modelo em `apps/ml-nsmf/models/` **não** foram alterados por estes scripts.

### Testes locais por slice

- `scripts/trisla_slice_behavior_tests.py` → `artifacts/local_slice_behavior_tests.json`, `artifacts/xai_samples_v3.json`.

### Observabilidade

- Treino local requer `scikit-learn` (ex.: `python3 -m venv .venv && .venv/bin/pip install scikit-learn pandas numpy`).

---

## FASE 11 — Arquitetura híbrida (regressão + classificação)

### Papel de cada modelo

- **Regressão** (`viability_model*.pkl`): score contínuo de viabilidade / risco bruto → base para **XAI** e `slice_adjusted_risk_score`.
- **Classificação** (`artifacts/decision_classifier.pkl`, opcional em runtime via `ML_DECISION_CLASSIFIER_PATH` ou arquivo em `artifacts/`): prediz **ACCEPT / RENEGOTIATE / REJECT** com **probabilidade da classe** (`classifier_confidence`).

### Resposta ML (`/api/v1/predict`)

- `predicted_decision_class`, `classifier_confidence`, `classifier_loaded` além do bloco de regressão existente.

### Scripts

| Script | Função |
|--------|--------|
| `scripts/trisla_create_classification_target.py` | `ml_training_dataset_v4.csv` + coluna `decision_label` |
| `scripts/trisla_train_classifier.py` | `decision_classifier.pkl` + métricas / matriz de confusão |
| `scripts/trisla_validate_hybrid_model.py` | `hybrid_decision_analysis.json`, `hybrid_xai_samples.json` |
| `scripts/trisla_hybrid_slice_behavior_tests.py` | `hybrid_slice_behavior_tests.json` |

### Limitações

- O target `decision_label` depende de `risk_score` + `slice_adjusted_risk` + thresholds; se o dataset não cobrir REJECT, o classificador pode ser binário.
- Gate de distribuição (10%–70% por classe) exige dados equilibrados.

---

## FASE 12 — Destravar classe REJECT (local)

### Causa raiz do v4 sem REJECT

- O `decision_label` em `ml_training_dataset_v4.csv` estava corretamente alinhado ao engine (risco ajustado + thresholds por slice), mas a massa de exemplos tinha `slice_adjusted_risk` abaixo do limiar de rejeição.
- Auditoria (`artifacts/labeling_audit_v4.json`) confirmou: `label_mismatch_count = 0`, sem clipping/rounding/fallback indevido.

### Estratégia adotada

- Enriquecimento supervisionado controlado com `scripts/trisla_generate_reject_dataset.py`.
- Casos plausíveis por slice e multi-domínio:
  - URLLC: latência/jitter/perda altos + confiabilidade degradada.
  - eMBB: throughput/banda muito baixos + pressão de core/congestionamento.
  - mMTC: alta carga (`active_slices_count`) + alta pressão de core/domínio.
- Fusão em `ml_training_dataset_v5.csv` com preservação do v4 integral.

### Resultado v5

- Distribuição pré-treino (`class_distribution_v5_pretrain.json`): ACCEPT ~42.3%, RENEGOTIATE ~13.8%, REJECT ~43.9%.
- Classificador v5 (`decision_classifier_metrics_v5.json`):
  - accuracy ~0.939
  - macro-F1 ~0.900
  - recall(REJECT) = 1.0
  - 3 classes presentes (ACCEPT/RENEGOTIATE/REJECT)
- Artefatos v5:
  - `artifacts/decision_classifier_v5.pkl`
  - `artifacts/decision_classifier_metrics_v5.json`
  - `artifacts/classifier_confusion_matrix_v5.csv`
  - `artifacts/class_distribution_v5.json`
  - `artifacts/hybrid_decision_analysis_v5.json`
  - `artifacts/hybrid_xai_samples_v5.json`
  - `artifacts/hybrid_slice_behavior_tests_v5.json`

## Evidence — full closure campaign

Os logs de `trisla-ml-nsmf` entram na matriz de rastreio da campanha (`scripts/e2e/trisla_full_closure_campaign.py` + `trisla_closure_common.trace_hits`) via presença do `intent_id` após cada predição servida ao Decision Engine.
