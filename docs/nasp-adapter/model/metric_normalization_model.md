# Metric Normalization Model

## 1. Objective

Transform heterogeneous metrics from different domains into a unified normalized space.

---

## 2. Input

Let:

M_ran, M_transport, M_core

---

## 3. Normalization Function

Each metric m is transformed:

**Normalization Function**

```text
m_norm = (m - min) / (max - min)
```

---

## 4. Aggregated State

**Formal Definition**

```text
X = [
  m1_norm,
  m2_norm,
  ...,
  mn_norm
]
```

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
