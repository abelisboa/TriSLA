# Metric Normalization Model

## 1. Objective

Transform heterogeneous metrics from different domains into a unified normalized space.

---

## 2. Input

Let:

$$
M = (M_{ran}, M_{transport}, M_{core})
$$

---

## 3. Normalization Function

Each metric m is transformed:

**Normalization Function**

$$
m_{norm} = \frac{m - m_{min}}{m_{max} - m_{min}}
$$

---

## 4. Aggregated State

**Formal Definition**

$$
X = [m_{1,norm},\ m_{2,norm},\ \ldots,\ m_{n,norm}]
$$

---

## 5. Output

Normalized metrics used by:

- Decision Engine
- SLA-Agent
- BC-NSSMF

---

## 6. Importance

Ensures comparability across domains.

---

## 7. Conclusion

The NASP Adapter guarantees metric consistency required for SLA-aware decisions.
