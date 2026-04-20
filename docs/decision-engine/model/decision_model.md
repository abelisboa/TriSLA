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

score = ML-NSMF risk score in [0,1]

---

## 3. Multi-Domain Risk Aggregation

The system implicitly evaluates:

**Multi-Domain Risk Aggregation**

```text
R_total = alpha * R_ran + beta * R_transport + gamma * R_core
```

Where:

alpha, beta, gamma are adaptive weights (not fixed).

---

## 4. Decision Function

The final decision is defined as:

**Decision Function**

```text
Decision =
  ACCEPT        if score <= T_accept
  RENEGOTIATE   if T_accept < score < T_reject
  REJECT        if score >= T_reject
```

Typical thresholds:

```text
T_accept = 0.4
T_reject = 0.7
```

---

## 5. Interpretation

- Low score -> system can sustain SLA  
- High score -> high probability of SLA violation  

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

**Formal Definition**

```text
Decision = f(SLA, R_ran, R_transport, R_core, score)
```

enabling SLA-aware operation in multi-domain 5G networks.
