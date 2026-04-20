# Interaction Model

## 1. Input Mapping

User input U is transformed into structured SLA request S:

**Formal Definition**

```text
SLA = f(U)
```

---

## 2. Backend Transformation

The backend maps:

```text
SLA -> Intent -> Pipeline
```

---

## 3. Output

**Formal Definition**

```text
O = Decision + Metrics + XAI
```

---

## 4. Loop

```text
U -> SLA -> Decision -> O -> Visualization
```

