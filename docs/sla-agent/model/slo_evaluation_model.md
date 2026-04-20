# SLO Evaluation Model

## 1. Objective

Evaluate whether an SLA remains compliant over time.

---

## 2. Variables

Let:

$$
M = \{observed\ metrics\}
$$

$$
SLO = \{constraints\}
$$

---

## 3. Evaluation Function

For each metric m:

**Formal Definition**

$$
compliance(m) = TRUE \text{ if } m \text{ satisfies SLO threshold}
$$

---

## 4. Global Compliance

**Compliance Ratio**

$$
C = \frac{compliant\ metrics}{total\ metrics}
$$

---

## 5. State Definition

**Decision Function**

$$
Decision =
\begin{cases}
OK & \text{if } C = 1 \\
RISK & \text{if } 0.8 \leq C < 1 \\
VIOLATED & \text{if } C < 0.8
\end{cases}
$$

---

## 6. Interpretation

- OK → SLA is stable  
- RISK → SLA degradation likely  
- VIOLATED → SLA breach  

---

## 7. Conclusion

The SLA-Agent provides runtime validation of SLA feasibility through continuous monitoring.
