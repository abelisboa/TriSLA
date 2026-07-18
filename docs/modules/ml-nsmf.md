# ML-NSMF

## Runtime Position In TriSLA Flow

Runtime position and cross-module flow ordering are defined by [`docs/modules/interfaces.md`](interfaces.md). This module document does not duplicate the full chain.

Canonical interface reference: [docs/modules/interfaces.md](interfaces.md).

Telemetry canonical reference: [docs/modules/telemetry.md](telemetry.md). ML-NSMF receives feature payloads from Decision Engine; its Prometheus client is not the prediction hot path.

> **Operational entry point** for the TriSLA Machine Learning Network Slice Management Function.
> Deep dives: [`docs/ml-nsmf/`](../ml-nsmf/README.md) (interfaces and examples).
> Implementation SSOT: `apps/ml-nsmf/`.

## Role (frozen architecture)

ML-NSMF is the **predictive intelligence layer**. It receives feature payloads from the Decision Engine, runs trained model inference, and returns risk scores and explainability metadata.

**ML-NSMF does not decide SLA.**  
**ML-NSMF produces prediction.**  
**The Decision Engine decides ACCEPT / RENEGOTIATE / REJECT.**

**Does:**

- Serve synchronous inference on `POST /api/v1/predict` (sole inference ingress)
- Load and run **BUNDLE-OP-001** artifacts (Random Forest regressor + scaler)
- Compute viability/risk scores, slice-adjusted risk, and XAI payloads
- Return structured `prediction` + `explanation` to the Decision Engine

**Does not:**

- Make final admission decisions (Decision Engine)
- Receive SLA submissions directly from Portal or SEM-CSMF on the production hot path
- Retrain models at runtime
- Run federated learning (not implemented)

Position in the frozen chain:

```text
Portal Backend → SEM-CSMF → Decision Engine POST /evaluate
                                    ↓ HTTP
                              ML-NSMF POST /api/v1/predict
                                    ↓ HTTP response
                              Decision Engine (_apply_decision_rules)
                                    ↓
                              SEM-CSMF → Portal → ...
```

## Operational baseline (Phase 47)

| Item | Value |
|------|-------|
| Deployment | `trisla-ml-nsmf` |
| Image | `ghcr.io/abelisboa/trisla-ml-nsmf` |
| Operational digest | `sha256:b0922b2199830a766a6fd999213583973bc8209862f39a949de2d18010017187` |
| Model bundle | **BUNDLE-OP-001** (MR-001, MR-002) |
| Active artifacts | `viability_model.pkl`, `scaler.pkl` |
| HTTP port | `8081` (cluster: `http://trisla-ml-nsmf:8081`) |
| App version | `3.10.0` (`apps/ml-nsmf/src/main.py`) |
| Wave 1 / Wave 3A | **Unchanged** at operational freeze |


## REST API catalog

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Liveness — includes active model status |
| GET | `/metrics` | Prometheus scrape |
| **POST** | **`/api/v1/predict`** | **SOLE INFERENCE INGRESS** — feature dict → prediction + explanation |

**Primary caller:** Decision Engine — `apps/decision-engine/src/ml_client.py` → `POST {ML_NSMF_HTTP_URL}/api/v1/predict`.

## Inference hot path

```text
Decision Engine (ml_client.predict_viability)
    ↓ HTTP POST /api/v1/predict
main.predict_risk
    ↓
DualLoadService.predict(metrics)          ← ACTIVE authority wrapper
    ↓
build_active_prediction(active RiskPredictor, metrics)
    ↓ normalize → predict (RandomForest) → predict_decision_class (optional)
    ↓ compute_slice_adjusted_risk → explain (SHAP/LIME/fallback)
    ↓ format_predict_response
    ↓ (side effect) PredictionProducer.send_prediction — no-op if Kafka off
HTTP response { latency_ms, prediction, explanation }
    ↓
Decision Engine parses → MLPrediction → admission rules
```

