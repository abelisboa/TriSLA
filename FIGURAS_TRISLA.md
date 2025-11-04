# Figuras e Diagramas para o Artigo TriSLA

## Figura 1: Arquitetura TriSLA de Alto Nível

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE / API                              │
│                  (Intent Submission in Natural Language)                  │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────────┐
                    │   SEM-NSMF                 │
                    │  (Semantic Layer)           │
                    │  - NLP Processing          │
                    │  - Ontology Reasoning      │
                    │  - NEST Template Generation │
                    └────────────┬────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────────┐
                    │   ML-NSMF                  │
                    │  (Intelligent Layer)        │
                    │  - LSTM Prediction         │
                    │  - SHAP Explainability     │
                    │  - Resource Availability   │
                    └────────────┬────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────────┐
                    │   BC-NSSMF                 │
                    │  (Contractual Layer)        │
                    │  - Smart Contract Creation  │
                    │  - Compliance Tracking     │
                    │  - Blockchain Ledger        │
                    └────────────┬────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        NASP PLATFORM                                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│  │ Non-RT   │  │ Open5GS   │  │ RAN      │  │Transport │               │
│  │ RIC      │  │ Core      │  │ Nodes    │  │ Domain   │               │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘               │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────┐     │
│  │         Monitoring Stack (Prometheus/Grafana/Jaeger)        │     │
│  └─────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────┘
```

**Caption**: High-level architecture of TriSLA showing the three-dimensional approach: SEM-NSMF for semantic interpretation, ML-NSMF for intelligent prediction, and BC-NSSMF for contractual enforcement, integrated with the NASP O-RAN platform.

---

## Figura 2: Fluxo Operacional Detalhado (6 Fases)

```
PHASE 1: INTENT SUBMISSION
    User Input: "cirurgia remota 5G com latência ultra baixa"
                    │
                    ▼
PHASE 2: SEMANTIC INTERPRETATION (SEM-NSMF)
    ├─ NLP Processing (spaCy)
    ├─ Entity Extraction
    ├─ Ontology Mapping (OWL/SWRL)
    └─ Output: NEST Template + Slice Type (URLLC) + QoS
                    │
                    ▼
PHASE 3: ML PREDICTION (ML-NSMF)
    ├─ Feature Extraction
    ├─ LSTM Prediction (Compliance Probability)
    ├─ SHAP Explanation
    └─ Output: Decision (ACCEPT/REJECT) + Confidence + Explanation
                    │
                    ▼
PHASE 4: CONTRACT FORMALIZATION (BC-NSSMF)
    ├─ Smart Contract Creation
    ├─ Contract Terms (SLA Parameters)
    ├─ Blockchain Registration (Hyperledger Fabric)
    └─ Output: Contract ID + Contract State
                    │
                    ▼
PHASE 5: SLICE DEPLOYMENT (NASP)
    ├─ Resource Allocation
    ├─ Network Slice Creation
    ├─ Service Activation
    └─ Output: Active Slice + Monitoring Endpoints
                    │
                    ▼
PHASE 6: MONITORING & FEEDBACK
    ├─ Prometheus Metrics Collection
    ├─ SLO Compliance Check
    ├─ Violation Detection
    ├─ Contract Update (if violation)
    └─ Feedback Loop to ML-NSMF (Model Learning)
```

**Caption**: Detailed operational flow of TriSLA showing the six-phase orchestration pipeline from intent submission to continuous monitoring and feedback.

---

## Figura 3: Integração com NASP e Interfaces

```
┌─────────────────────────────────────────────────────────────────┐
│                         TRISLA ARCHITECTURE                      │
│                                                                  │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐             │
│  │ SEM-NSMF │──────│ ML-NSMF  │──────│ BC-NSSMF │              │
│  │ :8080    │ I-02 │ :7070    │ I-04 │ :8051    │              │
│  └────┬─────┘      └────┬─────┘      └────┬─────┘              │
│       │ I-01             │ I-03             │ I-05               │
└───────┼──────────────────┼──────────────────┼────────────────────┘
        │                  │                  │
        │ REST             │ Prometheus       │ Blockchain
        │                  │ Queries          │ Fabric
        ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                      NASP PLATFORM                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐   │
│  │ Non-RT RIC      │  │ Prometheus      │  │ Hyperledger   │   │
│  │ (O-RAN Control) │  │ (Metrics)       │  │ Fabric        │   │
│  └─────────────────┘  └─────────────────┘  └──────────────┘   │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐                      │
│  │ Open5GS Core    │  │ RAN Nodes       │                      │
│  │ (5G Core)       │  │ (Radio)         │                      │
│  └─────────────────┘  └─────────────────┘                      │
└─────────────────────────────────────────────────────────────────┘

