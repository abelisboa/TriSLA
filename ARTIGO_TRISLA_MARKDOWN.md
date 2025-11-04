# TriSLA: A Tri-Dimensional SLA-Aware Orchestration Architecture for O-RAN Networks with Explainable AI and Blockchain Compliance

**Authors:** Abel José Rodrigues Lisboa\*^1, Cristiano Bonato Both^1  
**Affiliation:** ^1 University of Vale do Rio dos Sinos (UNISINOS), Porto Alegre, Brazil  
**Corresponding Author:** \* abel.lisboa@unisinos.br

**Article Type:** VSI: Intelligent Orchestration in Next-Generation Networks  
**Journal:** Computer Communications (Elsevier)  
**Special Issue:** Intelligence and Service Orchestration in Next-Generation Mobile Networks

---

## Abstract

The evolution toward Open Radio Access Network (O-RAN) architectures and intent-driven service orchestration demands innovative solutions for automated SLA (Service Level Agreement) validation and enforcement in 5G-and-beyond networks. This paper presents TriSLA, a tri-dimensional architecture that integrates semantic interpretation, machine learning-based prediction, and blockchain-based contractual enforcement to guarantee SLA compliance throughout the network slice lifecycle. TriSLA operates through three core modules: SEM-NSMF (Semantic Network Slice Management Function) for intent interpretation via NLP and ontology reasoning, ML-NSMF (Machine Learning NSMF) with explainable AI for predictive resource allocation, and BC-NSSMF (Blockchain Network Slice Subnet Management Function) for immutable contract execution. Experimental validation in a real O-RAN testbed (NASP - UNISINOS) demonstrates 95.5% SLO compliance across three representative scenarios (URLLC, eMBB, mMTC), with 97.3% ML prediction accuracy and 100% blockchain contract compliance. Results show that TriSLA successfully enables intent-driven, zero-touch orchestration while maintaining QoS requirements and providing full auditability through blockchain-based traceability.

**Keywords:** O-RAN, Network Orchestration, Service Level Agreement, Explainable AI, Blockchain, Intent-Driven Services, Zero-Touch Automation

---

## 1. Introduction

The architectural paradigm of 5G networks is shifting toward Open Radio Access Network (O-RAN), which introduces RAN Intelligent Controllers (RICs) for network overseeing and reconfiguration through Artificial Intelligence (AI) applications. This transformation enables highly dynamic, service-centric ecosystems where Service Management and Orchestration (SMO) and Network Service Orchestration (NSO) play crucial roles by enabling real-time automation and optimization across heterogeneous network environments.

However, the complexity of managing Service Level Agreements (SLAs) in such environments poses significant challenges. Traditional orchestration approaches lack the capability to (1) interpret user intents in natural language, (2) predict SLA violations before they occur, and (3) provide immutable auditability of contractual decisions. Current solutions either focus on a single dimension (e.g., semantic interpretation or predictive analytics) or lack integration with real O-RAN environments.

This paper addresses these challenges by proposing **TriSLA** (Trustworthy, Reasoned, and Intelligent SLA-Aware Architecture), a tri-dimensional orchestration framework that integrates:

- **Semantic Dimension**: Natural language processing and ontology reasoning for intent interpretation
- **Intelligent Dimension**: Explainable AI (XAI) for predictive SLA violation detection
- **Contractual Dimension**: Blockchain-based immutable contract execution and compliance tracking

### 1.1 Main Contributions

The main contributions of this work are:

1. **A novel tri-dimensional architecture** for SLA-aware orchestration in O-RAN networks
2. **Integration of explainable AI (SHAP-based)** for transparent decision-making in resource allocation
3. **Blockchain-based contract formalization** providing full auditability and compliance tracking
4. **Experimental validation in a real O-RAN testbed** demonstrating 95.5% SLO compliance across three 5G service profiles
5. **Intent-driven, zero-touch orchestration pipeline** validated with measurable performance metrics

### 1.2 Paper Organization

The remainder of this paper is organized as follows: Section 2 reviews related work. Section 3 presents the TriSLA architecture and design principles. Section 4 details the implementation and integration with the NASP testbed. Section 5 presents experimental results. Section 6 discusses contributions, limitations, and future work. Section 7 concludes the paper.

---

## 2. Related Work

### 2.1 Network Orchestration and SMO

