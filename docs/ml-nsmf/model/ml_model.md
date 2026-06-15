# ML-NSMF — Research Model

> **NOT OPERATIONAL SSOT**
>
> Runtime inference, models, features, XAI behavior, and integrations are defined in [`docs/modules/ml-nsmf.md`](../../modules/ml-nsmf.md) and implemented in `apps/ml-nsmf/src/`.
>
> This document preserves the **scientific / dissertation** formulation. Do not use for deployment, troubleshooting, or integration.

---

## 1. Problem Definition

Given SLA requirements and network-state features, estimate feasibility / violation risk as a scalar score used downstream by the Decision Engine.

**ML-NSMF does not apply admission thresholds.** Decision mapping (ACCEPT / RENEG / REJECT) is owned by the Decision Engine.

---

## 2. Input Variables (research notation)

$$
X = f(SLA, R_{ran}, R_{transport}, R_{core})
$$

Conceptual multi-domain variables; runtime feature vector includes base SLA metrics, derived v3 scores, and slice-type encoding — see canonical module doc.

---

## 3. Learned Function (research abstraction)

$$
score = ML(X)
$$

Runtime implementation: **Random Forest Regressor** on scaled features (`viability_model.pkl` + `scaler.pkl`), plus optional slice-adjusted risk post-processing.

---

## 4. Multi-Domain Interpretation (conceptual)

$$
R_{total} = \alpha \cdot R_{ran} + \beta \cdot R_{transport} + \gamma \cdot R_{core}
$$

Research weights may vary by slice narrative. Runtime slice adjustment uses explicit URLLC/eMBB/mMTC weight tables in `slice_risk_adjustment.py`.

---

## 5. Explainability (research)

SHAP/LIME and feature attribution support interpretability claims in publication. Runtime: best-effort SHAP → LIME → metadata fallback — see canonical doc § Explainability runtime truth.

---

## 6. Scientific vs operational baselines

| Artifact | Classification |
|----------|----------------|
| BUNDLE-OP-001 (`viability_model.pkl`, `scaler.pkl`) | **ACTIVE** |
| BUNDLE-SCI-001 (`decision_classifier.pkl` v7) | **SCIENTIFIC_BASELINE** — candidate / not loaded in production per traceability matrix |

Evidence: `model-registry/traceability/MODEL_TRACEABILITY_MATRIX.json`.

---

## 7. Not in scope (research mentions without runtime)

- LSTM / GRU — **NOT IMPLEMENTED**
- XGBoost — **NOT IMPLEMENTED**
- Federated Learning — **NOT IMPLEMENTED**
