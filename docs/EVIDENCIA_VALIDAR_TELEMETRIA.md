# Evidência — VALIDAR TELEMETRIA

Checklist do prompt **PROMPT — VALIDAR TELEMETRIA** e como reproduzir.

## Pré-requisitos

1. **Prometheus** acessível (`PROMETHEUS_URL`).
2. **Queries** definidas por ambiente (sem defaults no código):
   - `TELEMETRY_PROMQL_RAN_PRB`
   - `TELEMETRY_PROMQL_RAN_LATENCY`
   - `TELEMETRY_PROMQL_TRANSPORT_RTT`
   - `TELEMETRY_PROMQL_TRANSPORT_JITTER`
   - `TELEMETRY_PROMQL_CORE_CPU`
   - `TELEMETRY_PROMQL_CORE_MEMORY`
3. **Portal backend** com dependências (`httpx`) e pipeline NASP/decision respondendo em `BACKEND_URL` (default `http://localhost:8001`).

## FASE 1 — Prometheus

Para cada variável, validar manualmente ou via script:

- Retorna dados no intervalo?
- Valores **variam** no tempo (evitar série constante)?
- Unidade correta (revisão operador / documentação do exporter).

Script automatizado (janela ~5 min, `query_range`, `step=15s`):

```bash
cd /home/porvir5g/gtp5g/trisla
export PROMETHEUS_URL="http://<prometheus>:9090"
export TELEMETRY_PROMQL_RAN_PRB='...'
# ... demais TELEMETRY_PROMQL_*
python3 apps/portal-backend/tools/validate_telemetry.py --backend-url http://localhost:8001
```

Flags úteis:

- `--skip-phase1` — pula Prometheus (ex.: sem rota ao cluster; **não** conclui critério completo).
- `--skip-phase2` — não chama o backend (só sanity no CSV existente; **não** conclui validação).
- `--output-csv` — caminho alternativo ao default `processed/domain_dataset_v2.csv`.

O script usa apenas **stdlib** + `urllib` (sem `httpx`).

## FASE 2 — Três cenários

O script envia três submissões com `form_values.scenario`:

- `baixa_carga`
- `media_carga`
- `alta_carga`

(Os mesmos requisitos SLA base; a etiqueta de cenário permite distinguir linhas no dataset.)

## FASE 3 — Snapshot

Em cada resposta `200`, conferir:

- `metadata.telemetry_snapshot` presente
- Campos numéricos não nulos quando o cluster e as queries estão corretos
- Valores diferentes entre execuções (variabilidade real)

## FASE 4 — Dataset

Arquivo gerado/atualizado pelo script:

- `processed/domain_dataset_v2.csv`

Colunas:

| Coluna | Origem |
|--------|--------|
| `execution_id` | `metadata.execution_id` |
| `decision` | corpo da resposta |
| `ml_risk_score` | `metadata.ml_risk_score` |
| `ran_prb_utilization_measured` | `telemetry_snapshot.ran.prb_utilization` |
| `transport_rtt_measured` | `telemetry_snapshot.transport.rtt` |
| `core_cpu_usage_measured` | `telemetry_snapshot.core.cpu` |

## FASE 5 — Sanity

O script reporta variância por coluna numérica e correlação de Pearson com decisão codificada (ACCEPT=1, REJECT=0, RENEGOTIATE=0.5), quando há pontos suficientes.

**Critério de sucesso (prompt):**

- Métricas variam
- Métricas podem correlacionar com a decisão

Saída final: `TELEMETRY VALID` ou mensagem indicando ajuste de queries.

## Execução remota (runbook)

Conforme SSOT do projeto, validação em cluster costuma ser feita após `ssh node006` com URLs internas ao namespace (ex.: `PROMETHEUS_URL` do serviço Prometheus).

---

*Documento gerado para suportar auditoria de telemetria; preencher data e operador após execução real.*
