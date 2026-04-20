# ML-NSMF Model

## Architecture

- Core model: multiclass classifier (`RandomForestClassifier`) wrapped by `CalibratedClassifierCV`.
- Calibration strategy:
  - `isotonic` when dataset size is large enough.
  - `sigmoid` fallback for smaller training sets.
- Runtime output preserves TriSLA contract (`prediction` + `explanation`) and includes:
  - `predicted_decision_class`
  - `classifier_confidence`
  - `class_probabilities`
  - continuous `ml_risk_score` derived from calibrated class probabilities.

## Feature Set

Primary features:

- `latency`
- `throughput`
- `reliability`
- `jitter`
- `packet_loss`
- `cpu_utilization`
- `memory_utilization`
- `network_bandwidth_available`
- `active_slices_count`
- `slice_type_encoded`

Derived features:

- `latency_throughput_ratio`
- `reliability_packet_loss_ratio`
- `jitter_latency_ratio`
- `domain_pressure_score`
- `transport_instability_score`
- `core_pressure_score`
- `throughput_efficiency_score`
- `sla_stringency_score`
- `slice_domain_fit_score`

## Training Strategy

- Controlled rebuild with class coverage enforced for:
  - `ACCEPT`
  - `RENEGOTIATE`
  - `REJECT`
- Stratified split per class.
- Bootstrap controlled samples are allowed only for training support and are tagged/documented by origin.
- Bootstrap data is never used as scientific experimental evidence.

## Calibration Applied

- Probabilistic calibration via `CalibratedClassifierCV`.
- Calibration metadata tracked in `model_metadata.json`.

## Risk Formula

- Formula version: `v7_calibrated`
- Continuous risk in `[0, 1]`:
  - `risk = min(1, 0.5 * P(RENEGOTIATE) + 1.0 * P(REJECT))`

This formulation reduces early saturation and improves medium/high separability.

## Known Limitations

- Model quality still depends on runtime feature diversity in real runs.
- If runtime inputs collapse (e.g., weak excitation profiles), risk diversity may degrade even with a calibrated classifier.
- Slice-level behavior must be monitored continuously to avoid global-pass/local-collapse effects.

## Offline Validation (Gate)

Minimum offline gates:

- `macro_f1 >= 0.65`
- `balanced_accuracy >= 0.65`
- `recall_REJECT >= 0.50`
- monotonic risk profile (`risk_low < risk_medium < risk_high`)
- class risk ordering (`mean_ACCEPT < mean_RENEGOTIATE < mean_REJECT`)
- risk variability (`nunique > 10`, `std > 0`)
- slice stability (`URLLC`, `eMBB`, `mMTC` non-collapsed)

Promotion status is computed from these gates:

- `CRITICAL_FAILURE_ML_NOT_PROVEN`
- `PARTIAL_ML_SIGNAL`
- `ML_VALIDATED_FOR_PAPER`