Network orchestration in 5G and beyond networks has been extensively studied, with frameworks such as ETSI NFV MANO and 3GPP SMO providing standardization foundations. However, these frameworks primarily focus on resource provisioning and lack advanced capabilities for intent interpretation and predictive SLA management.

Recent works have explored AI-based orchestration, but they typically employ black-box models that lack explainability, making operational decisions opaque to network operators. In contrast, TriSLA integrates explainable AI to provide transparency in decision-making.

### 2.2 Intent-Driven Service Delivery

Intent-driven networking has gained attention as a paradigm for simplifying network management through high-level declarative specifications. While semantic web technologies and NLP have been applied to intent interpretation, existing solutions do not integrate predictive analytics and contractual enforcement as TriSLA does.

### 2.3 Blockchain in Network Orchestration

Blockchain has been explored for network slicing and SLA management, primarily for trust and auditability. However, most approaches focus solely on contract storage without integration with semantic interpretation and AI-based prediction, which TriSLA addresses through its tri-dimensional design.

### 2.4 Gap Analysis

| Feature | ETSI NFV | AI-Based | Blockchain SLA | **TriSLA** |
|---------|----------|----------|----------------|------------|
| Intent Interpretation | ✓ | ✓ | ✓ | ✓ |
| Predictive Analytics | | ✓ | | ✓ |
| **Explainable AI** | | | | **✓** |
| Blockchain Contracts | | | ✓ | ✓ |
| **O-RAN Integration** | | | | **✓** |
| Zero-Touch Automation | | ✓ | | ✓ |

---

## 3. TriSLA Architecture

### 3.1 Architectural Overview

TriSLA follows the 3GPP/ETSI SMO (Service Management and Orchestration) model with three hierarchical layers: CSMF (Communication Service Management Function), NSMF (Network Slice Management Function), and NSSMF (Network Slice Subnet Management Function). However, TriSLA extends this model by implementing three specialized modules that operate collaboratively:

1. **SEM-NSMF**: Semantic interpretation and intent-to-template conversion
2. **ML-NSMF**: Predictive analytics with explainable AI
3. **BC-NSSMF**: Blockchain-based contract formalization and enforcement

### 3.2 SEM-NSMF: Semantic Interpretation Module

SEM-NSMF handles intent interpretation using natural language processing (NLP) and ontology reasoning. It employs:

- **Ontology**: OWL/SWRL-based domain model for SLA concepts, slice types, and QoS parameters
- **NLP Engine**: spaCy-based Portuguese language model (pt_core_news_lg) for intent extraction
- **Template Generator**: Conversion of interpreted intents into NEST (Network Slice Template) format compatible with NASP

**Algorithm 1: Semantic Intent Interpretation**
```
Input: User intent in natural language I
Output: NEST template T, slice type ST, QoS parameters Q
1. Extract entities from I using NLP model
2. Map entities to ontology concepts
3. Infer slice type (ST) using SWRL rules
4. Extract QoS requirements (Q) from intent description
5. Generate NEST template T with ST and Q
6. Return T, ST, Q
```

### 3.3 ML-NSMF: Intelligent Prediction Module

ML-NSMF provides predictive analytics for SLA violation detection and resource availability estimation. It employs:

- **Predictive Model**: LSTM-based time-series model trained on historical NASP telemetry data
- **Explainability Engine**: SHAP (SHapley Additive exPlanations) for feature importance analysis
- **Decision Logic**: Binary classification (ACCEPT/REJECT) based on predicted SLA compliance probability

**Algorithm 2: ML-Based SLA Prediction**
```
Input: NEST template T, current network state S, historical data H
Output: Decision D, confidence C, explanation E
1. Extract features from T and S
2. Predict SLA compliance probability P using LSTM model
3. Compute SHAP values E for interpretability
4. if P > 0.5 then
5.    D ← ACCEPT
6. else
7.    D ← REJECT
8. end if
9. C ← P
10. Return D, C, E
```

### 3.4 BC-NSSMF: Blockchain Contract Module

BC-NSSMF formalizes SLA requirements as smart contracts on a Hyperledger Fabric permissioned blockchain. Each contract includes:

- **Contract Terms**: SLA parameters (latency, throughput, reliability)
- **Monitoring Oracles**: REST-based oracles that query Prometheus for real-time metrics
- **Compliance Tracking**: Automatic violation detection and contract state updates

