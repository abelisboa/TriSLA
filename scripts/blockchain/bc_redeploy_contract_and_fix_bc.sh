#!/usr/bin/env bash
set -euo pipefail

NS="${NS:-trisla}"
BESU_RPC="${BESU_RPC:-http://trisla-besu:8545}"
BC_DEPLOY="${BC_DEPLOY:-trisla-bc-nssmf}"
BC_SVC="${BC_SVC:-trisla-bc-nssmf:8083}"

EVD="${EVD:-./evidencias_e2e/$(date +%Y%m%d_%H%M%S)_bc_redeploy}"
mkdir -p "$EVD"

log() { printf "\n[%s] %s\n" "$(date +%H:%M:%S)" "$*" | tee -a "$EVD/run.log" ; }

jsonrpc() {
  local payload="$1"
  kubectl run -n "$NS" rpc-tmp --rm -i --restart=Never --image=curlimages/curl:8.6.0 -- \
    sh -c "curl -s -X POST ${BESU_RPC} -H 'Content-Type: application/json' -d '$payload'" \
    | tee -a "$EVD/run.log"
}

log "=================================================="
log "TriSLA – BC REDEPLOY CONTRACT + FIX (CONTROLADO)"
log "Namespace      : $NS"
log "Besu RPC       : $BESU_RPC"
log "BC Deployment  : $BC_DEPLOY"
log "BC Service     : $BC_SVC"
log "Evidências     : $EVD"
log "=================================================="

log "FASE 0) Gate – pré-requisitos mínimos"
kubectl get ns "$NS" >/dev/null
kubectl get deploy -n "$NS" "$BC_DEPLOY" >/dev/null
kubectl get deploy -n "$NS" trisla-besu >/dev/null
kubectl get svc -n "$NS" trisla-besu >/dev/null

