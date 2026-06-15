# Decision Engine — Research Model

> **NOT OPERATIONAL SSOT**
>
> Operational admission logic, thresholds, env vars, and runtime behavior are defined in [`docs/modules/decision-engine.md`](../../modules/decision-engine.md) and implemented in `apps/decision-engine/src/engine.py` + `decision_thresholds.py`.
>
> This document preserves the **scientific / dissertation** formulation. It must not be used for deployment, troubleshooting, or integration.

---

## 1. Problem Definition

Determine whether an SLA request should be accepted based on:

- Network state (multi-domain)
- Predicted risk from ML-NSMF
- Policy constraints

---

## 2. Variables (research notation)

$$
R_{ran} = PRB_{utilization}, \quad
R_{transport} = latency + jitter, \quad
R_{core} = cpu + memory
$$

---

## 3. Multi-Domain Risk Aggregation (conceptual)

$$
R_{total} = \alpha \cdot R_{ran} + \beta \cdot R_{transport} + \gamma \cdot R_{core}
$$

Research weights $\alpha, \beta, \gamma$ are slice-dependent in the paper narrative.  
**Runtime fixed weights** (operational): RAN 0.70, Transport 0.20, Core 0.10 — see canonical module doc.

PRB-sensitive adjustment (research):

$$
R_{final} = \min \left(1,\ R_{adj} + \alpha_{prb} \cdot PRB_{norm} \right)
$$

---

## 4. Decision Function (research abstraction)

$$
Decision \in \{\text{ACCEPT},\ \text{RENEGOTIATE},\ \text{REJECT}\}
$$

Operational slice thresholds (URLLC / eMBB / mMTC) and hard PRB gates are **not** reproduced here — see `decision_thresholds.py` and canonical module doc.

---

## 5. Multi-Domain Influence (research narrative)

Dominance varies by slice in the dissertation:

- URLLC → transport latency sensitivity
- eMBB → RAN utilization
- mMTC → core resource availability

Runtime domain lists and scoring are implemented in `engine._apply_decision_rules`.

---

## 6. Relation to Research Question

The decision model evaluates SLA feasibility at request time by integrating current resource signals, ML-predicted risk, and service requirements — enabling real-time admission control in multi-domain 5G networks.

For evidence and frozen digest: `baseline-registry/OPERATIONAL_BASELINE_REGISTRY.json`.
