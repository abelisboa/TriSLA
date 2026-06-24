# Patch Group A Isolation Audit

Phase: PHASE-I4C WORKTREE GOVERNANCE AUDIT

## PATCH_SCOPE

Files that belong directly to PATCH_GROUP_A implementation:

```text
apps/sem-csmf/src/main.py
PATCH_GROUP_A_CODE_DIFF.md
PATCH_GROUP_A_SCHEMA_DIFF.md
PATCH_GROUP_A_FUNCTIONAL_SAFETY.md
PATCH_GROUP_A_IMPLEMENTATION_REPORT.md
```

The implementation-relevant code file is:

```text
apps/sem-csmf/src/main.py
```

## DOCUMENTATION_ONLY

PATCH_GROUP_A governance documents generated across I2A-I4C are documentation-only. They should be handled separately from code build inputs.

Examples:

```text
PATCH_GROUP_A_AUTHORIZATION.md
PATCH_GROUP_A_IMPLEMENTATION_PACKAGE.md
PATCH_GROUP_A_POST_IMPLEMENTATION_AUDIT.md
WORKTREE_FULL_INVENTORY.md
```

## TEMPORARY_ARTIFACT

Temporary artifact class:

```text
apps/sem-csmf/src/__pycache__/
```

This does not belong to PATCH_GROUP_A source implementation and should not be committed or included in build context if avoidable.

## LEGACY_WORKTREE

All tracked modifications and untracked files outside the PATCH_SCOPE and governance documentation are classified as legacy worktree state for this audit.

Examples include changes under:

```text
apps/decision-engine/
apps/ml-nsmf/
apps/portal-backend/
apps/sla-agent-layer/
apps/bc-nssmf/
helm/
docs/
scripts/
runtime/
evidence and sprint directories
```

## UNKNOWN

No file is marked UNKNOWN at this audit resolution. The classification is conservative: if it is not PATCH_SCOPE, governance documentation, or pycache, it is legacy worktree.

## Isolation Verdict

```text
PATCH_GROUP_A_ISOLATION_POSSIBLE = YES
PATCH_GROUP_A_FILES_IDENTIFIED = YES
PATCH_GROUP_A_CODE_FILE_COUNT = 1
PATCH_GROUP_A_REQUIRED_REPORT_COUNT = 4
LEGACY_WORKTREE_PRESENT = YES
TEMPORARY_ARTIFACT_PRESENT = YES
```
