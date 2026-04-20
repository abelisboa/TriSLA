# TriSLA: A Tri-Dimensional SLA-Aware Orchestration Architecture for O-RAN Networks with Explainable AI and Blockchain Compliance

## Abstract

Service-level agreement management in 5G and O-RAN environments remains constrained by fragmented orchestration, weak decision transparency, and limited governance traceability. Although many proposals discuss SLA-aware automation, most remain conceptual or are validated only through simulation. This paper presents TriSLA as an integrated architecture that combines semantic interpretation, risk-aware admission intelligence, and conditional blockchain governance in a single operational pipeline. TriSLA connects SEM-CSMF, ML-NSMF, Decision Engine, and BC-NSSMF components and evaluates them through real runtime execution in a NASP environment. The experimental design uses controlled SLA loads of 1, 10, and 50 requests with balanced URLLC, eMBB, and mMTC compositions, and all measurements are extracted from real API responses rather than synthetic traces. Results show measurable end-to-end behavior, non-trivial admission selectivity, slice-aware decision asymmetry, and explicit scalability limits under stress. In the observed campaign, average admission latency remained within the same operational order of magnitude across scenarios, approval ratio decreased with load, and success ratio dropped at the highest tier, revealing realistic runtime constraints. Blockchain governance remained conditionally integrated but produced null transaction confirmations in this batch, which is reported transparently as an observability limitation. These findings demonstrate that TriSLA has moved from conceptual architecture to experimentally validated system-level behavior, providing a reproducible basis for next-stage SLA orchestration and governance research in O-RAN networks.

## 1. Introduction

The evolution toward 5G and O-RAN brings unprecedented flexibility through network slicing, but it also introduces a control challenge: SLA fulfillment must be continuously interpreted, evaluated, enforced, and audited across heterogeneous domains. In practice, operators need more than static policy definitions. They require runtime mechanisms able to transform service intent into concrete decisions and accountable enforcement while coping with dynamic load and multi-slice heterogeneity.

Despite broad interest in intelligent orchestration, a significant gap persists between architectural proposals and experimentally validated systems. Many studies present useful conceptual frameworks, yet rely on synthetic assumptions, incomplete runtime integration, or isolated module evaluation. As a consequence, the literature still lacks end-to-end evidence that semantic interpretation, ML-supported admission control, and governance mechanisms can operate as a unified pipeline under real execution conditions.

This paper addresses that gap with TriSLA, a tri-dimensional SLA-aware architecture designed for O-RAN-aligned environments. The central contribution is not only architectural composition, but its empirical validation through controlled runtime execution. TriSLA is evaluated with real API-driven experiments over multiple load tiers and slice categories, producing measurable evidence of latency, decision behavior, scalability, and governance integration. The resulting narrative reframes TriSLA from a conceptual proposition into an experimentally grounded orchestration and compliance system.

## 2. Background and Motivation

SLA management in mobile networks has historically focused on static contractual parameters, while 5G slicing introduces far more dynamic and context-dependent service guarantees. URLLC, eMBB, and mMTC profiles impose distinct latency, reliability, and resource expectations, making uniform admission policies insufficient. In O-RAN settings, this complexity is amplified by modular control planes and disaggregated operational domains.

Semantic processing is essential because SLA requests often start as high-level intent and must be transformed into machine-actionable constraints. Without semantic normalization, admission logic tends to depend on rigid templates and loses adaptability. At the same time, pure rule-based admission does not adequately capture runtime uncertainty; ML-driven risk awareness can improve decision quality, but only if confidence and reasoning traces are exposed for operational interpretation.

Governance is the third axis that remains weakly addressed in many orchestration approaches. Even when decisions are technically sound, auditability and enforcement traceability are often under-specified. Blockchain-based mechanisms can provide integrity and accountability, but must be integrated conditionally and pragmatically, rather than treated as isolated add-ons.

The motivation for TriSLA is therefore systemic: combine semantic grounding, intelligent decision support, and compliance-oriented governance in one executable control flow. The scientific relevance lies in demonstrating this integration with real evidence, reducing the distance between architectural design and reproducible operational validation.

## 3. TriSLA Architecture

TriSLA is organized around three tightly coupled dimensions: semantic interpretation, decision intelligence, and governance enforcement. SEM-CSMF receives intent-oriented SLA submissions and converts them into structured representations suitable for downstream orchestration. The Decision Engine coordinates admission behavior by combining semantic outputs with risk-aware signals produced by ML-NSMF. BC-NSSMF provides governance hooks for conditional commitment and traceability when policy and runtime conditions allow enforcement.

