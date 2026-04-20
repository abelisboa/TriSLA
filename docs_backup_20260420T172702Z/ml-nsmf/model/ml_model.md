# ML-NSMF Decision Model

## 1. Problem Definition

Given:

- SLA requirements (latency, throughput, reliability)
- Current network state (RAN, Transport, Core)

Predict:

S = feasibility score in [0,1]

---

## 2. Input Variables

Let:

R_ran = PRB utilization  
R_transport = (latency, jitter)  
R_core = (CPU, memory)

SLA = (latency_req, throughput_req, reliability_req)

---

## 3. Feature Vector

X = f(SLA, R_ran, R_transport, R_core)

Example:

X = [
  latency,
  throughput,
  reliability,
  jitter,
  cpu_utilization,
  memory_utilization,
  bandwidth_available,
  active_slices
]

Typical engineered features include latency/throughput ratio, reliability-to-loss relations, and resource pressure terms.

---

## 4. Learned Function

The model approximates:

S = ML(X)

where ML is a trained model (Random Forest or similar).

In implementation terms, preprocessing (scaling/normalization) and model inference are applied as a chained function over X.

---

## 5. Interpretation

Higher S -> higher risk of SLA violation

Lower S -> higher confidence that SLA can be satisfied under current conditions.

---

## 6. Relation to Multi-Domain Model

The score implicitly encodes:

S approx alpha*R_ran + beta*R_transport + gamma*R_core

Where:

alpha, beta, gamma are learned weights (not fixed).

This interpretation is conceptual; practical models may capture nonlinear interactions and cross-domain dependencies.

---

## 7. Explainability

SHAP/LIME approximates:

S approx Sum(contribution(feature_i))

allowing interpretation of decision factors.

Explainability outputs should be treated as local/approximate reasoning aids, not strict causal proofs.

---

## 8. Decision Threshold Mapping

Operational threshold policy:

- S <= 0.4: ACCEPT
- 0.4 < S < 0.7: RENEGOTIATE
- S >= 0.7: REJECT

This mapping aligns model output with orchestration semantics expected by Decision Engine.

---

## 9. Conclusion

The ML model provides a data-driven approximation of SLA feasibility, integrating multi-domain conditions into a single decision metric while preserving interpretability through XAI methods.
