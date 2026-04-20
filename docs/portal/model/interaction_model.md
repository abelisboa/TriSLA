# Interaction Model

## 1. Input Mapping

User input U is transformed into structured SLA request S:

**Formal Definition**

$$
SLA = f(U)
$$

---

## 2. Backend Transformation

The backend maps:

$$
SLA \rightarrow Intent \rightarrow Pipeline
$$

---

## 3. Output

**Formal Definition**

$$
O = Decision + Metrics + XAI
$$

---

## 4. Loop

$$
U \rightarrow SLA \rightarrow Decision \rightarrow O \rightarrow Visualization
$$

