# ML-NSMF — Machine Learning-Based SLA Feasibility Prediction

## 1. Overview

The ML-NSMF (Machine Learning Network Slice Management Function) is responsible for predicting the feasibility of SLA acceptance based on real-time multi-domain network conditions and SLA requirements.

It operates as the predictive intelligence layer of the TriSLA architecture.

The module is designed to complement semantic validation performed by SEM-CSMF, converting structured intent and runtime telemetry into a probabilistic feasibility estimate suitable for downstream orchestration decisions.

---

## 2. Role in TriSLA

Pipeline:

SEM-CSMF -> NEST -> ML-NSMF -> Prediction -> Decision Engine

The module evaluates whether an SLA request is sustainable given current network conditions.

It is intentionally positioned between semantic formalization and policy decision, enabling data-driven risk assessment without replacing rule-based governance.

---

## 3. Core Function

The ML-NSMF computes a feasibility score:

**Formal Definition**

```text
score in [0,1]
```

representing the likelihood that an SLA can be fulfilled.

Lower scores indicate higher feasibility and lower violation risk; higher scores indicate elevated violation probability under current observed conditions.

---

## 4. Decision Interpretation

**Decision Function**

```text
Decision =
  ACCEPT        if score <= T_accept
  RENEGOTIATE   if T_accept < score < T_reject
  REJECT        if score >= T_reject
```

```text
T_accept = 0.4
T_reject = 0.7
```

These thresholds are operational references used by TriSLA decisioning and can be calibrated based on campaign evidence and deployment policy.

---

## 5. Documentation Structure

- `architecture/` -> system structure
- `model/` -> mathematical model
- `pipeline/` -> execution flow
- `interfaces/` -> Kafka integration
- `examples/` -> usage examples

---

## 6. Coherence with SEM-CSMF and Decision Engine

- Receives semantically validated NEST from SEM-CSMF (Kafka I-02)
- Produces feasibility prediction and explainability payload
- Publishes prediction to Decision Engine (Kafka I-03)

This preserves separation of concerns:

- SEM-CSMF: semantic consistency
- ML-NSMF: predictive feasibility
- Decision Engine: final SLA decision and policy enforcement

---

## 7. Summary

ML-NSMF provides predictive intelligence and explainability, enabling SLA-aware decision-making under dynamic network conditions.
