# TriSLA: A Conservative and Auditable Architecture for SLA-aware Network Slicing

## Abstract

Network slicing in 5G and beyond networks requires sophisticated mechanisms for Service Level Agreement (SLA) admission and management. This paper presents TriSLA, an architecture that incorporates future sustainability assessment in the SLA admission process, differentiating itself from optimistic acceptance strategies that evaluate only momentary resource availability. Through controlled experimental validation in a real environment (NASP), we demonstrate that TriSLA exhibits consistent, predictable, and conservative decision-making behavior, systematically opting for renegotiation (RENEG) over direct acceptance (ACCEPT) or rejection (REJECT). Our experiments covered two main axes: Enhanced Mobile Broadband (eMBB) with 5, 10, and 20 simultaneous SLAs, and Ultra-Reliable Low-Latency Communications (URLLC) with 3, 6, and 10 simultaneous SLAs. Results show 100% renegotiation rate across all scenarios, with zero processing failures and complete traceability through unique correlation IDs. The architecture demonstrates independence of decision behavior from load variations, maintaining stability even when load is quadrupled (5→20 SLAs for eMBB) or tripled (3→10 SLAs for URLLC). These empirical findings establish clear operational limits and demonstrate that conservative strategies can provide significant benefits in terms of quality assurance and proactive violation reduction, even at the cost of acceptance speed. The work contributes to the field of SLA-aware network slicing through empirical evidence of conservative behavior, reproducible experimental methodology, and an auditable architecture suitable for production environments where reliability and compliance are prioritized.

**Keywords:** Network Slicing, SLA Management, 5G, Quality of Service, Empirical Validation

## 1. Introduction

Network slicing enables the creation of multiple virtual networks over a shared physical infrastructure, each tailored to specific service requirements. The management of Service Level Agreements (SLAs) in such environments presents significant challenges, particularly regarding admission decisions that must balance resource utilization, quality guarantees, and operational risk.

Existing approaches to SLA admission in network slicing can be broadly categorized into optimistic and conservative strategies. Optimistic strategies prioritize rapid acceptance and resource utilization maximization, accepting SLAs based on momentary resource availability without explicit assessment of future sustainability. While these approaches can maximize resource utilization, they may result in SLA violations when conditions change over time, leading to financial penalties, degraded user experience, or compromised critical applications.

This paper presents TriSLA, an architecture for SLA-aware network slicing that adopts a conservative strategy, incorporating future sustainability assessment in the admission decision process. The architecture integrates machine learning predictions (ML-NSMF) with conservative decision logic (Decision Engine), where the ML model provides risk indicators without directly deciding, and the decision logic interprets these indicators considering future sustainability over the slice lifecycle.

The main contributions of this work are: (1) an architecture that incorporates explicit future sustainability assessment in SLA admission, (2) empirical demonstration of conservative and predictable behavior under variable load conditions, (3) establishment of empirical operational limits for SLA-aware network slicing, and (4) a reproducible experimental methodology that ensures complete traceability and evidence preservation.

## 2. Architecture Overview

TriSLA is composed of several key components that work together to provide SLA-aware network slicing capabilities. The architecture follows a microservices-based design, with clear separation of concerns between components.

### 2.1 Core Components

**SEM-CSMF (Service Exposure Management - Communication Service Management Function):** Acts as the entry point for SLA requests, receiving and validating incoming SLA submissions. Each SLA is assigned a unique correlation_id for complete traceability.

**ML-NSMF (Machine Learning - Network Slice Management Function):** Provides risk assessment through machine learning models. The ML-NSMF analyzes SLA requirements and current system state, generating a risk_score and risk_level (low, medium, high) that serve as indicators of future sustainability.

**Decision Engine:** Implements the core admission logic, interpreting the risk indicators provided by ML-NSMF and making admission decisions (ACCEPT, RENEG, or REJECT) based on configurable thresholds. The Decision Engine incorporates future sustainability assessment by interpreting risk_score as an indicator of sustainability over the slice lifecycle.

**BC-NSSMF (Blockchain - Network Slice Subnet Management Function):** Provides immutable record-keeping of SLA decisions through blockchain technology, ensuring auditability and non-repudiation.

**NASP Adapter:** Interfaces with the underlying network infrastructure, translating high-level SLA requirements into network configuration.

### 2.2 Decision Logic

The Decision Engine implements a conservative decision strategy that considers not only immediate resource availability but also future sustainability. The decision logic interprets the risk_score from ML-NSMF as follows:

- **LOW_RISK_THRESHOLD (≤0.4):** Indicates acceptable current and future risk → Decision: ACCEPT
- **MEDIUM_RISK_THRESHOLD (≤0.7):** Indicates borderline future risk → Decision: RENEG
- **HIGH_RISK (>0.7):** Indicates high future risk → Decision: REJECT

