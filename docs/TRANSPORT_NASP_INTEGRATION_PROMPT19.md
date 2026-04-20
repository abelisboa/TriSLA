# Integração Transport NSSMF ↔ ONOS (PROMPT_19)

## Objectivo

Ligar o **ciclo de orquestração NASP** (`deploy_ns`) ao **controlador ONOS** via REST **intents**, com:

- **URL e credenciais configuráveis** (`ONOS_*` — sem hardcode do IP legado `67.205.130.238`)
- **Feature flag** `ENABLE_TRANSPORT` (default **desligado** para não alterar o comportamento anterior)
- **Idempotência**: antes de criar intents, remoção opcional via API (`ONOS_INTENT_IDEMPOTENT`)
- **Falha não fatal**: erro de Transport é registado; **não** aborta o deploy de Core/RAN já concluído antes deste bloco

## Código

- **Ficheiro:** `NASP/nasp/src/services/helm_deployments.py`
- **Variáveis:** ver `NASP/nasp/env.transport.example`

## Variáveis de ambiente

| Variável | Significado | Default |
|----------|-------------|---------|
| `ENABLE_TRANSPORT` | Activa `deploy_transport_network` no `deploy_ns` | `0` / desligado |
| `ONOS_REST_URL` | Base URL REST (`http://host:8181`) | `http://127.0.0.1:8181` |
| `ONOS_USER` / `ONOS_PASSWORD` | Basic auth | `onos` / `rocks` |
| `ONOS_INTENT_MODE` | `fase2`, `legacy`, ou `json` | `fase2` |
| `ONOS_INTENTS_JSON_FILE` | Caminho JSON se `ONOS_INTENT_MODE=json` | — |
| `ONOS_INTENT_IDEMPOTENT` | Apagar intents existentes antes de criar | `1` |

## Decision Engine / TriSLA

- **Nenhuma** alteração ao Decision Engine nem ao pipeline TriSLA neste prompt; apenas **NASP** (Transport NSSMF).

## Evidências

- `evidencias/PROMPT19_TRANSPORT_NASP/` (comandos `curl` e validação)
