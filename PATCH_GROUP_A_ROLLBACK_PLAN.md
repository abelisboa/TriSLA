# Patch Group A Rollback Plan

Phase: PHASE-I3A PATCH_GROUP_A_IMPLEMENTATION_REVIEW

Execution mode: review only. No rollback executed.

## Rollback Anchor

Current SEM-CSMF operational digest:

```text
sha256:1af16f60f1414a5a630f8792caa6540b52e42d1a4f4da8631069efb2f9bb3b23
```

Current SEM-CSMF rollback digest:

```text
sha256:38fb2396aec9de4bcf9ba430dce70bed0791976e3c6975160ea89101af5c830a
```

## Technical Rollback

If future Patch Group A implementation is deployed and fails validation:

```text
kubectl set image deployment/trisla-sem-csmf -n trisla \
  sem-csmf=ghcr.io/abelisboa/trisla-sem-csmf@sha256:38fb2396aec9de4bcf9ba430dce70bed0791976e3c6975160ea89101af5c830a

kubectl rollout status deployment/trisla-sem-csmf -n trisla
kubectl get deployment trisla-sem-csmf -n trisla -o jsonpath='{.spec.template.spec.containers[0].image}'
kubectl get pods -n trisla -l app=trisla-sem-csmf -o jsonpath='{.items[*].status.containerStatuses[*].imageID}'
```

## Operational Rollback

Rollback validation must record:

- operator and timestamp;
- old failed digest;
- restored rollback digest;
- pod name and restart count;
- health endpoint status;
- SEM interpretation smoke test status;
- admission path smoke test status.

## Scientific Rollback

Rollback must preserve:

- existing scientific baseline claims;
- existing score/decision behavior;
- existing ML behavior;
- existing ontology/GST/NEST semantics;
- existing frozen figures and datasets;
- `RESULTS_FREEZE_MAIN` status.

No failed telemetry values may be used as scientific evidence unless explicitly labeled as failed implementation evidence.

## Dataset Rollback

If future campaign/evidence was started after implementation:

- quarantine the new evidence pack;
- do not merge with frozen datasets;
- do not regenerate official figures;
- mark new dataset as `INVALIDATED_BY_ROLLBACK`;
- preserve logs for forensic audit only.

## Evidence Rollback

Rollback evidence must include:

- failed digest;
- rollback digest;
- deployment image before/after;
- pod imageID before/after;
- validation commands and outputs;
- final status report.

## Verdict

```text
ROLLBACK_DEFINED = YES
ROLLBACK_TRACEABILITY_VALIDATED = YES
ROLLBACK_DIGEST_DEFINED = YES
ROLLBACK_EXECUTED = NO
```
