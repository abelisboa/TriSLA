# Sprint S3.5.15 — Eliminação de Divergências

## Objetivo
Eliminar definitivamente todas as divergências detectadas no Helm Chart:
- Remover referências a `genesis-file`
- Trocar probes do Besu de `httpGet` para `tcpSocket`
- Eliminar duplicidade do Besu (subchart)
- Limpar dependências do Helm Chart

## Commit de Referência
- **Commit:** `$(git rev-parse --short HEAD)`
- **Branch:** `main`
- **Data:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

## Validações Realizadas

### ✅ Sem flags proibidas
- ❌ Nenhuma ocorrência de `genesis-file`
- ❌ Nenhuma ocorrência de `BESU_GENESIS_FILE`
- ❌ Nenhuma ocorrência de `miner-enabled` ou `miner-coinbase`
- ❌ Nenhuma ocorrência de `latest`
- ❌ Nenhuma ocorrência de `exec:` ou `curl`

### ✅ Probes do Besu
- ✅ `livenessProbe`: `tcpSocket` na porta `8545`
- ✅ `readinessProbe`: `tcpSocket` na porta `8545`
- ✅ Delays configurados: liveness (30s), readiness (10s)

### ✅ Duplicidade do Besu
- ✅ Apenas 1 Deployment do Besu no render
- ✅ Nenhum pod `trisla-trisla-besu`
- ✅ Subchart `trisla-besu` removido de `values-nasp.yaml`

### ✅ Helm Lint
- ✅ `helm lint` passa sem erros
- ✅ Nenhuma dependência fantasma

## Artefatos
- `render_besu_bc.yaml` - Render completo do Helm Chart (Besu + BC-NSSMF)
- `render_besu_bc.sha256` - Hash criptográfico SHA256 do render

## Próximo Deploy NASP
Após este sprint, o próximo deploy NASP deve resultar em:
- ✅ Besu Running 1/1 Ready, sem restarts por probe
- ✅ BC-NSSMF healthy com `rpc_connected: true`
- ✅ Render sem `genesis-file`/`miner`/`latest`
- ✅ Sem duplicidade `trisla-trisla-besu`
- ✅ `helm lint` sem falha por dependência

