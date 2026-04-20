# ML-NSMF Architecture

## 1. Position in TriSLA

ML-NSMF is the predictive analysis layer between semantic intent formalization and final policy decision.

Flow position:

SEM-CSMF (semantic output) -> ML-NSMF (feasibility prediction) -> Decision Engine (final decision)

## 2. Main Components

- `RiskPredictor` (core inference component)
- `KafkaConsumer` (NEST intake, I-02)
- `KafkaProducer` (prediction output, I-03)
- Model artifacts (`viability_model.pkl`, `scaler.pkl`, metadata)
- XAI layer (SHAP/LIME/fallback explanation)

## 3. Internal Runtime Blocks

1. Intake and validation
2. Metrics aggregation and feature assembly
3. Preprocessing and normalization
4. Model inference
5. Explainability generation
6. Kafka dispatch to Decision Engine

## 4. Non-Functional Requirements

- Prediction latency target (< 500 ms for operational path)
- Repeatable model versioning and metadata traceability
- Explainability payload availability
- Observability through metrics and traces

## 5. Scientific Coherence

ML-NSMF transforms multi-domain state and SLA requirements into a scalar feasibility estimate while preserving feature-level interpretation. This makes it suitable for reproducible evaluation and publication-oriented analysis.
