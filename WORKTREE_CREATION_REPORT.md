# Worktree Creation Report

Phase: PHASE-I4F WORKTREE_ISOLATED_ENVIRONMENT_CREATION

## Validation Summary

```text
HOST_VALIDATION = PASS
HOST_EXPECTED = node1
HOST_OBSERVED = node1
REPOSITORY_VALIDATION = PASS
REPOSITORY_EXPECTED = /home/porvir5g/gtp5g/trisla
REPOSITORY_OBSERVED = /home/porvir5g/gtp5g/trisla
GOVERNANCE_VALIDATION = PASS
DIGEST_BASELINE_VALIDATED = PASS
```

Note: SSH emitted `Load key "/home/porvir5g/.ssh/id_rsa": Permission denied`, but the remote command completed successfully and returned `node1`.

## Source and Target

```text
source repository = /home/porvir5g/gtp5g/trisla
source branch = e2e-o6-mapping-ssot
source HEAD = 9ddd90889d491720ae806ea211c25b6c939adf78
isolated worktree path = /home/porvir5g/gtp5g/trisla_patch_group_a_isolated
isolated branch = phase-i4f-patch-group-a-isolated-20260624
isolated HEAD = 9ddd90889d491720ae806ea211c25b6c939adf78
```

## Worktree Creation Result

Command outcome:

```text
Preparing worktree (new branch 'phase-i4f-patch-group-a-isolated-20260624')
HEAD is now at 9ddd9088 RC-P20-09: portal digest deploy - RC-P20-01/03/04A approved changes
```

Initial checkout status:

```text
clean checkout from source HEAD before PATCH_GROUP_A transfer
```

## Transfer Performed

PATCH_GROUP_A implementation transferred:

```text
apps/sem-csmf/src/main.py
```

PATCH_GROUP_A documentation/governance transferred:

```text
PATCH_GROUP_A_*.md
WORKTREE_REMEDIATION_AUTHORIZATION.md
WORKTREE_REMEDIATION_DESIGN.md
WORKTREE_CREATION_PLAN.md
```

## Restrictions Preserved

```text
AUTHORIZED_FOR_BUILD = NO
AUTHORIZED_FOR_DIGEST = NO
AUTHORIZED_FOR_DEPLOY = NO
NO_BUILD_PERFORMED = TRUE
NO_DIGEST_GENERATED = TRUE
NO_DEPLOY_PERFORMED = TRUE
NO_DATA_COLLECTION_PERFORMED = TRUE
NO_CAMPAIGN_EXECUTED = TRUE
```

## Report Verdict

```text
ISOLATED_WORKTREE_CREATED = YES
WORKTREE_PATH = /home/porvir5g/gtp5g/trisla_patch_group_a_isolated
WORKTREE_BRANCH = phase-i4f-patch-group-a-isolated-20260624
WORKTREE_HEAD = 9ddd90889d491720ae806ea211c25b6c939adf78
PATCH_GROUP_A_TRANSFERRED = YES
RUNTIME_ALTERED = NO
CLUSTER_ALTERED = NO
```
