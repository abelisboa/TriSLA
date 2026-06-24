# Patch Group A Deploy Review

Phase: PHASE-I3A PATCH_GROUP_A_IMPLEMENTATION_REVIEW

Execution mode: review only. No deploy performed.

## Current Deployment State

Read-only Kubernetes validation showed:

```text
deployment/trisla-sem-csmf image =
ghcr.io/abelisboa/trisla-sem-csmf@sha256:1af16f60f1414a5a630f8792caa6540b52e42d1a4f4da8631069efb2f9bb3b23

pod/trisla-sem-csmf-56b55c98f-pm9cj imageID =
ghcr.io/abelisboa/trisla-sem-csmf@sha256:1af16f60f1414a5a630f8792caa6540b52e42d1a4f4da8631069efb2f9bb3b23
```

## Official Future Deploy Procedure

Future deployment, if manually approved, must use:

```text
ssh node006
hostname
expect hostname = node1
pull image by full sha256 digest
update deployment by full sha256 digest
validate rollout
validate pod imageID
run smoke validation
register evidence
freeze digest
```

## Digest Pinning Requirement

Deployment command must use:

```text
ghcr.io/abelisboa/trisla-sem-csmf@sha256:<full_digest>
```

Deployment command must not use:

```text
latest
main
mutable tag
local image
partial digest
```

## Post-Deploy Validation Requirements

| Validation | Required |
|---|---|
| `hostname == node1` | YES |
| deployment image equals approved digest | YES |
| pod `imageID` equals approved digest | YES |
| pod restart count recorded | YES |
| SEM health endpoint validated | YES |
| Existing `/api/v1/interpret` functional response preserved | YES |
| Existing `/api/v1/intents` functional response preserved | YES |
| New telemetry fields present only as additive metadata | YES |
| Decision parity check | YES |
| Rollback digest retained | YES |

## Rollback Digest

```text
SEM_CSMF_ROLLBACK_DIGEST = sha256:38fb2396aec9de4bcf9ba430dce70bed0791976e3c6975160ea89101af5c830a
```

## Verdict

```text
DEPLOY_PROCESS_DEFINED = YES
DEPLOY_TRACEABILITY_VALIDATED = YES
DEPLOY_EXECUTED = NO
NO_DEPLOY_PERFORMED = TRUE
```
