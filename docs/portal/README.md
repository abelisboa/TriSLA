# TriSLA Portal — Interaction and Workload Injection Layer

Canonical module references: [`docs/modules/portal-backend.md`](../modules/portal-backend.md) and [`docs/modules/portal-frontend.md`](../modules/portal-frontend.md).
Canonical interface reference: [`docs/modules/interfaces.md`](../modules/interfaces.md).

## 1. Overview

The TriSLA Portal is the interaction layer between users and the TriSLA architecture.

It provides controlled input submission and visualization of SLA evaluation results.

---

## 2. Scientific Role

The Portal is not part of the decision logic.

Instead, it acts as:

- Input injection interface
- Controlled workload generator
- Observation interface for results

---

## 3. Components

- Portal Backend (API Gateway)
- Portal Frontend (User Interface)

---

## 4. Role in Architecture

User → Portal → TriSLA Core

---

## 5. Contribution

The Portal enables reproducible experiments by standardizing input and capturing outputs.

