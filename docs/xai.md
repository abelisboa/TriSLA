# Explainable AI (XAI) in TriSLA

## Overview

TriSLA integrates Explainable AI capabilities to provide transparency in SLA admission decisions. Every decision is accompanied by human-interpretable explanations.

## XAI Components

### Risk Assessment

| Metric | Description | Range |
|--------|-------------|-------|
| Risk Score | Probability of SLA violation | 0.0 - 1.0 |
| Risk Level | Categorical classification | LOW, MEDIUM, HIGH |
| Confidence | Model certainty | 0.0 - 1.0 |
| Viability Score | Overall feasibility | 0.0 - 1.0 |

### Feature Importance

The ML model provides feature importance scores for each decision:

- latency
- throughput
- reliability
- jitter
- packet_loss
- cpu_utilization
- memory_utilization
- network_bandwidth_available
- active_slices_count
- slice_type_encoded

### Justification

Each decision includes a natural language explanation:

```
"SLA eMBB accepted. ML predicts LOW risk (score: 0.09). 
SLOs viable. Domains: RAN, Transport."
```

## Decision Types

| Decision | Description |
|----------|-------------|
| ACCEPT | SLA can be fulfilled |
| REJECT | SLA cannot be fulfilled |
| RENEG | SLA requires renegotiation |

## API Response

```json
{
  "decision": "ACCEPT",
  "ml_risk_score": 0.094,
  "ml_risk_level": "low",
  "confidence": 0.5,
  "reasoning": "SLA eMBB accepted...",
  "metadata": {
    "ml_features_importance": {
      "reliability": 0.424,
      "latency": 0.189
    }
  }
}
```