Detailed interface contract: [`docs/ml-nsmf/interfaces/interfaces.md`](../ml-nsmf/interfaces/interfaces.md).

## Request contract — consumed vs ignored

Payload is a JSON dict built by Decision Engine `_extract_features()` from SLA intent, context, and optional `telemetry_snapshot`.

### Consumed (feature builder)

| Field | Source | Used by |
|-------|--------|---------|
| `intent_id` | DE | Logging only |
| `latency`, `throughput`, `reliability`, `jitter`, `packet_loss` | SLA requirements | `RiskPredictor._feature_dict_from_metrics` |
| `slice_type`, `slice_type_encoded` | Intent | Encoding + slice adjustment |
| `cpu_utilization`, `memory_utilization` | SLA requirements / defaults | Base features + v3 derived |
| `network_bandwidth_available` | SLA / defaults | Base + derived |
| `active_slices_count` | Context / NEST / default | Base features |

### Sent — NOT CONSUMED

Decision Engine forwards these from `telemetry_snapshot`; **`RiskPredictor` does not read them** today:

| Field | Status |
|-------|--------|
| `ran_prb_utilization` | **SENT / NOT CONSUMED** |
| `transport_latency_ms` | **SENT / NOT CONSUMED** |
| `core_cpu_utilization` | **SENT / NOT CONSUMED** |
| `core_memory_utilization` | **SENT / NOT CONSUMED** |

PRB and multi-domain admission pressure is applied in the **Decision Engine** from `telemetry_snapshot`, not in ML feature extraction.

## Response contract

Top-level:

| Field | Description |
|-------|-------------|
| `latency_ms` | Inference wall time |
| `prediction` | Model outputs (see below) |
| `explanation` | XAI payload (see below) |

### `prediction` (key fields)

| Field | Description |
|-------|-------------|
| `risk_score` | Primary risk (raw path before DE slice use) |
| `viability_score` | Regressor output (0–1, higher = more viable) |
| `risk_level` | `low` / `medium` / `high` (from slice-adjusted score) |
| `confidence` | Regressor-derived confidence |
| `raw_risk_score` | Pre-adjustment risk |
| `slice_adjusted_risk_score` | **Operational ML final score** for DE policy |
| `predicted_decision_class` | ACCEPT / RENEGOTIATE / REJECT (if classifier loaded) |
| `classifier_confidence` / `confidence_score` | Classifier probability (if loaded) |
| `classifier_loaded` | Whether `decision_classifier.pkl` was used |
| `slice_domain_xai.top_factors` | Top domain factors |
| `slice_domain_xai.dominant_domain` | RAN / Transport / Core |
| `model_used` | `true` when regressor ran (S34.2 — no mock fallback) |
| `risk_formula` | `v7_calibrated` when classifier path active; else regression-only |

### `explanation` (key fields)

| Field | Description |
|-------|-------------|
| `method` | `SHAP`, `LIME`, `feature_importance`, or `XAI` |
| `features_importance` | Normalized feature weights |
| `reasoning` | Text summary |
| `top_factors` | Slice-adjusted factor list |
| `dominant_domain` | Dominant stress domain |
| `shap_available` / `lime_available` | Runtime flags |

## Models

| Model | Artifact | Status |
|-------|----------|--------|
| **Random Forest Regressor** | `viability_model.pkl` | **ACTIVE** — BUNDLE-OP-001 production runtime |
| **StandardScaler** | `scaler.pkl` | **ACTIVE** — required at startup (S34.2) |
| **Decision classifier** | `decision_classifier.pkl` | **CONDITIONAL** — used when the optional local artifact is supplied; regression-only path when absent |
| LSTM | — | **NOT IMPLEMENTED** |
| GRU | — | **NOT IMPLEMENTED** |
| XGBoost | — | **NOT IMPLEMENTED** |
| Federated Learning | — | **NOT IMPLEMENTED** |
| Mock / fallback model | — | **REMOVED** (missing model/scaler → startup failure) |