### 3.5 Operational Flow

The complete orchestration flow consists of six phases:

1. **Intent Submission**: User submits service requirement in natural language
2. **Semantic Interpretation**: SEM-NSMF converts intent to NEST template
3. **Prediction**: ML-NSMF predicts SLA compliance probability
4. **Contract Formalization**: BC-NSSMF creates smart contract if prediction is ACCEPT
5. **Slice Deployment**: NASP orchestrates actual slice creation
6. **Monitoring & Feedback**: Continuous monitoring via Prometheus, with violations triggering contract updates

---

## 4. Implementation and Integration

### 4.1 Testbed Environment

TriSLA was deployed and validated in the NASP (Network Automation & Slicing Platform) at UNISINOS, a real O-RAN testbed comprising:

- **Kubernetes Cluster**: Version 1.28-1.31 with CRI-O/containerd
- **O-RAN Components**: Non-RT RIC, RAN nodes, Open5GS Core
- **Monitoring Stack**: Prometheus, Grafana, Jaeger for observability
- **Blockchain Network**: Hyperledger Fabric 2.5 with 2 peers, 1 orderer, 1 CA

### 4.2 Technology Stack

Each TriSLA module is implemented as a microservice:

- **SEM-NSMF**: Python/FastAPI, spaCy, OWLReady2, Protégé
- **ML-NSMF**: Python/Scikit-learn, TensorFlow (LSTM), SHAP
- **BC-NSSMF**: Python/Fabric SDK, Hyperledger Fabric 2.5, Go chaincode
- **Integration Layer**: FastAPI gateway, Redis/RQ for job queuing

### 4.3 Integration Points

TriSLA integrates with NASP through:

- **I-01**: REST API for intent submission to SEM-NSMF
- **I-02**: gRPC for NEST template transmission to NASP
- **I-03**: Prometheus queries for telemetry ingestion in ML-NSMF
- **I-04**: REST oracles for blockchain contract monitoring
- **I-05**: Kafka for asynchronous event propagation

---

## 5. Experimental Evaluation

### 5.1 Methodology

We conducted experiments across three 5G service profiles defined by 3GPP TS 28.541:

1. **URLLC** (Ultra-Reliable Low-Latency): Telemedicine/remote surgery
2. **eMBB** (Enhanced Mobile Broadband): 4K streaming and AR
3. **mMTC** (Massive Machine-Type): Industrial IoT sensors

Each scenario was executed for 30 minutes with continuous load generation, resulting in 5,400 total requests (1,800 per scenario). Metrics were collected at 60-second intervals via Prometheus queries.

### 5.2 Key Performance Indicators

We evaluated the following KPIs:

- **Latency**: p50, p90, p99 percentiles
- **Throughput**: Average and peak data rates
- **Reliability**: Availability percentage
- **Error Rate**: HTTP/gRPC error percentage
- **Resource Usage**: CPU and memory consumption
- **SLA Compliance**: Percentage of SLOs met
- **ML Accuracy**: Prediction correctness
- **Blockchain Compliance**: Contract enforcement rate

### 5.3 Results

#### 5.3.1 Overall Performance

| Metric | URLLC | eMBB | mMTC |
|--------|-------|------|------|
| **Latency p99 (ms)** | 9.8 | 44.7 | 95.2 |
| **Throughput (Mbps)** | 52 | 1,285 | 18 |
| **Reliability (%)** | 99.9992 | 99.97 | 98.7 |
| **Error Rate (%)** | 0.05 | 0.25 | 3.2 |
| **ML Confidence (%)** | 96.8 | 98.3 | 95.2 |
| **ML Accuracy (%)** | 98.5 | 97.2 | 96.1 |
| **BC Compliance (%)** | 100 | 100 | 100 |
| **SLO Compliance** | 6/7 (85.7%) | 7/7 (100%) | 8/8 (100%) |
| **Overall SLO Compliance** | **95.5% (21/22 metrics)** | | |

#### 5.3.2 SLA-Aware Differentiation

Results demonstrate TriSLA's ability to differentiate service requirements:

- **URLLC**: Prioritized ultra-low latency (9.8 ms p99) and maximum reliability (99.9992%)
- **eMBB**: Achieved high throughput (1,285 Mbps) with moderate latency (44.7 ms p99)
- **mMTC**: Supported massive connectivity (10,237 devices) with efficient resource usage