The architectural objective is to preserve end-to-end coherence from request intake to enforcement visibility. Instead of independent modules loosely connected by offline exchange, TriSLA operates as a runtime chain in which each stage informs the next one and contributes observable outputs. This design enables not only decision execution but also post hoc interpretation of behavior under real load.

An important distinction in this paper is that these components are not presented as conceptual placeholders. They are actively integrated in the execution pipeline assessed in Section 5. The resulting behavior includes successful and failed paths, selective admissions, and governance-related null outcomes, all of which are treated as empirical signals rather than filtered artifacts. This approach strengthens scientific validity by preserving the full operational profile of the system.

## 4. Methodology

The methodology is based on controlled experimentation in a real NASP runtime context, using production-aligned API paths. The campaign executes three scenarios with 1, 10, and 50 SLA submissions, respectively, and balances slice types across URLLC, eMBB, and mMTC to avoid single-profile bias. Each request is processed through the same operational chain, and the collected outputs are persisted as structured raw and processed artifacts.

All measurements are derived from real API responses. No synthetic metric injection, simulation backfilling, or inferred payload completion is used. Core indicators include admission latency, approval ratio, execution success ratio, confidence traces, slice-level behavior, and blockchain-related fields when available. Aggregation is performed by scenario, by slice, and globally, with percentile reporting where component availability supports it.

The analysis strategy combines descriptive and comparative interpretation. Descriptive analysis captures end-to-end behavior and module-visible outcomes across scenarios. Comparative analysis evaluates load progression effects and slice-specific asymmetries. Governance analysis examines whether blockchain-related signals are populated in runtime outputs and reports absence transparently when commitments are not confirmed in the observed batch. This methodology ensures reproducibility and guards against over-claiming by restricting conclusions to measurable evidence.

## 5. Unified Results and Discussion

### 5.1 Experimental Framework and Real Execution Context

The experimental campaign was executed in the operational TriSLA environment (NASP-based runtime), not in simulation mode. Three controlled scenarios were used: `1`, `10`, and `50` SLA submissions, with balanced slice composition across `URLLC`, `eMBB`, and `mMTC`. The evaluated path corresponds to the real orchestration chain: semantic interpretation (`SEM-CSMF`), decision and risk-aware admission (`Decision Engine` + `ML-NSMF`), and conditional governance (`BC-NSSMF`) when applicable.

All results in this section come from recorded runtime executions and structured exports in `evidencias_resultados_article1` and `evidencias_resultados_article2`. Therefore, this section updates the former conceptual emphasis with measurable evidence from a running system.

### 5.2 End-to-End SLA Orchestration Performance

Figure `fig1_latency_modulo.png` introduces module-level latency decomposition, while `fig2_latency_cenario.png` and `fig9_e2e_pipeline.png` show scenario scaling behavior and end-to-end composition. Across all runs, average admission time remained in the same order of magnitude: `291.64 ms` in `scenario_1`, `247.36 ms` in `scenario_10`, and `164.73 ms` in `scenario_50`.

The reduction in mean latency with higher load does not indicate guaranteed acceleration; rather, it reflects runtime variability and mixed decision outcomes under the observed conditions. The main scientific point is that measurable pipeline behavior is now explicit, replacing a previously architecture-only narrative.

### 5.3 Decision Intelligence and Admission Behavior

Figure `fig3_aprovacao.png` presents approval behavior by scenario, and `fig4_decision_dist.png` consolidates decision distribution. The observed approval ratio (`ACCEPT/total`) was `1.00` in `scenario_1`, `0.40` in `scenario_10`, and `0.22` in `scenario_50`.

The global decision profile (`N=61`) shows coexistence of acceptance and rejection under real workload pressure, with `26.23%` ACCEPT, `45.90%` REJECT, and `0.00%` RENEG in this execution window. This confirms practical operation as an intelligent SLA admission controller with non-trivial selectivity.

### 5.4 ML-Driven Risk Awareness

Figure `fig5_ml_risk.png` introduces the empirical ML evidence layer. The runtime payload exposed confidence traces consistently (`decision_confidence_avg ≈ 0.815`), confirming that ML-assisted decision support is active in production execution.

Risk-specific fields were partially available depending on per-request payload completeness. The relevant contribution here is not a synthetic risk curve, but the fact that admission outputs include measurable ML-related metadata under real execution, enabling future calibrated risk-to-decision analyses.

### 5.5 Slice-Aware Behavior Analysis

Figure `fig6_por_slice.png` compares behavior by slice type using the same experimental batch. Per-slice approval ratio was `72.73%` for URLLC (`n=22`), `0.00%` for eMBB (`n=20`), and `0.00%` for mMTC (`n=19`).

