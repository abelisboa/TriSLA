# Patch Group A Build Governance Review

Phase: PHASE-I5A PATCH_GROUP_A_BUILD_AUTHORIZATION

Execution mode: governance review only. No commit, build, digest generation, deploy, data collection, evidence generation, or campaign execution performed.

## Required Future Build Chain

The future authorized build must follow this chain:

```text
GitHub Commit
-> GitHub Push
-> Build
-> SHA256 Digest
-> Deploy remoto por digest
```

## Required Registry and Digest Controls

```text
REGISTRY = ghcr.io/abelisboa/trisla-sem-csmf
CURRENT_RUNTIME_DIGEST = sha256:1af16f60f1414a5a630f8792caa6540b52e42d1a4f4da8631069efb2f9bb3b23
ROLLBACK_DIGEST = sha256:38fb2396aec9de4bcf9ba430dce70bed0791976e3c6975160ea89101af5c830a
DEPLOYMENT_MODE_REQUIRED = REMOTE_DIGEST_ONLY
```

## Prohibited Paths

```text
latest = PROHIBITED
mutable tags = PROHIBITED
imagem local = PROHIBITED
docker run local = PROHIBITED
kubectl set image sem digest = PROHIBITED
build sem commit = PROHIBITED
deploy sem digest = PROHIBITED
```

## Mandatory Future Phase Entry Rule

```text
1. Executar ssh node006
2. Confirmar hostname=node1
3. Confirmar repositório=/home/porvir5g/gtp5g/trisla
4. Validar digest baseline
5. Somente então iniciar a fase
```

Any deviation requires immediate stop.

## Governance Verdict

```text
BUILD_GOVERNANCE_VALIDATED = YES
GITHUB_COMMIT_REQUIRED = YES
GITHUB_PUSH_REQUIRED = YES
BUILD_AFTER_COMMIT_ONLY = YES
DIGEST_AFTER_AUTHORIZED_BUILD_ONLY = YES
DEPLOY_BY_DIGEST_ONLY = YES
LOCAL_IMAGE_BUILD_ALLOWED = NO
MUTABLE_TAG_ALLOWED = NO
DIRECT_CLUSTER_MUTATION_ALLOWED = NO
AUTHORIZED_FOR_DIGEST_GENERATION = NO
AUTHORIZED_FOR_DEPLOY = NO
NO_COMMIT_PERFORMED = TRUE
NO_BUILD_PERFORMED = TRUE
NO_DIGEST_GENERATED = TRUE
NO_DEPLOY_PERFORMED = TRUE
NO_DATA_COLLECTION_PERFORMED = TRUE
NO_CAMPAIGN_EXECUTED = TRUE
```
