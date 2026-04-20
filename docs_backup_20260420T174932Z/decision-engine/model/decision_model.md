# Decision Engine Mathematical Model

## 1. Problem Definition

Determine whether an SLA request should be accepted based on:

- Network state (multi-domain)
- Predicted risk
- Policy constraints

---

## 2. Variables

Let:

R_ran = PRB utilization  
R_transport = latency + jitter  
R_core = CPU + memory  

S = ML-NSMF risk score ∈ [0,1]

---

## 3. Multi-Domain Risk Aggregation

The system implicitly evaluates:

R_total = α·R_ran + β·R_transport + γ·R_core

Where:

α, β, γ are adaptive weights (not fixed).

---

## 4. Decision Function

The final decision is defined as:

ACCEPT if S ≤ T_accept  
RENEGOTIATE if T_accept < S < T_reject  
REJECT if S ≥ T_reject  

Typical thresholds:

T_accept ≈ 0.4  
T_reject ≈ 0.7  

---

## 5. Interpretation

- Low S → system can sustain SLA  
- High S → high probability of SLA violation  

---

## 6. Multi-Domain Influence

The dominance of each domain varies by slice:

- URLLC → Transport  
- eMBB → RAN  
- mMTC → Core  

---

## 7. Relation to Research Question

The decision model evaluates SLA feasibility at request time by integrating:

- current resource availability  
- predicted risk  
- service requirements  

Thus enabling real-time admission control.

---

## 8. Conclusion

The Decision Engine provides a deterministic mapping:

(SLA requirements, network state, ML prediction) → Decision

enabling SLA-aware operation in multi-domain 5G networks.
