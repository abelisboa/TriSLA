# TriSLA Release History

## v3.10.0 — Scientific Baseline (2026-01-31)

**First fully validated TriSLA baseline**

### Features

- End-to-end SLA creation in NASP (5G/O-RAN-like environment)
- XAI exposed in Portal UI
- Blockchain-backed SLA registration (Hyperledger Besu with QBFT)
- Kafka-based observability and event replay
- ML-based risk prediction with feature importance

### Components

| Component | Version |
|-----------|---------|
| ui-dashboard | 3.10.0 |
| sem-csmf | 3.10.0 |
| ml-nsmf | 3.10.0 |
| decision-engine | 3.10.0 |
| bc-nssmf | 3.10.0 |
| sla-agent-layer | 3.10.0 |
| nasp-adapter | 3.10.0 |

### Validation

- Smoke test passed
- SLA submission: HTTP 200 with ACCEPT decision
- XAI: Risk score, confidence, feature importance
- Blockchain: Block confirmation
- Kafka: Event consumption verified

### Scientific Use

Used as experimental reference in the MSc dissertation:

> "TriSLA: An SLA-Aware Architecture for Explainable Network Slice Admission Control"

---

## Previous Versions

### v3.9.x (Development)

- Iterative development and stabilization
- Besu QBFT consensus implementation
- Smart contract deployment
- Portal XAI visualization

### v3.8.x (Functional Freeze)

- Initial functional baseline
- End-to-end pipeline validation
- Not validated on NASP

### v3.10.0 (Post-release cleanup)

- Removed legacy directories (monitoring/, trisla-portal/, configs/)
- Repository now reflects only the validated scientific baseline
- No impact on experiments or NASP environment
