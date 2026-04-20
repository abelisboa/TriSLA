# Decision Engine Mathematical Model

## 1. Problem Definition

Determine whether an SLA request should be accepted based on:

- Network state (multi-domain)
- Predicted risk
- Policy constraints

---

## 2. Variables

Let:

$$
R_{ran} = PRB_{utilization}
$$

$$
R_{transport} = latency + jitter
$$

$$
R_{core} = cpu + memory
$$

$$
score \in [0,1]
$$

---

## 3. Multi-Domain Risk Aggregation

The system implicitly evaluates:

**Multi-Domain Risk Aggregation**

$$
R_{total} = \alpha \cdot R_{ran} + \beta \cdot R_{transport} + \gamma \cdot R_{core}
$$

Where:

alpha, beta, gamma are adaptive weights (not fixed).

PRB-sensitive adjustment:

$$
R_{final} = \min \left(1,\ R_{adj} + \alpha_{prb} \cdot PRB_{norm} \right)
$$

---

## 4. Decision Function

The final decision is defined as:

**Decision Function**

$$
Decision =
\begin{cases}
ACCEPT & \text{if } score \leq T_{accept} \\
RENEGOTIATE & \text{if } T_{accept} < score < T_{reject} \\
REJECT & \text{if } score \geq T_{reject}
\end{cases}
$$

Typical thresholds:

$$
T_{accept} = 0.4,\quad T_{reject} = 0.7
$$

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

$$
Decision = f(SLA, R_{ran}, R_{transport}, R_{core}, score)
$$

enabling SLA-aware operation in multi-domain 5G networks.
