# XAI View - Explainable AI Visualization

## Overview

The XAI (Explainable AI) View provides transparency into the SLA decision-making process. It displays the reasoning behind each SLA acceptance, rejection, or renegotiation recommendation.

## Components

### XAIResultPanel

Located at: `src/components/XAI/XAIResultPanel.tsx`

Displays the following information:

- **Decision**: ACCEPT / REJECT / RENEG with visual indicator
- **Risk Score**: 0-100% with progress bar
- **Risk Level**: LOW / MEDIUM / HIGH
- **Confidence**: ML model confidence score
- **Viability Score**: SLA feasibility score
- **Domains Evaluated**: RAN, Transport, Core
- **Justification**: Natural language explanation
- **Feature Importance**: Top contributing factors (if available)
- **Blockchain Confirmation**: TX hash and block number

## Usage

```tsx
import XAIResultPanel from './components/XAI/XAIResultPanel';

<XAIResultPanel
  slaId="sla-123"
  xai={{
    decision: 'ACCEPT',
    risk_score: 0.25,
    risk_level: 'low',
    confidence: 0.99,
    viability_score: 0.85,
    justification: 'SLA accepted. Low risk predicted.',
    domains_evaluated: ['RAN', 'Transport', 'Core'],
  }}
  txHash="0x3d84417..."
  blockNumber={101}
/>
```

## Data Source

XAI data is provided by the Decision Engine and returned in the SLA submission response:

```json
{
  "decision": "ACCEPT",
  "ml_prediction": {
    "risk_score": 0.25,
    "risk_level": "low",
    "confidence": 0.99,
    "viability_score": 0.85
  },
  "justification": "SLA eMBB aceito. ML prevê risco BAIXO...",
  "system_xai": {
    "domains_evaluated": ["RAN", "Transport", "Core"]
  }
}
```

## Scientific Requirement

This visualization is a **scientific requirement** for the TriSLA research project. It provides evidence of:

1. **Transparency**: Users can understand why decisions were made
2. **Explainability**: ML predictions are interpretable
3. **Accountability**: Blockchain confirmation ensures immutability
