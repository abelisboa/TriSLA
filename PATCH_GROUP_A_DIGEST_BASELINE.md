# Patch Group A Digest Baseline

Phase: PHASE-I3B PATCH_GROUP_A_IMPLEMENTATION_PACKAGE_FREEZE

Execution mode: package freeze only. No code, build, deploy, campaign, dataset, SSOT, article, architecture, or functional behavior change performed.

## Runtime Digest Freeze

| Field | Value |
|---|---|
| Component | `trisla-sem-csmf` |
| Registry | `ghcr.io/abelisboa/trisla-sem-csmf` |
| Namespace | `trisla` |
| Deployment | `trisla-sem-csmf` |
| Image | `ghcr.io/abelisboa/trisla-sem-csmf` |
| CURRENT_RUNTIME_DIGEST | `sha256:1af16f60f1414a5a630f8792caa6540b52e42d1a4f4da8631069efb2f9bb3b23` |
| ROLLBACK_DIGEST | `sha256:38fb2396aec9de4bcf9ba430dce70bed0791976e3c6975160ea89101af5c830a` |
| Current deployment image | `ghcr.io/abelisboa/trisla-sem-csmf@sha256:1af16f60f1414a5a630f8792caa6540b52e42d1a4f4da8631069efb2f9bb3b23` |
| Rollback image | `ghcr.io/abelisboa/trisla-sem-csmf@sha256:38fb2396aec9de4bcf9ba430dce70bed0791976e3c6975160ea89101af5c830a` |

## Evidence Sources

| Source | Evidence |
|---|---|
| `CURRENT_APPROVED_DIGESTS.md` | Current and rollback digest inventory |
| `baseline-registry/WAVE3A_OPERATIONAL_FREEZE.md` | Current SEM-CSMF operational freeze and rollback pin |
| `baseline-registry/OPERATIONAL_BASELINE_REGISTRY.json` | Current operational baseline registry |
| `baseline-registry/DIGEST_TRACEABILITY_MATRIX.json` | Git/Helm/deployment/pod digest chain |
| `semantic-registry/SEMANTIC_SSOT_POINTER.json` | Semantic runtime authority pointer |
| Kubernetes read-only query | Deployment and pod imageID match current digest |

## Future Digest Rule

Future implementation must produce a new digest through:

```text
GitHub Commit
-> Container Build
-> SHA256 Digest
-> Deploy remoto por digest
-> Rollout validation
-> Freeze registration
```

Forbidden:

```text
latest
tag mutavel
imagem local
digest parcial
kubectl set image sem digest
```

## Verdict

```text
DIGEST_ALIGNMENT = PASS
DIGEST_BASELINE_FROZEN = YES
CURRENT_RUNTIME_DIGEST = sha256:1af16f60f1414a5a630f8792caa6540b52e42d1a4f4da8631069efb2f9bb3b23
ROLLBACK_DIGEST = sha256:38fb2396aec9de4bcf9ba430dce70bed0791976e3c6975160ea89101af5c830a
```