I-01: REST API (Intent Submission)
I-02: gRPC (NEST Template)
I-03: Prometheus Queries (Telemetry)
I-04: REST Oracles (Contract Monitoring)
I-05: Kafka Events (Asynchronous Communication)
```

**Caption**: Integration interfaces between TriSLA modules and NASP platform components, showing communication protocols and data flows.

---

## Figura 4: Resultados Experimentais - Comparação de Cenários

### 4a. Latência p99 por Cenário

```
URLLC:  ████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  9.8 ms
eMBB:   ████████████████████████████████████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  44.7 ms
mMTC:   ████████████████████████████████████████████████████████████████████████████████████████  95.2 ms

SLO Thresholds:
URLLC: < 10 ms  ✅
eMBB:  < 50 ms  ✅
mMTC:  < 100 ms ✅
```

### 4b. Throughput por Cenário

```
URLLC:  ████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  52 Mbps
eMBB:   ████████████████████████████████████████████████████████████████████████████████████████  1285 Mbps
mMTC:   ████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  18 Mbps
```

### 4c. Confiabilidade (Reliability)

```
URLLC:  ████████████████████████████████████████████████████████████████████████████████████████  99.9992%
eMBB:   ████████████████████████████████████████████████████████████████████████████████████████  99.97%
mMTC:   ████████████████████████████████████████████████████████████████████████████████████████  98.7%

All Above SLO Threshold (> 98%)
```

**Caption**: Comparative performance metrics across three 5G service profiles demonstrating TriSLA's ability to differentiate and meet specific QoS requirements.

---

## Figura 5: Explicabilidade XAI - Feature Importance (SHAP)

```
URLLC Scenario:
Feature Importance:
  ┌─────────────────────────────────────┐
  │ Latency        ████████████████ 58% │
  │ Reliability    ████████░░░░░░░░ 32% │
  │ Jitter         ███░░░░░░░░░░░░░ 10% │
  └─────────────────────────────────────┘

eMBB Scenario:
Feature Importance:
  ┌─────────────────────────────────────┐
  │ Bandwidth      ████████████████ 65% │
  │ Throughput     ██████░░░░░░░░░░ 25% │
  │ Latency        ███░░░░░░░░░░░░░ 10% │
  └─────────────────────────────────────┘

mMTC Scenario:
Feature Importance:
  ┌─────────────────────────────────────┐
  │ Device Capacity ████████████████ 52% │
  │ Connectivity    ██████████░░░░░░ 35% │
  │ Energy          ████░░░░░░░░░░░░ 13% │
  └─────────────────────────────────────┘
```

**Caption**: SHAP-based feature importance analysis showing how ML-NSMF adapts decision criteria based on service profile, providing transparent reasoning for network operators.

---

## Figura 6: Pipeline de Decisão ML-NSMF

```
┌──────────────────────────────────────────────────────────────────┐
│                      INPUT                                        │
│  - NEST Template (from SEM-NSMF)                                │
│  - Current Network State (from Prometheus)                       │
│  - Historical Data (Training Set)                                │
└────────────────────────────────┬─────────────────────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────────┐
                    │  Feature Extraction         │
                    │  - Latency Metrics          │
                    │  - Throughput Metrics       │
                    │  - Resource Availability    │
                    └────────────┬────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────────┐
                    │  LSTM Model Prediction     │
                    │  - Time-series Analysis     │
                    │  - Compliance Probability P │
                    └────────────┬────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────────┐
                    │  SHAP Explanation          │
                    │  - Feature Importance      │
                    │  - Contribution Scores     │
                    └────────────┬────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────────┐
                    │  Decision Logic            │
                    │  if P > 0.5: ACCEPT         │
                    │  else: REJECT               │
                    └────────────┬────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────┐
