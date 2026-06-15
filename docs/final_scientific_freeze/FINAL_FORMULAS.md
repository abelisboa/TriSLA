# Final Formulas (Frozen)

Source: `docs/TRISLA_MASTER_SSOT_RUNTIME_BASELINE_V1.md`, `decision_score_mode.py`, `feasibility_runtime.py`.

| Term | Formula |
|------|---------|
| ran_prb_goodness | clamp01(1 − PRB_util/100) |
| transport_rtt_goodness | clamp01(1 − RTT_ms / RTT_REF), RTT_REF=12.21 ms |
| resource_pressure_v1 | 0.4·PRB_norm + 0.3·RTT_norm + 0.3·CPU_norm (renormalized) |
| feasibility_goodness | clamp01(1 − (ml_risk + resource_pressure)/2) |
| resource_headroom_goodness | clamp01(1 − resource_pressure) |
| decision_score | Σ(wᵢ·gᵢ) / Σwᵢ over active terms |

**Do not alter.**
