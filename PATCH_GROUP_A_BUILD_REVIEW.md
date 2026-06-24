# Patch Group A Build Review

Phase: PHASE-I3A PATCH_GROUP_A_IMPLEMENTATION_REVIEW

Execution mode: review only. No build performed.

## Current Build Governance

The active governance rule is digest-only:

```text
GitHub Commit
-> GitHub Push
-> Controlled Container Build
-> SHA256 Digest
-> Remote Deploy by Digest
-> Rollout Validation
-> Freeze Registration
```

## Current SEM-CSMF Image State

| Item | Value |
|---|---|
| Component | `trisla-sem-csmf` |
| Registry | `ghcr.io/abelisboa/trisla-sem-csmf` |
| Current approved digest | `sha256:1af16f60f1414a5a630f8792caa6540b52e42d1a4f4da8631069efb2f9bb3b23` |
| Current deployment image | `ghcr.io/abelisboa/trisla-sem-csmf@sha256:1af16f60f1414a5a630f8792caa6540b52e42d1a4f4da8631069efb2f9bb3b23` |
| Rollback digest | `sha256:38fb2396aec9de4bcf9ba430dce70bed0791976e3c6975160ea89101af5c830a` |
| Helm SSOT | `helm/trisla/values.yaml#semCsmf` |
| Operational freeze | `baseline-registry/WAVE3A_OPERATIONAL_FREEZE.md` |

## Future Build Requirements

| Requirement | Status |
|---|---|
| Build must originate from explicit Git commit | REQUIRED |
| Build must be pushed to GHCR | REQUIRED |
| Full SHA256 digest must be captured | REQUIRED |
| Helm/deploy reference must use digest, not mutable tag | REQUIRED |
| Build manifest must record commit, image, digest, timestamp, and rollback digest | REQUIRED |
| No local-only image may be used | REQUIRED |
| No `latest` or floating tag may be used | REQUIRED |

## Forbidden Build Paths

```text
docker latest
docker tag mutable
main without digest
local image
partial sha256
reconstructed digest
```

## Build Validation Gates

Future implementation build review must validate:

- source commit matches implementation review approval;
- image digest is full SHA256;
- digest is visible in GHCR/build manifest;
- build artifact has no unrelated component changes;
- old digest remains recorded for rollback.

## Verdict

```text
BUILD_PROCESS_DEFINED = YES
BUILD_TRACEABILITY_VALIDATED = YES
BUILD_EXECUTED = NO
NO_BUILD_PERFORMED = TRUE
FLOATING_TAG_ALLOWED = NO
```