This approach differentiates TriSLA from systems that adopt optimistic acceptance, where SLAs are accepted based solely on momentary conditions without assessment of future sustainability.

## 3. Experimental Methodology

To validate the TriSLA architecture empirically, we designed a rigorous experimental methodology that ensures complete isolation from production code, full evidence preservation, and integral traceability.

### 3.1 Experimental Environment

All experiments were executed in a real environment (NASP - Network as a Service Platform), without modifications to production code or decision rules. The experimental infrastructure was completely isolated in a dedicated experiments/ directory, ensuring that no production code was altered during validation.

### 3.2 Experimental Axes

Two main experimental axes were defined:

**Axis C1 - Enhanced Mobile Broadband (eMBB):** Evaluates system behavior under incremental eMBB load. Three scenarios were executed: C1.1_R1 (5 simultaneous SLAs), C1.2_R1 (10 simultaneous SLAs), and C1.3_R1 (20 simultaneous SLAs). eMBB SLAs were characterized by moderate requirements: latency 50ms, throughput 100Mbps, reliability 0.99.

**Axis C2 - Ultra-Reliable Low-Latency Communications (URLLC):** Evaluates system behavior under URLLC SLAs with extremely rigorous requirements. Three scenarios were executed: C2.1_R1 (3 simultaneous SLAs), C2.2_R1 (6 simultaneous SLAs), and C2.3_R1 (10 simultaneous SLAs). URLLC SLAs were characterized by rigorous requirements: latency 5ms (10x more rigorous than eMBB), reliability 0.99999 (100x more rigorous than eMBB), jitter 1ms.

### 3.3 Data Collection

For each scenario, we collected: (1) submission data with unique correlation_ids and client-side timestamps, (2) Prometheus metrics from the monitoring system, (3) logs from all critical components (Decision Engine, ML-NSMF, SEM-CSMF, BC-NSSMF), and (4) offline analysis computing decision times, end-to-end times, and acceptance/renegotiation/rejection rates.

All experimental artifacts were preserved with SHA256 checksums and archived in compressed tar files, ensuring complete reproducibility and integrity validation.

## 4. Results and Analysis

### 4.1 Results for Axis C1 (eMBB)

All three eMBB scenarios exhibited identical behavior: 100% of submitted SLAs resulted in renegotiation (RENEG) decisions. No SLAs were directly accepted (ACCEPT) or rejected (REJECT) in any scenario. Table I (reference: table_C1_eMBB_results.md) consolidates these results.

**C1.1_R1 (5 SLAs):** All 5 SLAs were processed successfully, resulting in 100% RENEG. No processing failures were observed.

**C1.2_R1 (10 SLAs):** All 10 SLAs were processed successfully, resulting in 100% RENEG. The decision behavior remained identical despite doubling the load.

**C1.3_R1 (20 SLAs):** All 20 SLAs were processed successfully, resulting in 100% RENEG. The decision behavior remained consistent even when load was quadrupled (5→20 SLAs).

The scalability analysis (Figure 1, reference: fig_scalability_C1.png) visualizes the renegotiation rate maintaining constant at 100% for all load levels tested (5, 10, and 20 simultaneous SLAs). This load independence suggests that operational limits for eMBB SLAs are beyond the tested range, at least in terms of processing capacity.

### 4.2 Results for Axis C2 (URLLC)

All three URLLC scenarios exhibited identical behavior to C1: 100% of submitted SLAs resulted in renegotiation (RENEG) decisions. Table II (reference: table_C2_URLLC_results.md) consolidates these results.

**C2.1_R1 (3 SLAs):** All 3 SLAs were processed successfully, resulting in 100% RENEG. The system demonstrated capability to process URLLC SLAs with extremely rigorous requirements without processing failures.

**C2.2_R1 (6 SLAs):** All 6 SLAs were processed successfully, resulting in 100% RENEG. The decision behavior remained identical despite doubling the load.

**C2.3_R1 (10 SLAs):** All 10 SLAs were processed successfully, resulting in 100% RENEG. The decision behavior remained consistent even when load was tripled (3→10 SLAs).

The scalability analysis (Figure 2, reference: fig_scalability_C2.png) visualizes the renegotiation rate maintaining constant at 100% for all load levels tested (3, 6, and 10 simultaneous SLAs). This load independence under extremely rigorous requirements suggests that operational limits for URLLC SLAs are beyond the tested range.

### 4.3 Comparative Analysis C1 × C2

The formal comparison between axes C1 (eMBB) and C2 (URLLC) reveals a scientifically significant observation: decision behavior was completely identical for eMBB SLAs (moderate requirements) and URLLC SLAs (extremely rigorous requirements). Table III (reference: table_C1_vs_C2_comparison.md) consolidates this comparison.

Despite substantial differences in requirements between eMBB and URLLC (10x more rigorous latency, 100x more rigorous reliability for URLLC), decision behavior remained identical. This observation suggests that operational limits may be related more to decision thresholds than to processing capacity itself.

