# SLA-Agent Layer — Execution and SLA Compliance Monitoring

## 1. Overview

The SLA-Agent Layer is responsible for executing and validating SLA decisions within the TriSLA architecture.

It operates as the execution and monitoring layer, ensuring that admitted SLAs are effectively deployed and continuously evaluated across multiple network domains.

---

## 2. Role in TriSLA

Pipeline:

Decision Engine → SLA-Agent → Monitoring → Events → BC-NSSMF

The SLA-Agent Layer operates after SLA admission.

---

## 3. Core Function

The module ensures:

- Execution of SLA-related actions across domains
- Continuous monitoring of Service Level Objectives (SLOs)
- Detection of SLA violations and risks
- Emission of lifecycle events

---

## 4. Multi-Domain Execution

The SLA-Agent operates across:

- RAN (radio resources)
- Transport (latency and jitter)
- Core (compute resources)

Each domain is managed by a dedicated agent.

---

## 5. Lifecycle Role

The SLA-Agent does not define lifecycle states but evaluates:

**Formal Definition**

$$
Decision \in \{OK,\ RISK,\ VIOLATED\}
$$

---

## 6. Relation to Research Problem

The SLA-Agent validates whether accepted SLAs remain feasible over time.

Thus, it provides empirical evidence supporting the decision model.

---

## 7. Summary

The SLA-Agent Layer transforms SLA decisions into observable and measurable system behavior, enabling continuous validation of SLA feasibility in multi-domain environments.