Production regressor: `sklearn.ensemble.RandomForestRegressor` (trained offline via `apps/ml-nsmf/training/train_model.py`).

## Feature engineering

### Base features

From `_feature_dict_from_metrics`: latency, throughput, reliability, jitter, packet_loss, cpu_utilization, memory_utilization, network_bandwidth_available, active_slices_count, slice_type_encoded, plus ratio features (latency_throughput_ratio, reliability_packet_loss_ratio, jitter_latency_ratio).

### Derived v3 features

From `_derived_sla_features_v3`:

| Feature | Role |
|---------|------|
| `domain_pressure_score` | Aggregate domain stress |
| `transport_instability_score` | Jitter / loss / latency pressure |
| `core_pressure_score` | CPU + memory pressure |
| `throughput_efficiency_score` | Throughput vs available bandwidth |
| `sla_stringency_score` | Strictness of SLA requirements |
| `slice_domain_fit_score` | Slice-type fit heuristic |

### Slice risk adjustment

Post-model: `slice_risk_adjustment.compute_slice_adjusted_risk` blends raw model risk with slice-weighted domain stress (URLLC / eMBB / mMTC weights) → **`slice_adjusted_risk_score`** (operational ML output consumed by DE), `top_factors`, `dominant_domain`.

## Prediction logic

| Step | Logic |
|------|-------|
| Normalize | `scaler.transform` on feature vector |
| Regressor | `viability_score = model.predict(X)` |
| Risk | `risk_score = clamp(1 - viability_score, 0, 1)` |
| Confidence | `1 - abs(viability - 0.5) * 2`, clamped [0.5, 1.0] |
| Classifier (if loaded) | Multiclass ACCEPT/RENEG/REJECT + `confidence_score` |
| Raw risk selection | Classifier formula if `classifier_loaded`; else regression `risk_score` |
| Slice adjust | `slice_adjusted_risk_score` = blend(raw, domain_stress, α=0.42) |
| Risk level | On adjusted score: >0.7 high, >0.4 medium, else low |

**Decision thresholds (ACCEPT/RENEG/REJECT) are applied by the Decision Engine**, not ML-NSMF.

## Explainability runtime truth

| Capability | Status |
|------------|--------|
| **SHAP** (`TreeExplainer`) | **IMPLEMENTED / CONDITIONAL** — runs if `shap` available and explainer succeeds |
| **LIME** (`LimeTabularExplainer`) | **IMPLEMENTED / CONDITIONAL** — fallback if SHAP fails; uses synthetic random background data |
| **Feature importance (metadata)** | **IMPLEMENTED / FALLBACK** — from `model_metadata.training_history` when SHAP/LIME unavailable |
| **top_factors** | **ACTIVE** — from `slice_risk_adjustment`, exported in prediction + explanation |
| **dominant_domain** | **ACTIVE** — exported in `slice_domain_xai` and explanation |
| **reasoning** | **ACTIVE** — text in `explanation.reasoning` |
| **features_importance** | **ACTIVE** when any explain method succeeds |

Do **not** document SHAP or LIME as always executing on every request.

Legacy `ml_nsmf.explain_prediction` and Kafka `send_xai_explanation` exist in repo but are **not** on the `/api/v1/predict` hot path.

## Federated learning runtime truth

**NOT IMPLEMENTED**

No federated modules, aggregation, client models, or global model sync exist in `apps/ml-nsmf/`. Any dissertation narrative on FL is **TRACEABILITY_ONLY** with no runtime backing.

## Training runtime truth

**OFFLINE ONLY**

| Mode | Runtime |
|------|---------|
| Online learning | **NO** |
| Continuous learning | **NO** |
| Scheduled retraining | **NO** |
| Runtime retraining | **NO** |
| Manual offline training | **YES** — `apps/ml-nsmf/training/train_model.py` |

