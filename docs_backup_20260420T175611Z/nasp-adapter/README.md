# NASP Adapter — Platform Integration and Metric Normalization Layer

## 1. Overview

The NASP Adapter is the integration layer responsible for connecting the TriSLA architecture with real network infrastructure.

It provides a normalized, consistent, and observable view of multi-domain network resources.

---

## 2. Role in TriSLA

The NASP Adapter operates as the boundary between:

- Logical SLA decisions
- Physical network state

---

## 3. Core Function

The module performs:

- Metric collection from real infrastructure
- Metric normalization across domains
- Execution of platform-level actions
- Exposure of a stable API

---

## 4. Domains Covered

- RAN (radio metrics)
- Transport (latency, jitter)
- Core (CPU, memory, network)

---

## 5. Research Contribution

The NASP Adapter enables:

- Real-world validation of SLA feasibility
- Continuous observability of system state
- Experimental reproducibility

---

## 6. Summary

The NASP Adapter transforms heterogeneous infrastructure metrics into a unified representation, enabling consistent SLA evaluation and system validation.