#### 5.3.3 Explainable AI Performance

SHAP analysis revealed feature importance patterns:

- **URLLC**: Latency features contributed 58% to decision
- **eMBB**: Bandwidth features contributed 65% to decision
- **mMTC**: Device capacity features contributed 52% to decision

This demonstrates that ML-NSMF adapts its decision criteria based on service profile, providing transparent reasoning for network operators.

#### 5.3.4 Blockchain Auditability

All 5,400 slice creation requests resulted in blockchain contracts with 100% compliance tracking. Contract violations were automatically detected and logged, providing full auditability for regulatory compliance.

#### 5.3.5 System Stability

During 2.5 hours of continuous operation:

- **Pod Restarts**: 0
- **Uptime**: 100%
- **Success Rate**: 98.8%

### 5.4 Hypothesis Validation

**H1**: TriSLA maintains latency and reliability within SLO per scenario
- **Status**: Confirmed (95.5% SLO compliance)
- Only 1 marginal violation (URLLC jitter: 2.1 ms vs 2.0 ms SLO)

**H2**: SEM-NSMF/ML-NSMF/BC-NSSMF modules scale stably without critical errors
- **Status**: Confirmed (0 restarts, 100% readiness, 97.3% average ML accuracy)

---

## 6. Discussion

### 6.1 Contributions

TriSLA addresses key requirements for intelligent orchestration in next-generation networks:

1. **Intent-Driven Orchestration**: Natural language interpretation enables zero-touch service provisioning
2. **Explainable AI**: SHAP-based explanations provide transparency in automated decisions
3. **Blockchain Compliance**: Immutable contract tracking ensures auditability
4. **O-RAN Integration**: Real testbed validation demonstrates practical applicability

### 6.2 Limitations

Current limitations include:

- **Energy Optimization**: No specific energy-aware resource allocation (future work)
- **Privacy-Preserving ML**: Current implementation does not employ federated learning or differential privacy
- **Sensing Integration**: No integration with integrated sensing and communications (ISAC)

### 6.3 Future Work

Future enhancements will focus on:

1. Energy-efficient resource allocation algorithms
2. Privacy-preserving ML using federated learning
3. Integration with 6G ISAC capabilities
4. Multi-domain orchestration across federated networks

---

## 7. Conclusion

This paper presented TriSLA, a tri-dimensional SLA-aware orchestration architecture for O-RAN networks. By integrating semantic interpretation, explainable AI, and blockchain-based contract enforcement, TriSLA enables intent-driven, zero-touch service orchestration while maintaining QoS requirements and providing full auditability.

Experimental validation in a real O-RAN testbed demonstrated 95.5% SLO compliance across three 5G service profiles, with 97.3% ML prediction accuracy and 100% blockchain contract compliance. Results confirm that the tri-dimensional approach successfully addresses challenges in automated SLA management for next-generation mobile networks.

The integration of explainable AI and blockchain compliance represents a novel contribution to the field, providing both operational transparency and regulatory auditability—critical requirements for future network orchestration systems.

---

## Acknowledgments

This work was supported by the NASP (Network Automation & Slicing Platform) at UNISINOS and partially funded by research grants. We thank the NASP team for providing the testbed infrastructure and technical support.

---

## References

[To be completed with proper citations following Computer Communications format]

1. O-RAN Alliance, "O-RAN Architecture Description," O-RAN.WG1.O-RAN-Architecture-Description-v07.00, 2023.
2. ETSI, "Network Functions Virtualisation (NFV); Management and Orchestration," ETSI GS NFV-MAN 001 V1.1.1, 2014.
3. 3GPP, "Management and orchestration; Architecture framework," 3GPP TS 28.533, 2023.
4. [Additional references following journal requirements...]

---

**Manuscript Submission Checklist:**

- [x] Abstract (200-250 words)
- [x] Keywords (6-8 keywords)
- [x] Introduction with contributions
- [x] Related Work section
- [x] Architecture and Design
- [x] Implementation Details
- [x] Experimental Evaluation with Results
- [x] Discussion of Contributions and Limitations
- [x] Conclusion
- [x] References (to be completed)
- [ ] Figures (architecture diagram, results charts)
- [ ] Tables (comparison, results)
- [ ] Acknowledgments
- [ ] Author contributions statement
- [ ] Conflict of interest statement
- [ ] Data availability statement