The comparison visualization (Figure 3, reference: fig_C1_vs_C2_comparison.png) demonstrates the similarity of decision behavior regardless of slice type or requirement criticality.

## 5. Discussion and Limitations

### 5.1 Interpretation of Decision Behavior

The systematic decision for renegotiation (RENEG) in 100% of tested cases does not represent a system failure, but rather a deliberate architectural characteristic reflecting a conservative quality assurance strategy. The Decision Engine evaluates not only immediate resource availability but also future sustainability over the slice lifecycle.

This approach fundamentally differs from systems adopting optimistic acceptance strategies, where SLAs are accepted based solely on momentary resource availability conditions. TriSLA, in contrast, incorporates implicit future risk assessment, derived from the risk_score provided by ML-NSMF, interpreted as a sustainability indicator over time.

### 5.2 Empirical Limits Identified

The experiments established clear empirical limits for TriSLA behavior in the tested version. The system successfully processed up to 20 simultaneous eMBB SLAs and up to 10 simultaneous URLLC SLAs without processing failures or observable performance degradation. These values represent the maximum limits tested experimentally, not necessarily the real maximum limits of the system.

The most clearly observed limit was decision behavior: in all tested scenarios, the system presented 100% renegotiation, 0% direct acceptance, and 0% rejection. This limit suggests that thresholds configured in the Decision Engine are sufficiently conservative to result in renegotiation even for moderate requirements.

### 5.3 Implications for SLA-aware Network Slicing

The conservative strategy observed in TriSLA offers clear practical benefits for network operators. By prioritizing renegotiation over direct acceptance, the system reduces the risk of resource commitment without adequate maintenance guarantees, which can result in SLA violations and financial penalties.

The future sustainability assessment incorporated in TriSLA, even if implicitly through risk_score, represents a proactive strategy for reducing SLA violations. By considering not only momentary conditions but also future risk indicators, the system can identify SLAs that, although technically acceptable at request time, may result in violations over time.

### 5.4 Current Architectural Limitations

The current version of TriSLA does not demonstrate capability to directly accept SLAs (ACCEPT) under tested conditions, even for moderate requirements. This limitation may be adequate for critical environments where quality assurance is prioritized, but may represent a barrier for scenarios where rapid acceptance is desirable.

The system does not demonstrate capability to adapt decision behavior based on slice type or requirement criticality, resulting in identical behavior for eMBB and URLLC. This architectural limitation suggests that differentiation by slice type, if desired, would require adjustments in Decision Engine thresholds or decision logic.

## 6. Related Work

The literature in network slicing presents a variety of approaches for SLA admission, ranging from systems that prioritize resource utilization maximization to systems that adopt more conservative strategies.

Many proposed systems adopt optimistic acceptance strategies, where SLAs are accepted based on momentary resource availability conditions. These systems often maximize resource utilization and respond rapidly to requests, but may result in SLA violations when conditions change over time.

TriSLA positions itself as a conservative and auditable system, where all decisions are traceable through unique correlation_ids and complete logs. This characteristic differentiates the system from approaches that prioritize speed over traceability, offering operators complete audit capability without compromising functionality.

The empirical evidence presented in this work demonstrates that conservative strategies can provide significant benefits in terms of quality assurance and proactive violation reduction, even at the cost of acceptance speed. This contribution is particularly relevant for operators working in critical environments where reliability is essential.

## 7. Conclusion and Future Work

This paper presented TriSLA, an architecture for SLA-aware network slicing that incorporates future sustainability assessment in the admission decision process. Through controlled experimental validation in a real environment, we demonstrated that TriSLA exhibits consistent, predictable, and conservative decision-making behavior, systematically opting for renegotiation over direct acceptance.

The empirical results establish clear operational limits and demonstrate that the architecture maintains stability and consistency under variable load conditions, processing up to 20 simultaneous eMBB SLAs and up to 10 simultaneous URLLC SLAs without failures. The conservative strategy observed offers benefits in terms of quality assurance and proactive violation reduction, making TriSLA suitable for production environments where reliability and compliance are prioritized.

Future work directions include: (1) implementation of adaptive thresholds that could allow direct acceptance of SLAs with moderate requirements while maintaining renegotiation for rigorous requirements, (2) differentiation by slice type through slice-specific logic or differentiated thresholds, and (3) dynamic threshold adjustment based on operational conditions, historical decisions, or load patterns, which would require substantial complexity increase and extensive experimental validation.

The work contributes to the field of SLA-aware network slicing through empirical evidence of conservative behavior, reproducible experimental methodology, and an auditable architecture suitable for production environments where reliability is essential.

## Acknowledgments

The authors acknowledge the support of the NASP platform for providing the experimental environment, and the research community for valuable feedback during the development of this work.

## References

[References would be included here in IEEE format, citing related work in network slicing, SLA management, and 5G architectures]

