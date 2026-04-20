# ML-NSMF Decision Model

## 1. Problem Definition

Given:

- SLA requirements (latency, throughput, reliability)
- Current network state (RAN, Transport, Core)

Predict:

**Formal Definition**

$$
score \in [0,1]
$$

---

## 2. Input Variables

Let:

$$
R_{ran} = PRB_{utilization}
$$

$$
R_{transport} = (latency, jitter)
$$

$$
R_{core} = (cpu, memory)
$$

$$
SLA = (latency_{req}, throughput_{req}, reliability_{req})
$$

---

## 3. Feature Vector

**Formal Definition**

$$
X = f(SLA, R_{ran}, R_{transport}, R_{core})
$$

Example:

**Feature Vector Example**

$$
X = [
latency,\ throughput,\ reliability,\ jitter,\ cpu_{utilization},\ memory_{utilization},\ bandwidth_{available},\ active_{slices}
]
$$

Typical engineered features include latency/throughput ratio, reliability-to-loss relations, and resource pressure terms.

---

## 4. Learned Function

The model approximates:

**Formal Definition**

$$
score = ML(X)
$$

where ML is a trained model (Random Forest or similar).

In implementation terms, preprocessing (scaling/normalization) and model inference are applied as a chained function over X.

---

## 5. Interpretation

Higher score -> higher risk of SLA violation

Lower score -> higher confidence that SLA can be satisfied under current conditions.

---

## 6. Relation to Multi-Domain Model

The score implicitly encodes:

**Multi-Domain Risk Aggregation**

$$
R_{total} = \alpha \cdot R_{ran} + \beta \cdot R_{transport} + \gamma \cdot R_{core}
$$

Where:

alpha, beta, gamma are learned weights (not fixed).

This interpretation is conceptual; practical models may capture nonlinear interactions and cross-domain dependencies.

---

## 7. Explainability

SHAP/LIME approximates:

**Formal Definition**

$$
score = \sum contribution(feature_i)
$$

allowing interpretation of decision factors.

Explainability outputs should be treated as local/approximate reasoning aids, not strict causal proofs.

---

## 8. Decision Threshold Mapping

Operational threshold policy:

**Decision Function**

$$
Decision =
\begin{cases}
ACCEPT & \text{if } score \leq T_{accept} \\
RENEGOTIATE & \text{if } T_{accept} < score < T_{reject} \\
REJECT & \text{if } score \geq T_{reject}
\end{cases}
$$

Typical operating values:

$$
T_{accept} = 0.4,\quad T_{reject} = 0.7
$$

This mapping aligns model output with orchestration semantics expected by Decision Engine.

---

## 9. Conclusion

The ML model provides a data-driven approximation of SLA feasibility, integrating multi-domain conditions into a single decision metric while preserving interpretability through XAI methods.
