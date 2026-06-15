# Figure Runtime Validation

### F01
- Proves: Score evolves with telemetry regimes
- Reviewer-safe: Digest-frozen score_mode only
- Do NOT infer: Not closed-loop orchestration
- Notes: —

### F02
- Proves: PRB gates structure decisions
- Reviewer-safe: Frozen HARD_PRB thresholds
- Do NOT infer: Not slice-specific admission proof alone
- Notes: —

### F03
- Proves: Pressure/feasibility co-evolve at admission
- Reviewer-safe: Snapshot formula
- Do NOT infer: Not post-orchestration pressure
- Notes: —

### F04
- Proves: Admission path latency by slice
- Reviewer-safe: HTTP elapsed only
- Do NOT infer: Not orchestration-only latency
- Notes: —

### F05
- Proves: RAN/transport/core visible at runtime
- Reviewer-safe: Observability not balanced causality
- Do NOT infer: Not transport dominance
- Notes: —

### F06
- Proves: Contribution terms from frozen weights
- Reviewer-safe: Real contrib_* fields
- Do NOT infer: Not independent domain causality
- Notes: —

### F07
- Proves: Temporal PRB-score anti-correlation tendency
- Reviewer-safe: Campaign timestamps
- Do NOT infer: Not causal orchestration
- Notes: —

### F08
- Proves: Sequential E2E submit→NASP→BC
- Reviewer-safe: Real batch timings
- Do NOT infer: Not continuous NSI timeline
- Notes: —

### F09
- Proves: Latency under orch_probe epochs
- Reviewer-safe: NCM campaign
- Do NOT infer: Not admission recompute
- Notes: —

### F10
- Proves: SEM store counts at probe time
- Reviewer-safe: Snapshot not time series
- Do NOT infer: Not CRD churn over time
- Notes: cluster snapshot at LIFE-EXEC-03 probe — not a continuous NSI time series

### F11
- Proves: Weak coupling orch latency vs pressure
- Reviewer-safe: Real NCM rows
- Do NOT infer: Not orchestration-driven pressure
- Notes: —

### F12
- Proves: BC commits after successful submits
- Reviewer-safe: tx_hash present
- Do NOT infer: Not smart-contract performance benchmark
- Notes: —

### F13
- Proves: Score range across slices same state
- Reviewer-safe: network_state_id groups
- Do NOT infer: Not admission label divergence
- Notes: —

### F14
- Proves: Score stable vs pressure under orch
- Reviewer-safe: NCM dataset
- Do NOT infer: Not proving zero latency
- Notes: —

### F15
- Proves: Forward vs absent feedback paths
- Reviewer-safe: Conceptual from freeze
- Do NOT infer: Not measured latency on diagram
- Notes: frozen audit model — not simulated telemetry

### F16
- Proves: Validated absent feedback paths
- Reviewer-safe: Conceptual from code audit
- Do NOT infer: Not live packet trace
- Notes: —
