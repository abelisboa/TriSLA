# Worktree Remediation Design

Phase: PHASE-I4D WORKTREE REMEDIATION DESIGN

Execution mode: design only. No code change, file removal, file movement, git add, git commit, git stash, git clean, build, digest, deploy, data collection, or campaign execution performed.

## Governance Baseline

```text
PATCH_GROUP_A_ISOLATION_POSSIBLE = YES
PATCH_GROUP_A_COMMIT_STRATEGY_DEFINED = YES
WORKTREE_GOVERNANCE = FAIL
READY_FOR_BUILD_AUTHORIZATION = NO
```

## Classification

```text
PATCH_GROUP_A_FILES = 5
LEGACY_FILES = 785
DOCUMENTATION_FILES = 33
TEMPORARY_FILES = 29
PYCACHE_FILES = 29
UNKNOWN_FILES = 0
```

## Strategy Review

Best strategy for traceability:

```text
Strategy D: Git worktree isolada
```

Fallback:

```text
Strategy A/D: Commit seletivo with strict cached diff review
```

## Traceability

```text
TRACEABILITY_RESTORABLE = YES
```

Traceability is restorable if PATCH_GROUP_A is moved/staged into an isolated clean context before build/digest/deploy.

## Pycache

```text
PYCACHE_RUNTIME_IMPACT = NO
PYCACHE_REMOVAL_REQUIRED = YES
PYCACHE_COMMIT_ALLOWED = NO
PYCACHE_BUILD_ALLOWED = NO
```

Removal is required before clean commit/build, but it was not performed in this design phase.

## Clean Commit

```text
CLEAN_COMMIT_POSSIBLE = YES
PATCH_GROUP_A_ONLY_COMMIT = YES
PATCH_GROUP_A_ONLY_BUILD = YES
PATCH_GROUP_A_ONLY_DIGEST = YES
```

## Build Authorization Blockers

```text
BUILD_BLOCKED_BY_WORKTREE = YES
DIGEST_BLOCKED_BY_WORKTREE = YES
DEPLOY_BLOCKED_BY_WORKTREE = YES
TRACEABILITY_BLOCKED_BY_WORKTREE = YES
```

The blockers are governance/provenance blockers, not PATCH_GROUP_A code blockers.

## Recommended Roadmap

```text
STEP_1 = Manual remediation authorization
STEP_2 = Create isolated worktree or clean clone
STEP_3 = Apply/stage PATCH_GROUP_A only
STEP_4 = Review diff and cached diff
STEP_5 = Create PATCH_GROUP_A-only commit and request build authorization
```

## Final Verdict

```text
CLEAN_COMMIT_POSSIBLE = YES
PATCH_GROUP_A_ONLY_COMMIT = YES
PATCH_GROUP_A_ONLY_BUILD = YES
PATCH_GROUP_A_ONLY_DIGEST = YES
TRACEABILITY_RESTORABLE = YES
PYCACHE_REMOVAL_REQUIRED = YES
PYCACHE_COMMIT_ALLOWED = NO
WORKTREE_REMEDIATION_REQUIRED = YES
RECOMMENDED_STRATEGY = STRATEGY_D_GIT_WORKTREE_ISOLADA
READY_FOR_BUILD_AUTHORIZATION = NO
NO_CODE_CHANGE_PERFORMED = TRUE
NO_BUILD_PERFORMED = TRUE
NO_DIGEST_GENERATED = TRUE
NO_DEPLOY_PERFORMED = TRUE
NO_DATA_COLLECTION_PERFORMED = TRUE
NO_CAMPAIGN_EXECUTED = TRUE
MANUAL_APPROVAL_REQUIRED = YES
NEXT_ALLOWED_PHASE = WORKTREE_REMEDIATION_AUTHORIZATION
```
