# Runbooks — canonical index (no duplication)

Do **not** copy these files into `RECOVERED/RUNBOOKS/`. Import paths stay stable; this index is the recovery map.

## Primary

| Document | Role |
|----------|------|
| [../../TRISLA_MASTER_RUNBOOK.md](../../TRISLA_MASTER_RUNBOOK.md) | Master operational runbook (E2E, NASP, BC, SLA-Agent, campaigns) |
| [../../TRISLA_INFRA_RUNBOOK.md](../../TRISLA_INFRA_RUNBOOK.md) | Infrastructure incidents (e.g. CNI / Multus) |
| [../../TRISLA_E2E_FLOW_CANONICAL.md](../../TRISLA_E2E_FLOW_CANONICAL.md) | Code-aligned E2E sequence (submit → SEM → … → BC → SLA-Agent) |
| [../../TRISLA_BLOCKCHAIN_CANONICAL.md](../../TRISLA_BLOCKCHAIN_CANONICAL.md) | Besu / BC-NSSMF SSOT (RPC, genesis, wallet, reset procedure) |

## NASP & transport

| Document | Role |
|----------|------|
| [../../nasp/NASP_DEPLOY_RUNBOOK.md](../../nasp/NASP_DEPLOY_RUNBOOK.md) | NASP deploy / integration |
| [../../TRANSPORT_NASP_INTEGRATION_PROMPT19.md](../../TRANSPORT_NASP_INTEGRATION_PROMPT19.md) | Transport / ONOS alignment notes |

## Declared infra / portal snapshots (SSOT)

| Document | Role |
|----------|------|
| [../../TRISLA_INFRA_SSOT.md](../../TRISLA_INFRA_SSOT.md) | Large snapshot: deployments, env blocks (including `TELEMETRY_PROMQL_*`) |
| [../../TRISLA_INFRA_SNAPSHOT_20260413T123324Z.md](../../TRISLA_INFRA_SNAPSHOT_20260413T123324Z.md) | Point-in-time infra snapshot |

## Telemetry contracts

| Document | Role |
|----------|------|
| [../../TELEMETRY_CONTRACT_V2.md](../../TELEMETRY_CONTRACT_V2.md) | Contract v2 |
| [../../TELEMETRY_CONTRACT_RUNTIME_V2.md](../../TELEMETRY_CONTRACT_RUNTIME_V2.md) | Runtime v2 |
| [../../PROMQL_SSOT_V2.md](../../PROMQL_SSOT_V2.md) | PromQL SSOT |

## Historical mirror (read-only)

| Location | Note |
|----------|------|
| [../../../backup/source/docs/TRISLA_MASTER_RUNBOOK.md](../../../backup/source/docs/TRISLA_MASTER_RUNBOOK.md) | Backup mirror; prefer `docs/TRISLA_MASTER_RUNBOOK.md` unless diffing versions |
| [../../../backup/source/docs/TRISLA_MASTER_RUNBOOK.md.backup](../../../backup/source/docs/TRISLA_MASTER_RUNBOOK.md.backup) | Older revision |

## Snapshots (git / cluster captures)

| Location | Role |
|----------|------|
| [../../../snapshots/](../../../snapshots/) | Frozen `kubectl`/helm/git captures (digest lock, rebuild evidence, etc.) |

**Count (indexed operational sources above):** 14 distinct paths (excluding duplicate backup master if you always use `docs/`).
