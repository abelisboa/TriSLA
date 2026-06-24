# Patch Group A Build Deploy Freeze

Phase: PHASE-I3B PATCH_GROUP_A_IMPLEMENTATION_PACKAGE_FREEZE

## GitHub Workflow

| Item | Frozen rule |
|---|---|
| Branch | Current working branch observed: `e2e-o6-mapping-ssot`; future implementation branch must be explicitly approved before code change |
| Commit strategy | One scoped commit for Patch Group A implementation, plus separate documentation/evidence commit only if manually approved |
| Source of build | GitHub commit only |
| Build trigger | Manual approval required |
| Registry | `ghcr.io/abelisboa/trisla-sem-csmf` |
| Digest strategy | Full SHA256 digest required |
| Deploy strategy | Remote deploy by full digest only |
| Rollback strategy | Restore previous approved digest |

## Required Future Chain

```text
GitHub Commit
-> Build
-> SHA256 Digest
-> Deploy remoto por digest
-> Rollout validation
-> Evidence registration
-> Freeze update
```

## Current Baseline

```text
CURRENT_RUNTIME_DIGEST = sha256:1af16f60f1414a5a630f8792caa6540b52e42d1a4f4da8631069efb2f9bb3b23
ROLLBACK_DIGEST = sha256:38fb2396aec9de4bcf9ba430dce70bed0791976e3c6975160ea89101af5c830a
REGISTRY = ghcr.io/abelisboa/trisla-sem-csmf
NAMESPACE = trisla
DEPLOYMENT = trisla-sem-csmf
```

## Forbidden

```text
latest
tag mutavel
imagem local
digest parcial
kubectl set image sem digest
```

## Required Post-Deploy Proof

- deployment image equals approved digest;
- pod imageID equals approved digest;
- rollout status complete;
- SEM health endpoint OK;
- `/api/v1/interpret` behavior preserved;
- `/api/v1/intents` behavior preserved;
- decision equivalence validated;
- additive telemetry present;
- rollback digest still documented.

## Verdict

```text
BUILD_PROCESS_FROZEN = YES
DEPLOY_PROCESS_FROZEN = YES
ROLLBACK_PROCESS_FROZEN = YES
NO_BUILD_PERFORMED = TRUE
NO_DEPLOY_PERFORMED = TRUE
```
