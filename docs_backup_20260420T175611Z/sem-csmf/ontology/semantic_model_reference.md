# TriSLA Ontology Semantic Model Reference

## 1. Ontology Profile

- Format: OWL 2.0 (Turtle)
- Namespace: `http://trisla.org/ontology#`
- Runtime location: `apps/sem-csmf/src/ontology/trisla.ttl`
- Runtime components:
  - `loader.py`
  - `reasoner.py`
  - `parser.py`
  - `matcher.py`

## 2. Standards Alignment

The ontology design is aligned with 3GPP TS 28.541 and GSMA NG.116/NG.127 concepts for network slice and SLA semantics.

## 3. Core Class Hierarchy

```text
owl:Thing
├── Intent
│   └── UseCaseIntent
├── SliceRequest
├── Slice
│   ├── eMBB_Slice
│   ├── URLLC_Slice
│   ├── mMTC_Slice
│   └── UseCaseSlice
├── SliceType
├── SLA
├── SLO
├── SLI
├── Metric
│   ├── LatencyMetric
│   ├── ThroughputMetric
│   ├── ReliabilityMetric
│   ├── JitterMetric
│   └── PacketLossMetric
├── Domain
│   ├── RAN
│   ├── Transport
│   └── Core
├── GSTTemplate
├── NESTTemplate
├── Decision
│   ├── AdmissionDecision
│   └── ReconfigurationDecision
├── RiskAssessment
├── SmartContract
│   └── OnChainSLAContract
├── EnforcementAction
├── MLModel
├── Prediction
├── Explanation
├── TelemetrySample
└── ObservationWindow
```

## 4. Key Object Properties

| Property | Domain | Range | Description |
|---|---|---|---|
| `hasSliceType` | Intent | SliceType | Links intent to slice category |
| `hasSLA` | Slice | SLA | Links slice to SLA |
| `hasSLO` | SLA | SLO | Links SLA to SLO |
| `hasSLI` | SLO | SLI | Links SLO to SLI |
| `hasMetric` | SLI | Metric | Links SLI to metric |
| `belongsToSLA` | SLO | SLA | SLO ownership |
| `measuresSLO` | SLI | SLO | SLI measurement target |
| `hasDomain` | Slice | Domain | Domain association |
| `generatedFromGST` | NESTTemplate | GSTTemplate | GST-to-NEST mapping |
| `generatedBy` | Prediction | MLModel | Prediction provenance |
| `explainsPrediction` | Explanation | Prediction | XAI link |

## 5. Key Data Properties

| Property | Domain | Range | Description |
|---|---|---|---|
| `hasLatency` | Slice/SLO/Metric | xsd:float | Max latency (ms) |
| `hasThroughput` | Slice/SLO/Metric | xsd:float | Min throughput (Mbps) |
| `hasReliability` | Slice/SLO/Metric | xsd:float | Reliability (0-1) |
| `hasJitter` | Slice/SLO/Metric | xsd:float | Max jitter (ms) |
| `hasPacketLoss` | Slice/SLO/Metric | xsd:float | Packet loss ratio |
| `hasCoverage` | Slice | xsd:string | Coverage profile |
| `hasMobility` | Slice | xsd:string | Mobility profile |
| `hasDeviceDensity` | Slice | xsd:float | Device density |
| `hasSST` | GSTTemplate | xsd:integer | Slice/Service Type |
| `hasSD` | GSTTemplate | xsd:string | Slice Differentiator |
| `hasViabilityScore` | Prediction | xsd:float | Viability score |

## 6. Reasoning and Validation Workflow

1. Load ontology graph with `OntologyLoader`
2. Initialize reasoner with `SemanticReasoner`
3. Map intent constraints to ontology concepts
4. Validate semantic consistency by slice type and constraints
5. Emit validation result for NEST construction

Example:

```python
from ontology.loader import OntologyLoader
from ontology.reasoner import SemanticReasoner

loader = OntologyLoader()
loader.load(apply_reasoning=True)

reasoner = SemanticReasoner(loader)
reasoner.initialize()

sla_dict = {"latency": "10ms", "throughput": "100Mbps"}
is_valid = reasoner.validate_sla_requirements("URLLC", sla_dict)
```

## 7. Protégé Usage (Reproducible Steps)

1. Open `apps/sem-csmf/src/ontology/trisla.ttl`
2. Run `Reasoner -> Check consistency`
3. Inspect class and property hierarchies
4. Export graph views for publication:
   - Class hierarchy
   - Property hierarchy
   - OntoGraf view

## 8. SPARQL Query Patterns

Intent-to-slice semantic mapping:

```sparql
SELECT ?intent ?sliceType
WHERE {
  ?intent :hasSliceType ?sliceType .
}
```

SLA-to-metric chain:

```sparql
SELECT ?sla ?slo ?sli ?metric
WHERE {
  ?sla :hasSLO ?slo .
  ?slo :hasSLI ?sli .
  ?sli :hasMetric ?metric .
}
```

## 9. Extension Guidelines

- Add new classes as subclasses under existing semantic roots
- Define object/data properties with explicit domain/range
- Preserve naming consistency and namespace conventions
- Re-run consistency checks after each ontology change
- Update SEM-CSMF mapping logic only after ontology validation passes

## 10. Scientific Summary

The ontology provides the formal semantic backbone for TriSLA intent interpretation. It enables machine-checkable semantic consistency before decision scoring, improves reproducibility of SLA-aware experiments, and supports paper-grade traceability of semantic assumptions.
