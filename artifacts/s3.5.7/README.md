# Sprint S3.5.7 — Prova de Convergência Helm (LOCAL)

## Objetivo
Provar que o Helm Chart local está correto, idempotente e pronto para consumo no NASP.

## Artefatos
- `render_besu_bc.yaml` - Render completo do Helm Chart (Besu + BC-NSSMF)
- `render_besu_bc.sha256` - Hash criptográfico SHA256 do render

## Garantias
- ✅ Probes Besu usam httpGet (sem exec/curl)
- ✅ Nenhuma flag obsoleta (miner-enabled, miner-coinbase, genesis-file)
- ✅ Nenhum genesis customizado
- ✅ Chart modular e determinístico
- ✅ Helm lint passa sem erros
- ✅ Render isolado (Besu + BC-NSSMF) gerado com sucesso

## Validações Realizadas
- ❌ Nenhuma ocorrência de `miner-enabled`
- ❌ Nenhuma ocorrência de `miner-coinbase`
- ❌ Nenhuma ocorrência de `genesis-file`
- ❌ Nenhuma ocorrência de `exec:`
- ❌ Nenhuma ocorrência de `curl`
- ✅ `httpGet` presente nos probes
- ✅ Porta `8545` configurada corretamente
- ✅ `trisla-besu` referenciado corretamente
- ✅ `trisla-bc-nssmf` referenciado corretamente

## Próximo Sprint
**S3.5.7_NASP_READONLY** — Prova de convergência via comparação de artefatos

## Data de Geração
Gerado em: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

## Versão do Chart
Chart: trisla
Namespace: trisla
Componentes habilitados: besu, bcNssmf
Componentes desabilitados: semCsmf, mlNsmf, decisionEngine, uiDashboard