Artifacts are baked into the container image at deploy; loaded once at service startup.

## Active model runtime

| Component | Status |
|-----------|--------|
| `DualLoadService` | **ACTIVE** — wraps `/api/v1/predict` with the single public active model |
| Active predictor (BUNDLE-OP-001) | **ACTIVE** — sole model loaded and sole decision authority |
| Candidate, replay, and shadow workflows | **NOT INCLUDED** in the public release |

## Integrations

| Integration | Status |
|-------------|--------|
| **Decision Engine** | **ACTIVE** — HTTP `POST /api/v1/predict` per `/evaluate` |
| **PredictionProducer** (Kafka) | **CONDITIONAL** — called after predict; **CONDITIONAL / NOT HOT PATH** (`KAFKA_ENABLED=false`) |
| **PrometheusClient** | **NOT HOT PATH** — instantiated in `main.py`, never called on predict |
| **MetricsConsumer** (Kafka) | **NOT HOT PATH** — instantiated, never called |
| **SEM-CSMF direct** | **NOT HOT PATH** — no Kafka intake from SEM in production |

## Observability

| Layer | Implementation |
|-------|----------------|
| **Prometheus** | `trisla_http_requests_total`, `trisla_http_request_duration_seconds`; `GET /metrics` |
| **OTEL** | FastAPI instrumentation; `OTEL_EXPORTER_OTLP_ENDPOINT` |
| **Spans** | `predict_risk`, `normalize_metrics`, `explain_prediction`, `send_prediction_i03` |
| **Logs** | `[ML_PREDICT]`, `[ML] Loading...`, `[ML_ACTIVE]` |
| **Inference metrics** | `prediction_latency_ms`, `model_used` in response body |

## Persistence

| Store | Notes |
|-------|-------|
| Model artifacts | Active model and scaler pickle files under `/app/models/` or explicit active-path variables |
| XAI logs | Optional `XAI_LOG_DIR`, `XAI_CSV_DIR` — not wired in main hot path |

**NO SQL · NO ORM · NO FEATURE STORE**

## Legacy and non-hot paths

| Component | Status |
|-----------|--------|
| `ml_nsmf.py` | **LEGACY** — not imported by `main.py` |
| Kafka consumer (`nasp-metrics`) | **CONDITIONAL / NOT HOT PATH** |
| Kafka producer (`trisla-ml-predictions`) | **CONDITIONAL** — fire-and-forget after HTTP response |
| SEM → Kafka → ML narrative | **OBSOLETE** — not production SSOT |

## Key environment variables

| Variable | Default | Role |
|----------|---------|------|
| `ML_NSMF_HTTP_URL` (DE side) | `http://127.0.0.1:8081` | DE client target |
| `ML_ACTIVE_MODEL_PATH` | `/app/models/viability_model.pkl` | Active regressor |
| `ML_ACTIVE_SCALER_PATH` | `/app/models/scaler.pkl` | Active scaler |
| `ML_DECISION_CLASSIFIER_PATH` | optional | Classifier override |
| `KAFKA_ENABLED` | `false` | Async prediction publish |

## Related documentation

| Topic | Location |
|-------|----------|
| HTTP interface (I-05) | [`docs/ml-nsmf/interfaces/interfaces.md`](../ml-nsmf/interfaces/interfaces.md) |
| Offline training examples | [`docs/ml-nsmf/examples/usage_examples.md`](../ml-nsmf/examples/usage_examples.md) |
| DE admission (consumer) | [`docs/modules/decision-engine.md`](decision-engine.md) |

## Canonical Telemetry Reference

Canonical telemetry reference: docs/modules/telemetry.md defines telemetry_snapshot freshness and the distinction between runtime telemetry and ML feature objects.

## Canonical Observability Reference

Canonical observability reference: docs/modules/observability.md defines ML-NSMF metrics, OTEL tracing, health, dashboards, and alerting boundaries.
