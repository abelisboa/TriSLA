# Decision Engine — SLA Feasibility and Admission Control Model

## 1. Overview

The Decision Engine is the core component of the TriSLA architecture, responsible for determining whether an SLA request can be accepted based on real-time multi-domain network conditions.

It integrates semantic input, predictive intelligence, and infrastructure observability to produce deterministic SLA decisions.

---

## 2. Role in TriSLA

Pipeline:

SEM-CSMF → ML-NSMF → Decision Engine → BC-NSSMF → SLA-Agent

The Decision Engine is the final authority for SLA admission control.

---

## 3. Decision Objective

Given:

- SLA requirements (semantic + structured)
- Real-time network conditions
- ML-based risk predictions

The engine determines:

**Formal Definition**

```text
Decision in {ACCEPT, REJECT, RENEGOTIATE}
```

---

## 4. Multi-Domain Inputs

The decision is based on:

- RAN → PRB utilization
- Transport → latency, jitter
- Core → CPU, memory
- ML-NSMF → risk score in [0,1]

---

## 5. Core Principle

The decision reflects:

"Can this SLA be sustained over time given current multi-domain conditions?"

---

## 6. Delegation Boundaries

The Decision Engine:

✔ integrates inputs  
✔ applies policies  
✔ produces final decision  

It does NOT:

✘ interpret intent (SEM-CSMF)  
✘ predict risk (ML-NSMF)  
✘ enforce contracts (BC-NSSMF)  

---

## 7. Summary

The Decision Engine operationalizes SLA-aware decision-making by combining multi-domain observability and predictive intelligence into a single deterministic outcome.
