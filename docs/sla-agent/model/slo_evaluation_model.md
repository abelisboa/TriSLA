# SLO Evaluation Model

## 1. Objective

Evaluate whether an SLA remains compliant over time.

---

## 2. Variables

Let:

M = set of observed metrics  
SLO = set of constraints  

---

## 3. Evaluation Function

For each metric m:

**Formal Definition**

```text
compliance(m) = TRUE if m satisfies SLO threshold
```

---

## 4. Global Compliance

**Compliance Ratio**

```text
C = compliant_metrics / total_metrics
```

---

## 5. State Definition

**Decision Function**

```text
Decision =
  OK         if C = 1
  RISK       if 0.8 <= C < 1
  VIOLATED   if C < 0.8
```

---

## 6. Interpretation

- OK → SLA is stable  
- RISK → SLA degradation likely  
- VIOLATED → SLA breach  

---

## 7. Conclusion

The SLA-Agent provides runtime validation of SLA feasibility through continuous monitoring.