log "FASE 1) Prova – Besu responde e está minerando/blocando (eth_blockNumber)"
BN="$(jsonrpc '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' | sed -n 's/.*"result":"\([^"]*\)".*/\1/p' | tail -n1)"
echo "$BN" > "$EVD/eth_blockNumber.txt"
log "eth_blockNumber = $BN (salvo em $EVD/eth_blockNumber.txt)"

log "FASE 2) Prova – contrato SSOT e contrato runtime NÃO existem (eth_getCode=0x)"
# runtime address (arquivo dentro do pod)
BC_POD="$(kubectl get pod -n "$NS" -l app=trisla-bc-nssmf -o jsonpath='{.items[0].metadata.name}')"
echo "$BC_POD" > "$EVD/bc_pod.txt"
log "BC pod: $BC_POD"

RUNTIME_ADDR="$(kubectl exec -n "$NS" "$BC_POD" -- sh -c "cat /app/src/contracts/contract_address.json 2>/dev/null | sed -n 's/.*\"address\"[[:space:]]*:[[:space:]]*\"\\([^\"]*\\)\".*/\\1/p' | head -n1" || true)"
echo "${RUNTIME_ADDR:-<empty>}" > "$EVD/runtime_contract_address.txt"
log "Endereço runtime (arquivo no BC pod) = ${RUNTIME_ADDR:-<empty>} (salvo em $EVD/runtime_contract_address.txt)"

SSOT_ADDR="$(kubectl get cm -n "$NS" trisla-bc-contract-address -o jsonpath='{.data.contract_address\.json}' 2>/dev/null | sed -n 's/.*\"address\"[[:space:]]*:[[:space:]]*\"\\([^\"]*\\)\".*/\\1/p' | head -n1 || true)"
echo "${SSOT_ADDR:-<empty>}" > "$EVD/ssot_contract_address.txt"
log "Endereço SSOT (ConfigMap) = ${SSOT_ADDR:-<empty>} (salvo em $EVD/ssot_contract_address.txt)"

if [[ -n "${RUNTIME_ADDR:-}" ]]; then
  CODE_RUNTIME="$(jsonrpc "{\"jsonrpc\":\"2.0\",\"method\":\"eth_getCode\",\"params\":[\"${RUNTIME_ADDR}\",\"latest\"],\"id\":1}" | sed -n 's/.*"result":"\([^"]*\)".*/\1/p' | tail -n1)"
  echo "$CODE_RUNTIME" > "$EVD/eth_getCode_runtime.txt"
  log "eth_getCode(runtime) = $CODE_RUNTIME (salvo em $EVD/eth_getCode_runtime.txt)"
fi

if [[ -n "${SSOT_ADDR:-}" ]]; then
  CODE_SSOT="$(jsonrpc "{\"jsonrpc\":\"2.0\",\"method\":\"eth_getCode\",\"params\":[\"${SSOT_ADDR}\",\"latest\"],\"id\":1}" | sed -n 's/.*"result":"\([^"]*\)".*/\1/p' | tail -n1)"
  echo "$CODE_SSOT" > "$EVD/eth_getCode_ssot.txt"
  log "eth_getCode(SSOT) = $CODE_SSOT (salvo em $EVD/eth_getCode_ssot.txt)"
fi

log "FASE 3) Gate – BC-NSSMF readiness real (deve validar RPC + BC_PRIVATE_KEY)"
kubectl run -n "$NS" bc-ready --rm -i --restart=Never --image=curlimages/curl:8.6.0 -- \
  sh -c "curl -sS http://${BC_SVC}/health/ready" \
  | tee "$EVD/bc_health_ready.json" >/dev/null
log "Resposta /health/ready salva em $EVD/bc_health_ready.json"

log "FASE 4) Auditoria – BC-NSSMF tem BC_PRIVATE_KEY configurada?"
kubectl get deploy -n "$NS" "$BC_DEPLOY" -o yaml > "$EVD/bc_deploy.yaml"
if grep -q "BC_PRIVATE_KEY" "$EVD/bc_deploy.yaml"; then
  log "✅ BC_PRIVATE_KEY encontrada no deployment (ver $EVD/bc_deploy.yaml)"
else
  log "❌ BC_PRIVATE_KEY NÃO encontrada no deployment (ver $EVD/bc_deploy.yaml)"
  log "=> Isso explica diretamente a mensagem 'Conta blockchain não disponível'."
fi

log "FASE 5) Descoberta – existe Job/manifest de deploy do contrato no chart/repo?"
# Busca local (repo) – não falha se grep não achar
( grep -R --line-number "deploy-sla-contract" helm/trisla 2>/dev/null || true ) | tee "$EVD/grep_deploy_sla_contract_in_chart.txt" >/dev/null
( grep -R --line-number "deploy_contract" helm/trisla apps 2>/dev/null || true ) | tee "$EVD/grep_deploy_contracts_in_repo.txt" >/dev/null

log "FASE 6) Plano de correção (NÃO APLICA automaticamente – evita regressão)"
cat > "$EVD/PLAN.md" <<'EOF'
# Plano de Correção Controlado – Blockchain (TriSLA)

## Diagnóstico provado
- eth_getCode(runtime)=0x e eth_getCode(SSOT)=0x -> contrato não existe na chain atual.
- Deployment do BC-NSSMF não monta ConfigMap (Mounts: <none>), portanto runtime usa arquivo embutido na imagem.
- Se BC_PRIVATE_KEY não existir no deployment/secret -> BC reporta "Conta blockchain não disponível" e /register-sla retorna 503.

## Correção em 2 blocos (SSOT via Helm)
### Bloco A – Conta blockchain (BC_PRIVATE_KEY)
1) Definir a origem SSOT: Secret Kubernetes (ex.: `trisla-bc-wallet`) com chave `BC_PRIVATE_KEY`.
2) Ajustar helm/trisla templates do bc-nssmf para injetar env:
   - name: BC_PRIVATE_KEY
     valueFrom:
       secretKeyRef:
         name: trisla-bc-wallet
         key: BC_PRIVATE_KEY
3) helm upgrade trisla helm/trisla -n trisla (sem kubectl patch persistente).

### Bloco B – Contrato e SSOT de endereço
4) Reimplantar o SLAContract na chain atual (job canônico S57 do runbook, ou Job no chart).
5) Capturar NEW_CONTRACT_ADDRESS e provar `eth_getCode(NEW)!=0x`.
6) Atualizar ConfigMap `trisla-bc-contract-address` com o novo endereço (SSOT).
7) Ajustar helm/trisla templates do bc-nssmf para montar o ConfigMap em:
   - /app/src/contracts/contract_address.json (subPath)
8) helm upgrade + rollout restart do bc-nssmf (via Helm).

## Validação pós-correção
- BC /health/ready deve indicar rpc_connected=true e private_key_ok=true (ou equivalente).
- POST /api/v1/register-sla -> HTTP 200 com tx_hash + block_number.
- E2E via Portal Backend /api/v1/sla/submit deve passar fase blockchain (sem 503).
EOF

log "✅ Plano gerado em $EVD/PLAN.md"
log "FASE 7) Encerrando sem aplicar mudanças (modo seguro)."
log "Próximo passo: executar o Bloco A e Bloco B via Helm (SSOT), com evidências."
