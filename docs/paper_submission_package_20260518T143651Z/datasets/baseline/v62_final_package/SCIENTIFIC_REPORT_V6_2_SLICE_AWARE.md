# Scientific report — V6.2 slice-aware isolation protocol

## Protocol
- Per submit: Prometheus instant **before** (PRB/RTT/jitter/core per SSOT-style queries) and `telemetry_snapshot` **after** from submit response.
- `sample_valid_for_scenario` flags rows where control domains stayed within operational bands defined in `analysis/acceptance_bands_v6_2.json` (phase0).

## Outputs
- Raw rows: 180 (see `dataset/final_dataset_v6_2_raw.csv` + JSON columns).
- Clean rows: 141.
- By slice: `dataset/final_dataset_v6_2_by_slice.csv`.

## Summary table (by slice × block)
```json
[
  {
    "slice_type": "URLLC",
    "scenario_block": "URLLC_transport_bad",
    "n": 30,
    "n_valid": 9,
    "valid_rate": 0.3,
    "mean_score_all": 0.8804454457849463,
    "mean_score_valid_only": 0.6873202886738352
  },
  {
    "slice_type": "URLLC",
    "scenario_block": "URLLC_transport_good",
    "n": 30,
    "n_valid": 21,
    "valid_rate": 0.7,
    "mean_score_all": 0.6882139614623656,
    "mean_score_valid_only": 0.6920227580645162
  },
  {
    "slice_type": "eMBB",
    "scenario_block": "eMBB_high_prb",
    "n": 20,
    "n_valid": 20,
    "valid_rate": 1.0,
    "mean_score_all": 0.73,
    "mean_score_valid_only": 0.73
  },
  {
    "slice_type": "eMBB",
    "scenario_block": "eMBB_low_prb",
    "n": 20,
    "n_valid": 18,
    "valid_rate": 0.9,
    "mean_score_all": 0.7453477525357142,
    "mean_score_valid_only": 0.7467062892658729
  },
  {
    "slice_type": "eMBB",
    "scenario_block": "eMBB_mid_prb",
    "n": 20,
    "n_valid": 17,
    "valid_rate": 0.85,
    "mean_score_all": 0.6716241735714286,
    "mean_score_valid_only": 0.6702121875210084
  },
  {
    "slice_type": "mMTC",
    "scenario_block": "mMTC_core_heavy",
    "n": 30,
    "n_valid": 28,
    "valid_rate": 0.9333333333333333,
    "mean_score_all": 0.6628696577727274,
    "mean_score_valid_only": 0.6635577506655845
  },
  {
    "slice_type": "mMTC",
    "scenario_block": "mMTC_core_light",
    "n": 30,
    "n_valid": 28,
    "valid_rate": 0.9333333333333333,
    "mean_score_all": 0.662354961248485,
    "mean_score_valid_only": 0.6641093101038962
  }
]
```

## Interpretation
- Compare valid rates across blocks; low validity often flags measurement alignment (before vs after source mismatch), not only workload failure.
- Use clean-only plots for slice-sensitivity claims; raw retains full operational trace for audit.
- If `mMTC_core_heavy` shows zero valid rows, re-run after updating the campaign script (stress_active gate vs incompatible CPU cross-compare).