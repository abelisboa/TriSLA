# ML-NSMF Interfaces

## Kafka I-03

ML-NSMF -> Decision Engine

Topic: `ml-nsmf-predictions`

Payload:

- feasibility score
- explanation
- SLA metadata
- correlation identifiers (`intent_id`, `nest_id`)

---

## Input

Kafka I-02 from SEM-CSMF

Topic: `sem-csmf-nests`

Payload includes semantically validated NEST data used for feature extraction and prediction.

---

## Interface Contract Notes

- Input/output topics must preserve ordering assumptions required by downstream policies
- Payloads must include model/version metadata for reproducibility
- Failures should be retried with bounded backoff and dead-letter strategy where available

---

## Integration Summary

The interface layer connects semantic intent processing (SEM-CSMF) to policy decisioning (Decision Engine) through ML-NSMF predictions, enabling coherent SLA-aware orchestration.
