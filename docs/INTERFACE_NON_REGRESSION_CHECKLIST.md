# Checklist de Não Regressão (Interfaces)

Usar este checklist em cada fase de evolução de interfaces.

## API/Fluxo principal
- [ ] `POST /api/v1/sla/interpret` retorna 200 e payload esperado.
- [ ] `POST /api/v1/sla/submit` retorna 200 e payload esperado.
- [ ] `GET /api/v1/sla/status/{sla_id}` permanece funcional.
- [ ] `GET /api/v1/sla/metrics/{sla_id}` permanece funcional.

## Pipeline inter-serviços
- [ ] Portal Backend continua chamando SEM-CSMF (`/api/v1/interpret`, `/api/v1/intents`).
- [ ] SEM-CSMF continua acionando Decision Engine (`/evaluate`).
- [ ] Decision Engine continua acionando ML-NSMF (`/api/v1/predict`).
- [ ] Orquestração NASP (`/api/v1/nsi/instantiate`) permanece funcional para casos `ACCEPT`.

## Observabilidade / closed-loop
- [ ] `metadata.telemetry_snapshot` continua sendo preenchido no submit.
- [ ] I-01 metadata echo: `DecisionResult.metadata.inbound_metadata` presente quando SEM envia root `metadata` (Wave 1 G3-A).
- [ ] Decisão (`action`, `confidence`, `domains`) inalterada com/sem root `metadata` (parity).
- [ ] Consultas Prometheus (`/api/v1/prometheus/*`) seguem válidas.
- [ ] SLA-Agent ingestão (quando habilitada) permanece funcional.

## Governança / blockchain
- [ ] Fluxo de `register-sla` permanece operacional.
- [ ] Campos `tx_hash`/`block_number` continuam propagados quando disponíveis.
- [ ] `bc_status` segue coerente com retorno do pipeline.

## Runtime e compatibilidade
- [ ] Nenhum endpoint público existente foi removido ou renomeado.
- [ ] Nenhum serviço foi renomeado.
- [ ] Não houve introdução de dependência obrigatória nova.
- [ ] Rollback por flag disponível e testado.
