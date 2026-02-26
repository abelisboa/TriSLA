# Decision Engine (TriSLA)

**Role.** The Decision Engine performs SLA admission control by combining: (i) real-time infrastructure signals (CPU, memory, disk, network), (ii) ML-NSMF outputs (risk score + confidence + explanation pointers), and (iii) policy rules that enforce minimum viability thresholds.

## Responsibilities
- Evaluate incoming SLA requests (portal submissions or API calls)
- Correlate request identifiers (intent_id / decision_id) across modules
- Produce a deterministic decision outcome (e.g., ACCEPT / RENEG / REJECT)
- Emit decision events to Kafka for downstream consumers (e.g., BC-NSSMF)

## Inputs and Outputs
### Inputs
- SLA request payload (template_id + form values / requirements)
- SEM-CSMF metadata (NEST / slice type / requirements)
- ML-NSMF prediction package (score, confidence, XAI metadata)
- Observability signals (Prometheus queries)

### Outputs
- Decision response (decision + justification fields)
- Correlation identifiers: intent_id, decision_id
- Kafka decision event (topic configured in deployment)

## Public endpoints (example)
- `POST /api/v1/sla/submit` — submit a SLA request (via Portal backend)
- `GET /health` — liveness check

> Note: endpoint paths may vary by deployment configuration. Always consult `helm/` values.

## Observability
- Prometheus metrics: request count, decision counts, latency histograms
- OpenTelemetry traces: end-to-end spans across SEM/ML/Decision phases

## Troubleshooting (field notes)
- **Common symptom:** decisions consistently return RENEG due to viability threshold not met  
  **Action:** verify the availability of Prometheus signals and the ML prediction payload consistency.


## Decision States

The Decision Engine produces one of three deterministic outcomes:

- **ACCEPT**: The SLA request meets all viability thresholds and can be admitted
- **REJECT**: The SLA request fails critical thresholds and cannot be admitted
- **RENEGOTIATE (RENEG)**: The SLA request partially meets thresholds but requires parameter adjustment

The decision is based on:
1. Real-time infrastructure signals (CPU, memory, disk, network availability)
2. ML-NSMF risk score and confidence level
3. Policy rules configured in the deployment

## Decision Logic Flow

1. Receive SLA request with requirements
2. Query Prometheus for current infrastructure metrics
3. Obtain ML-NSMF prediction (risk score + XAI metadata)
4. Obtain SEM-CSMF semantic processing results (NEST / slice type)
5. Apply policy rules and thresholds
6. Produce deterministic decision outcome
7. Emit decision event to Kafka topic (if configured)
