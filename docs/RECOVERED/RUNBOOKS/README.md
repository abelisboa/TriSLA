# Runbooks — canonical index (no duplication)

Do **not** copy these files into `RECOVERED/RUNBOOKS/`. Import paths stay stable; this index is the recovery map.

## Primary

| Document | Role | Cleanup |
|----------|------|---------|
| [../../TRISLA_MASTER_RUNBOOK.md](../../TRISLA_MASTER_RUNBOOK.md) | Master operational runbook (E2E, NASP, BC, SLA-Agent, campaigns) | LINK_FIXED |
| `TRISLA_INFRA_RUNBOOK.md` | Infrastructure incidents (e.g. CNI / Multus) | LINK_ARCHIVED - source not present in current tree |
| [../../TRISLA_E2E_FLOW_CANONICAL.md](../../TRISLA_E2E_FLOW_CANONICAL.md) | Code-aligned E2E sequence (submit -> SEM -> ... -> BC -> SLA-Agent) | LINK_FIXED |
| `TRISLA_BLOCKCHAIN_CANONICAL.md` | Besu / BC-NSSMF SSOT (RPC, genesis, wallet, reset procedure) | LINK_ARCHIVED - source not present in current tree |

## NASP & transport

| Document | Role | Cleanup |
|----------|------|---------|
| `nasp/NASP_DEPLOY_RUNBOOK.md` | NASP deploy / integration | LINK_ARCHIVED - source not present in current tree |
| `TRANSPORT_NASP_INTEGRATION_PROMPT19.md` | Transport / ONOS alignment notes | LINK_ARCHIVED - source not present in current tree |

## Declared infra / portal snapshots (SSOT)

| Document | Role |
|----------|------|
| [../../TRISLA_INFRA_SSOT.md](../../TRISLA_INFRA_SSOT.md) | Large snapshot: deployments, env blocks (including `TELEMETRY_PROMQL_*`) |
| [../../TRISLA_INFRA_SNAPSHOT_20260413T123324Z.md](../../TRISLA_INFRA_SNAPSHOT_20260413T123324Z.md) | Point-in-time infra snapshot |

## Telemetry contracts

| Document | Role | Cleanup |
|----------|------|---------|
| `TELEMETRY_CONTRACT_V2.md` | Contract v2 | LINK_ARCHIVED - source not present in current tree |
| `TELEMETRY_CONTRACT_RUNTIME_V2.md` | Runtime v2 | LINK_ARCHIVED - source not present in current tree |
| [../../PROMQL_SSOT_V2.md](../../PROMQL_SSOT_V2.md) | PromQL SSOT | LINK_FIXED |

## Historical mirror (read-only)

| Location | Note | Cleanup |
|----------|------|---------|
| `backup/source/docs/TRISLA_MASTER_RUNBOOK.md` | Backup mirror; prefer `docs/TRISLA_MASTER_RUNBOOK.md` unless diffing versions | LINK_ARCHIVED - backup source not present in current tree |
| `backup/source/docs/TRISLA_MASTER_RUNBOOK.md.backup` | Older revision | LINK_ARCHIVED - backup source not present in current tree |

## Snapshots (git / cluster captures)

| Location | Role | Cleanup |
|----------|------|---------|
| `snapshots/` | Frozen `kubectl`/helm/git captures (digest lock, rebuild evidence, etc.) | LINK_ARCHIVED - source not present in current tree |

**Count (indexed operational sources above):** 14 distinct paths (excluding duplicate backup master if you always use `docs/`).
