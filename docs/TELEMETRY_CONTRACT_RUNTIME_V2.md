# Telemetria — contrato runtime v2 (PR-01 / PROMPT_39)

- **`telemetry_snapshot`** inclui campos **legados** (`latency`, `rtt`, `jitter`, `cpu`, `memory`) e **aliases v2** (`latency_ms`, `rtt_ms`, `jitter_ms`, `cpu_utilization`, `memory_bytes`) com os **mesmos valores**.
- **`telemetry_snapshot.telemetry_contract_version`**: `"v2"`.
- **`metadata.telemetry_version`**: `"v2"`; **`metadata.telemetry_units`**: mapa de unidades de referência (documentação).
- **Normalização** para SLA agregado avançado: ver PROMPT_35 / fase futura — **não** aplicada neste PR.
