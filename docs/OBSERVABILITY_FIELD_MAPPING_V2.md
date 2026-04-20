# Mapeamento painéis ↔ campos reais (V2)

Referência mínima **Painel → Campo → Origem → Observação**.  
Contrato de submit: `POST /api/v1/sla/submit` → `metadata` no JSON de resposta.

| Painel | Campo | Origem | Observação |
|--------|-------|--------|------------|
| Saúde E2E | `http_200` | `summary.json` | Runner E2E (`prompt21_multi_domain_validation.py`) |
| Saúde E2E | `total_requests` | `summary.json` | Idem |
| Saúde E2E | `valid_samples` | `summary.json` | HTTP 200 + `telemetry_present` |
| Saúde E2E | `invalid_samples` | `summary.json` | Derivado |
| Telemetria | `telemetry_complete` | `metadata` (submit) | `true` se `len(telemetry_gaps)==0` |
| Telemetria | `telemetry_gaps` | `metadata` (submit) | Lista `domain.field` ausentes |
| Telemetria | `telemetry_complete_ratio` | `summary.json` (runner) | Agregação PR-06 |
| Telemetria | `valid_samples_all_telemetry_fields_non_null` | `summary.json` | Gate estrito snapshot |
| Telemetria | `telemetry_all_domains_non_null_ratio` | `summary.json` | Razão de linhas com todos domínios preenchidos |
| Política | `sla_policy_version` | `metadata` | `v1` / `v2` / `v2_fallback_v1` (`sla_metrics`) |
| Política | `resource_pressure_v1` | `metadata.sla_metrics` | Legado |
| Política | `resource_pressure_v2` | `metadata.sla_metrics` | Com `USE_SLA_V2` no backend |
| Política | `feasibility_score` | `metadata.sla_metrics` | |
| Core | `core.cpu_utilization` | `metadata.telemetry_snapshot.core` | Alias V2; legado `cpu` / `cpu_usage` |
| Core | `core.memory_bytes` | `metadata.telemetry_snapshot.core` | Alias V2; legado `memory` |
| Transport | `transport.jitter_ms` | `metadata.telemetry_snapshot.transport` | Alias V2; legado `jitter` |
| Transport | `transport.rtt_ms` | `metadata.telemetry_snapshot.transport` | Alias V2; legado `rtt` |
| RAN | `ran.prb_utilization` | `metadata.telemetry_snapshot.ran` | |
| RAN | `ran.latency_ms` | `metadata.telemetry_snapshot.ran` | Alias V2; legado `latency` |
| Decisão | `decision` | Corpo JSON submit | `ACCEPT` / `RENEGOTIATE` / `REJECT` |
| Decisão | divergência (futuro) | — | Reservado |
| PromQL resumo | `ran_prb_utilization` | `GET .../prometheus/summary` | Instant query SSOT |
| PromQL resumo | `metadata.telemetry_version` | `GET .../prometheus/summary` | Referência contrato V2 |
| PromQL resumo | `metadata.telemetry_units` | `GET .../prometheus/summary` | Mapa de unidades |

**Nota Core:** em alguns ambientes o snapshot Core pode refletir agregado global/proxy — tratar como observação operacional até granularidade por NF.