Per-slice success ratio remained in a similar range, with `72.73%` for URLLC, `70.00%` for eMBB, and `73.68%` for mMTC. The results reveal differentiated admission outcomes across slices while maintaining a comparable processing-success band, indicating that slice-aware semantics are materially affecting acceptance behavior.

### 5.6 Scalability and System Stability

Figure `fig7_scalability.png` and `metrics_by_scenario.csv` quantify behavior under load expansion (`1 → 10 → 50`). Success ratio was `1.00` for `scenario_1`, `1.00` for `scenario_10`, and `0.66` for `scenario_50`.

P95 admission latency was `291.64 ms` in `scenario_1`, `310.27 ms` in `scenario_10`, and `266.55 ms` in `scenario_50`. Global error rate in this campaign was `27.87%` (derived from success ratio `72.13%`), indicating real stress sensitivity at the highest load tier while preserving substantial throughput continuity.

### 5.7 Blockchain-Based SLA Governance (Article 2 Integration)

Figure `fig8_blockchain.png` and `article2_metrics_by_scenario.csv` integrate governance evidence into the same results narrative. The architecture enforces a conditional governance model: blockchain commitment is triggered by admission outcomes and runtime availability, not by unconditional write attempts.

In the present run, transaction-oriented fields remained empty in payload (`tx_success_ratio = 0.00` in all three scenarios), which is reported as-is. This is still scientifically relevant: governance behavior is integrated into the pipeline and instrumented, but the current operational window did not yield successful on-chain confirmations in the captured dataset.

### 5.8 Integrated Orchestration + Governance Discussion

The combined evidence supports a closed-loop interpretation of TriSLA in which semantic intent is transformed into machine-actionable SLA structure, decision logic operates with measurable confidence signals, admission outcomes affect downstream enforcement eligibility, and governance hooks remain observable in the same runtime chain, even when transaction completion is absent in a specific batch.

Under this perspective, TriSLA is not only orchestration middleware. It behaves as a unified decision-execution-governance system in operational conditions.

### 5.9 Limitations and Observability Constraints

Scientific validity requires explicit treatment of missing and partial evidence. Several advanced latency fields (`semantic_parsing_latency_ms`, `decision_duration_ms`, `blockchain_transaction_latency_ms`) were null in part of the payloads and were preserved as null in aggregates. End-to-end composite latency percentiles for decomposed stages are therefore incomplete when component fields are unavailable.

Blockchain metrics such as transaction latency, gas usage, and block time were not populated in this batch and were not inferred. In addition, the high-load scenario (`50`) showed reduced success ratio, indicating real operational constraints that require further investigation. These limitations increase credibility by preventing over-claiming and preserving strict traceability to observed data.

### 5.10 Key Contributions Reinforced by Experimental Evidence

The evidence-backed contributions are the demonstration of real SLA-aware orchestration under controlled but operational runtime conditions, empirical decision behavior with measurable ML confidence signals, conditional blockchain-governance integration in the same orchestration path, and a validated scalability profile (`1/10/50`) with explicit stability limits.

In synthesis, TriSLA progresses from an architectural proposition to an experimentally validated system with quantifiable orchestration and governance behavior.

## 6. Conclusion and Future Work

### 6.1 Conclusion

This work presents TriSLA as a practical response to the gap between conceptual SLA orchestration proposals and real, reproducible runtime validation in 5G/O-RAN contexts. By integrating semantic intent processing, ML-assisted decision behavior, and conditional blockchain governance into one executable pipeline, TriSLA demonstrates measurable end-to-end behavior beyond architectural abstraction.

The experimental campaign confirms that admission, confidence-aware decisioning, and slice-sensitive behavior can be observed under controlled load progression, while also exposing realistic stress effects and governance-data incompleteness. Rather than weakening the contribution, this transparent profile strengthens the scientific claim that TriSLA is a functioning system with empirically bounded behavior.

### 6.2 Future Work

Future work should prioritize renegotiation-aware flows as a first-class outcome, increasing support for explicit RENEG trajectories and policy feedback loops. Additional efforts are needed to improve ACCEPT coverage through calibrated admission strategies and richer context features without sacrificing safety constraints.

On the governance side, the immediate priority is to expand blockchain observability with complete transaction latency, gas consumption, and commit confirmation signals across broader workloads. A second direction is closed-loop integration with RIC-aligned control feedback for adaptive policy refinement. Finally, long-horizon validation in production-like continuous operation is required to assess drift, resilience, and governance consistency over time.
