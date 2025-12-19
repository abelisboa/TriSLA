# Sprint S3.5.13 — Freeze Científico (Correção Definitiva das Divergências)

## Objetivo do Freeze
Congelar o estado do Helm Chart e BC-NSSMF após eliminação definitiva de todas as divergências detectadas nos Sprints S3.5.7 a S3.5.12, garantindo reprodução científica para banca e artigo.

## Commit de Referência
- **Commit:** `$(git rev-parse --short HEAD)`
- **Branch:** `main`
- **Data:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

## Garantias Técnicas

### Helm Chart
- ✅ Helm lint passa sem erros
- ✅ Render isolado (Besu + BC-NSSMF) gerado com sucesso
- ✅ Nenhuma flag proibida presente (genesis-file, miner-enabled, miner-coinbase, exec, curl)
- ✅ Probes do Besu usam httpGet (porta 8545)
- ✅ Flags do Besu: apenas --network=dev, --rpc-http-enabled, --rpc-http-port=8545, --rpc-http-api=ETH,NET,WEB3

### BC-NSSMF
- ✅ Versão: v3.7.18
- ✅ ImagePullPolicy: Always
- ✅ API convergente com schemas finais:
  - `/api/v1/register-sla`: sla_id, service_name, slos[].threshold
  - `/api/v1/update-sla-status`: sla_id, status (string)
  - `/api/v1/execute-contract`: operation, function, args

### Besu
- ✅ Sem genesis customizado
- ✅ Sem flags obsoletas de miner
- ✅ Probes nativos (httpGet)
- ✅ RPC determinístico (FQDN: svc.cluster.local)

## Artefatos
- `render_besu_bc.yaml` - Render completo do Helm Chart (Besu + BC-NSSMF)
- `render_besu_bc.sha256` - Hash criptográfico SHA256 do render

## Uso para Reprodução Experimental
Este freeze garante que:
1. O Helm Chart renderizado corresponde exatamente ao código publicado
2. Todas as divergências foram eliminadas
3. O estado é imutável e reproduzível
4. Pode ser usado como evidência científica em banca e artigo

## Validações Realizadas
- ❌ Nenhuma ocorrência de `genesis-file`
- ❌ Nenhuma ocorrência de `miner-enabled`
- ❌ Nenhuma ocorrência de `exec:` ou `curl`
- ✅ `httpGet` presente nos probes
- ✅ Porta `8545` configurada corretamente
- ✅ `trisla-bc-nssmf:v3.7.18` referenciado corretamente

## Próximo Passo
Este freeze representa o estado final validado e pronto para uso científico. Nenhuma modificação adicional deve ser feita sem novo sprint de correção.

