# Modelo Proposto de Interfaces (Sem alterar implementação atual)

Status: proposta arquitetural para padronização; não implica mudança imediata de endpoint.

## Princípios
- Manter 100% de compatibilidade com APIs atuais.
- Introduzir nomenclatura formal por documentação e camada wrapper.
- Separar claramente domínio funcional e responsabilidade.

## Interfaces propostas

### `RAN-I1`
- Responsabilidade: dados/ações RAN usados no ciclo de decisão.
- Origem -> destino: Portal/Decision/SLA-Agent -> coletores/adapter RAN.
- Tipo de dado: PRB, latência RAN, indicadores UE/RAN, comandos de ação RAN.
- Base atual equivalente:
  - `telemetry_snapshot.ran.*`
  - endpoints de agente RAN `/api/v1/agents/ran/*`
  - fluxo via `nasp-adapter` e métricas associadas.

### `TN-I1`
- Responsabilidade: dados/ações de transporte.
- Origem -> destino: Portal/Decision/SLA-Agent -> coletores transport.
- Tipo de dado: RTT, jitter, perda, banda/throughput, ações de transporte.
- Base atual equivalente:
  - `telemetry_snapshot.transport.*`
  - `/api/v1/agents/transport/*`
  - consultas Prometheus transport.

### `CN-I1`
- Responsabilidade: orquestração de core/NSI e estado de execução.
- Origem -> destino: Portal Backend -> NASP Adapter.
- Tipo de dado: pedido de instância de slice, estado de gate, status de orchestration.
- Base atual equivalente:
  - `POST /api/v1/nsi/instantiate`
  - `GET/POST /api/v1/3gpp/gate`
  - `POST /api/v1/sla/register` (adapter).

### `OBS-I1`
- Responsabilidade: coleta, snapshot e ingestão de observabilidade para closed-loop.
- Origem -> destino: Portal/SEM/Decision/SLA-Agent -> Prometheus/collector/ingest.
- Tipo de dado: `telemetry_snapshot`, métricas agregadas, eventos de ingestão pipeline.
- Base atual equivalente:
  - `/api/v1/prometheus/*`
  - `telemetry_snapshot` no submit
  - `SLA_AGENT_PIPELINE_INGEST_URL`
  - endpoints `/api/v1/agents/*`, `/api/v1/metrics/realtime`.

### `BC-I1`
- Responsabilidade: governança e trilha blockchain de SLA.
- Origem -> destino: Portal Backend (e fluxos internos) -> BC-NSSMF/Besu.
- Tipo de dado: register/update contract, `tx_hash`, `block_number`, status de commit.
- Base atual equivalente:
  - `POST /api/v1/register-sla`
  - `POST /api/v1/update-sla-status`
  - `POST /api/v1/execute-contract`.

## Observação de compatibilidade
- Esta proposta define **nomes e responsabilidades**; endpoints atuais permanecem como implementação subjacente.
