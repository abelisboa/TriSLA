# ML-NSMF Module Complete Guide

**Version:** 3.5.0  
**Date:** 2025-01-27  
**Module:** Machine Learning Network Slice Management Function

---

## 📋 Table of Contents

1. [Overview](#overview)  
2. [Module Architecture](#module-architecture)  
3. [Module Operation](#module-operation)  
4. [Model Training](#model-training)  
5. [Prediction and XAI](#prediction-and-xai)  
6. [Integration with Other Modules](#integration-with-other-modules)  
7. [Interface I-03 (Kafka)](#interface-i-03-kafka)  
8. [Observability](#observability)  
9. [Usage Examples](#usage-examples)  
10. [Troubleshooting](#troubleshooting)  

---

## 🎯 Overview

The **ML-NSMF (Machine Learning Network Slice Management Function)** is responsible for predicting the feasibility of SLA acceptance based on historical metrics, NEST characteristics, and the current state of infrastructure resources.

### Objectives

1. **Feasibility Prediction:** Predict whether an SLA can be satisfied (score 0–1)  
2. **Explainability (XAI):** Provide explanations for predictions using SHAP and LIME  
3. **Recommendations:** Suggest requirement adjustments when necessary  
4. **Integration:** Communicate with the Decision Engine via Interface I-03 (Kafka)  

### Key Features

- **ML Model:** Random Forest (current) or LSTM/GRU (future)  
- **XAI:** SHAP and LIME for explainability  
- **Response Time:** < 500 ms  
- **Accuracy:** > 85% (trained model)  

---

## 🏗️ Module Architecture

### Directory Structure

# ML-NSMF Module Complete Guide

**Version:** 3.5.0  
**Date:** 2025-01-27  
**Module:** Machine Learning Network Slice Management Function

---

## 📋 Table of Contents

1. [Overview](#overview)  
2. [Module Architecture](#module-architecture)  
3. [Module Operation](#module-operation)  
4. [Model Training](#model-training)  
5. [Prediction and XAI](#prediction-and-xai)  
6. [Integration with Other Modules](#integration-with-other-modules)  
7. [Interface I-03 (Kafka)](#interface-i-03-kafka)  
8. [Observability](#observability)  
9. [Usage Examples](#usage-examples)  
10. [Troubleshooting](#troubleshooting)  

---

## 🎯 Overview

The **ML-NSMF (Machine Learning Network Slice Management Function)** is responsible for predicting the feasibility of SLA acceptance based on historical metrics, NEST characteristics, and the current state of infrastructure resources.

### Objectives

1. **Feasibility Prediction:** Predict whether an SLA can be satisfied (score 0–1)  
2. **Explainability (XAI):** Provide explanations for predictions using SHAP and LIME  
3. **Recommendations:** Suggest requirement adjustments when necessary  
4. **Integration:** Communicate with the Decision Engine via Interface I-03 (Kafka)  

### Key Features

- **ML Model:** Random Forest (current) or LSTM/GRU (future)  
- **XAI:** SHAP and LIME for explainability  
- **Response Time:** < 500 ms  
- **Accuracy:** > 85% (trained model)  

---

## 🏗️ Module Architecture

### Directory Structure

apps/ml-nsmf/
├── src/
│ ├── main.py # FastAPI application
│ ├── predictor.py # RiskPredictor class (prediction)
│ ├── kafka_consumer.py # Kafka consumer (receives NESTs)
│ ├── kafka_producer.py # Kafka producer (sends predictions)
│ └── init.py
├── models/
│ ├── viability_model.pkl # Trained model (Random Forest)
│ ├── scaler.pkl # Normalization scaler
│ └── model_metadata.json # Model metadata
├── data/
│ ├── datasets/
│ │ └── trisla_ml_dataset.csv # Training dataset
│ └── training/ # Training scripts
├── tests/
│ └── unit/ # Unit tests
├── Dockerfile
├── requirements.txt
└── README.md

### Main Components

1. **RiskPredictor** — Core prediction class  
2. **MetricsConsumer** — Consumes NASP metrics via Kafka  
3. **PredictionProducer** — Sends predictions to the Decision Engine via Kafka  
4. **ML Model** — Trained model (Random Forest or LSTM/GRU)  
5. **XAI Explainer** — Explanation engine using SHAP/LIME  

---

## ⚙️ Module Operation

### Processing Pipeline

Receive NEST (Kafka I-02 from SEM-CSMF)
│
▼
Collect Current Metrics (NASP Adapter)
│
▼
Feature Extraction (NEST + metrics)
│
▼
Normalization (trained scaler)
│
▼
ML Prediction (trained model)
│
▼
XAI Explanation (SHAP/LIME)
│
▼
Send to Decision Engine (Kafka I-03)


### Detailed Flow

1. **NEST Reception**
   - Kafka consumer receives NEST from SEM-CSMF  
   - Topic: `sem-csmf-nests`

2. **Metrics Collection**
   - Queries NASP Adapter for current metrics  
   - Domains: RAN, Transport, Core  

3. **Feature Extraction**
   - From NEST: `sliceType`, `latency_requirement`, `throughput_requirement`, `reliability_requirement`  
   - From metrics: `cpu_utilization`, `memory_utilization`, `network_bandwidth_available`, `active_slices_count`  
   - Feature engineering: `latency_throughput_ratio`, `reliability_packet_loss_ratio`, etc.  

4. **Normalization**
   - Uses trained `scaler.pkl`  
   - StandardScaler or MinMaxScaler  

5. **Prediction**
   - ML model outputs feasibility score (0–1)  
   - Configurable threshold (e.g., 0.7)  

6. **Explanation (XAI)**
   - SHAP or LIME generates explanations  
   - Feature importance ranking  
   - Textual reasoning  

7. **Delivery to Decision Engine**
   - Kafka producer sends prediction  
   - Topic: `ml-nsmf-predictions`  

---

## 🎓 Model Training

### 1. Data Preparation

#### Training Dataset

**File:** `apps/ml-nsmf/data/datasets/trisla_ml_dataset.csv`

**Dataset Structure:**

| Column | Type | Description |
|------|------|-------------|
| `latency` | float | Required latency (ms) |
| `throughput` | float | Required throughput (Mbps) |
| `reliability` | float | Required reliability (0–1) |
| `jitter` | float | Required jitter (ms) |
| `packet_loss` | float | Packet loss (0–1) |
| `cpu_utilization` | float | CPU utilization (0–1) |
| `memory_utilization` | float | Memory utilization (0–1) |
| `network_bandwidth_available` | float | Available bandwidth (Mbps) |
| `active_slices_count` | int | Number of active slices |
| `slice_type_encoded` | int | Encoded slice type (1=eMBB, 2=URLLC, 3=mMTC) |
| `viability_score` | float | Feasibility score (0–1) — **TARGET** |

### Feature Engineering

```python
features['latency_throughput_ratio'] = features['latency'] / features['throughput']
features['reliability_packet_loss_ratio'] = features['reliability'] / (features['packet_loss'] + 0.001)
features['jitter_latency_ratio'] = features['jitter'] / (features['latency'] + 0.001)
features['resource_ratio'] = features['required_cpu'] / features['available_cpu']

🔮 Prediction and XAI
Feasibility Interpretation

0.0 – 0.4: Low risk (ACCEPT)

0.4 – 0.7: Medium risk (CONDITIONAL_ACCEPT)

0.7 – 1.0: High risk (REJECT)

XAI Methods

SHAP: Primary explanation method

LIME: Fallback when SHAP is unavailable

Fallback: Static feature importance when neither is available

📊 Observability
Prometheus Metrics
Metric	Type	Description
ml_nsmf_predictions_total	Counter	Total predictions
ml_nsmf_prediction_duration_seconds	Histogram	Prediction latency
ml_nsmf_model_accuracy	Gauge	Model accuracy
ml_nsmf_viability_scores	Histogram	Score distribution
ml_nsmf_training_duration_seconds	Histogram	Training duration
OpenTelemetry Traces

predict_risk

normalize_metrics

explain_prediction

send_prediction

🎯 Conclusion

The ML-NSMF provides intelligent SLA feasibility prediction with explainable AI. The module:

✅ Predicts SLA feasibility using real metrics

✅ Explains predictions with SHAP/LIME

✅ Integrates with SEM-CSMF and Decision Engine

✅ Is observable via Prometheus and OpenTelemetry

✅ Can be retrained with new data

For further details, see:

apps/ml-nsmf/src/predictor.py

apps/ml-nsmf/models/model_metadata.json

apps/ml-nsmf/README.md

End of Guide