│                      OUTPUT                                       │
│  - Decision (ACCEPT/REJECT)                                     │
│  - Confidence Score (0-1)                                       │
│  - SHAP Explanation (JSON)                                      │
└──────────────────────────────────────────────────────────────────┘
```

**Caption**: ML-NSMF decision pipeline showing feature extraction, LSTM-based prediction, SHAP explanation generation, and decision logic.

---

## Figura 7: Blockchain Contract Lifecycle

```
┌──────────────────────────────────────────────────────────────────┐
│                    CONTRACT CREATION                              │
│  - Contract ID Generation                                        │
│  - SLA Parameters Definition                                     │
│  - Terms Registration                                            │
└────────────────────────────────┬─────────────────────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────────┐
                    │  Smart Contract Deployment │
                    │  (Hyperledger Fabric)      │
                    │  - Chaincode Invocation    │
                    │  - Ledger Registration     │
                    └────────────┬────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────────┐
                    │  Active Contract State    │
                    │  Status: ACTIVE            │
                    │  Compliance: 100%          │
                    └────────────┬────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────────┐
                    │  Continuous Monitoring     │
                    │  (Prometheus Oracles)      │
                    │  - Metrics Collection      │
                    │  - SLO Compliance Check    │
                    └────────────┬────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
        ┌──────────────────┐      ┌──────────────────┐
        │ COMPLIANT        │      │ VIOLATION        │
        │ Status: ACTIVE    │      │ Status: VIOLATED │
        │ Update: OK        │      │ Update: Log     │
        └──────────────────┘      └──────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────────┐
                    │  Contract Termination      │
                    │  Status: TERMINATED        │
                    │  - Audit Trail            │
                    │  - Immutable Record        │
                    └────────────────────────────┘
```

**Caption**: Blockchain contract lifecycle showing creation, active monitoring, compliance tracking, and termination phases with full auditability.

---

## Figura 8: SLO Compliance Dashboard (Gráfico de Barras)

```
SLO Compliance by Scenario (%)
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│ 100% │                                                           │
│      │                           ████████████████████████       │
│  95% │                                                           │
│      │              ████████████████████████                     │
│  90% │                                                           │
│      │  ████████████████████████                                 │
│  85% │                                                           │
│      │                                                           │
│  80% └──────────────────────────────────────────────────────────│
│          URLLC (85.7%)    eMBB (100%)     mMTC (100%)          │
│                                                                  │
│  Overall: 95.5% (21/22 metrics)                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Caption**: SLO compliance percentages across three service scenarios, demonstrating overall 95.5% compliance rate.

---

## Figura 9: Comparação com Abordagens Existentes

```
┌─────────────────────────────────────────────────────────────────┐
│ Feature Comparison Matrix                                       │
│                                                                  │
│ Feature              │ ETSI NFV │ AI-Based │ BC-SLA │ TriSLA  │
│──────────────────────┼──────────┼──────────┼─────────┼─────────│
│ Intent Interpretation│     ✓    │    ✓     │    ✓    │    ✓    │
│ Predictive Analytics │          │    ✓     │         │    ✓    │
│ Explainable AI       │          │          │         │    ✓    │
│ Blockchain Contracts │          │          │    ✓    │    ✓    │
│ O-RAN Integration    │          │          │         │    ✓    │
│ Zero-Touch Automation│          │    ✓     │         │    ✓    │
│ Multi-Domain Support │    ✓     │          │         │    ✓    │
│──────────────────────┴──────────┴──────────┴─────────┴─────────│
│                                                                  │
│ TriSLA provides comprehensive coverage of all features           │
└─────────────────────────────────────────────────────────────────┘
```

**Caption**: Feature comparison matrix showing TriSLA's comprehensive coverage compared to existing orchestration approaches.

---

## Instruções para Conversão em Figuras LaTeX

### Para Diagramas (Figuras 1, 2, 3, 6, 7):
Use pacote `tikz` ou `pstricks` no LaTeX:

```latex
\usepackage{tikz}
\usetikzlibrary{shapes,arrows,positioning}
```

### Para Gráficos (Figuras 4, 5, 8):
Use pacote `pgfplots`:

```latex
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
```

### Para Tabelas (Figura 9):
Use ambiente `tabular` ou `booktabs`.

---

## Arquivos de Figuras Sugeridos

1. **`trisla_architecture.pdf`** - Figura 1 (arquitetura de alto nível)
2. **`operational_flow.pdf`** - Figura 2 (fluxo operacional)
3. **`integration_interfaces.pdf`** - Figura 3 (integração NASP)
4. **`experimental_results.pdf`** - Figura 4 (resultados comparativos)
5. **`xai_shap_importance.pdf`** - Figura 5 (explicabilidade XAI)
6. **`ml_decision_pipeline.pdf`** - Figura 6 (pipeline ML)
7. **`blockchain_lifecycle.pdf`** - Figura 7 (ciclo de vida blockchain)
8. **`slo_compliance_chart.pdf`** - Figura 8 (compliance SLO)
9. **`comparison_matrix.pdf`** - Figura 9 (comparação)





