#!/usr/bin/env bash
set -euo pipefail

NS="trisla"
BC_DEPLOY="trisla-bc-nssmf"
BESU_SVC="trisla-besu"
BESU_RPC="http://${BESU_SVC}:8545"
BC_SVC="http://${BC_DEPLOY}:8083"

TS="$(date +%Y%m%d_%H%M%S)"
EVID_DIR="${EVID_DIR:-./evidencias_e2e/${TS}_bc_fix_contract}"
mkdir -p "${EVID_DIR}"

log() { printf "\n[%s] %s\n" "$(date +%H:%M:%S)" "$*" | tee -a "${EVID_DIR}/run.log" ; }
die() { log "ERRO: $*"; exit 1; }

require() {
  command -v "$1" >/dev/null 2>&1 || die "Comando ausente: $1"
}

require kubectl

log "=============================================="
log "TriSLA – BC FIX (SSOT contract address)"
log "Namespace : ${NS}"
log "BC-NSSMF   : deploy/${BC_DEPLOY}"
log "Besu RPC   : ${BESU_RPC}"
log "Evidências : ${EVID_DIR}"
log "=============================================="

log "1) Gate – namespace e deployments"
kubectl get ns "${NS}" >/dev/null
kubectl get deploy -n "${NS}" "${BC_DEPLOY}" >/dev/null
kubectl get svc -n "${NS}" "${BESU_SVC}" >/dev/null

log "2) Coletando endereço de contrato usado pelo BC-NSSMF (arquivo dentro do pod)"
BC_POD="$(kubectl get pod -n "${NS}" -l app=trisla-bc-nssmf -o jsonpath='{.items[0].metadata.name}')"
log "BC pod: ${BC_POD}"
kubectl exec -n "${NS}" "${BC_POD}" -- sh -c "cat /app/src/contracts/contract_address.json" \
  | tee "${EVID_DIR}/bc_contract_address_runtime.json" >/dev/null

RUNTIME_ADDR="$(kubectl exec -n "${NS}" "${BC_POD}" -- sh -c "cat /app/src/contracts/contract_address.json" \
  | sed -n 's/.*"address":[[:space:]]*"\(0x[0-9a-fA-F]\{40\}\)".*/\1/p' | head -n1)"

if [[ -z "${RUNTIME_ADDR}" ]]; then
  die "Não consegui extrair o address do /app/src/contracts/contract_address.json"
fi
log "Endereço runtime (BC-NSSMF): ${RUNTIME_ADDR}"

log "3) Prova – eth_getCode do endereço runtime (deve ser != 0x)"
kubectl run -n "${NS}" rpc-code-runtime --rm -i --restart=Never --image=curlimages/curl:8.6.0 -- \
  sh -c "curl -s -X POST ${BESU_RPC} -H 'Content-Type: application/json' \
  -d '{\"jsonrpc\":\"2.0\",\"method\":\"eth_getCode\",\"params\":[\"${RUNTIME_ADDR}\",\"latest\"],\"id\":1}'" \
  | tee "${EVID_DIR}/eth_getCode_runtime.json" >/dev/null

CODE_RUNTIME="$(cat "${EVID_DIR}/eth_getCode_runtime.json" | sed -n 's/.*"result":[[:space:]]*"\(0x[0-9a-fA-F]*\)".*/\1/p' | head -n1)"
log "eth_getCode(runtime) = ${CODE_RUNTIME}"

if [[ "${CODE_RUNTIME}" != "0x" ]]; then
  log "✅ O contrato runtime EXISTE na chain atual (bytecode != 0x)."
  log "Se ainda há 503, então a causa NÃO é ausência de bytecode; iremos para wallet/privkey depois."
  log "Encerrando aqui para evitar alterações desnecessárias."
  exit 0
fi

log "❌ Confirmado: contrato runtime NÃO existe nesta chain (eth_getCode=0x)."

log "4) Verificando se existe ConfigMap SSOT do endereço do contrato (trisla-bc-contract-address)"
if kubectl get cm -n "${NS}" trisla-bc-contract-address >/dev/null 2>&1; then
  kubectl get cm -n "${NS}" trisla-bc-contract-address -o yaml \
    | tee "${EVID_DIR}/cm_trisla-bc-contract-address.yaml" >/dev/null
  log "✅ ConfigMap SSOT encontrado: trisla-bc-contract-address (dump salvo)."
else
  log "⚠️ ConfigMap SSOT NÃO encontrado. O endereço pode estar embutido na imagem/arquivo do container."
  log "Ainda assim, vamos corrigir via patch controlado do arquivo dentro do pod? NÃO."
  log "Regra anti-regressão: sem patch manual persistente. Precisamos do SSOT via ConfigMap/Helm."
  die "Sem ConfigMap SSOT do contrato. Próximo passo: localizar no chart/values e restaurar SSOT."
fi

log "5) Ação controlada – atualizar o SSOT do endereço do contrato (ConfigMap) para um endereço válido"
log "   -> Informe o novo endereço via variável NEW_CONTRACT_ADDRESS ao executar o script."
log "   -> Exemplo: NEW_CONTRACT_ADDRESS=0xFF... ./bc_fix_contract_ssot.sh"

NEW_ADDR="${NEW_CONTRACT_ADDRESS:-}"
if [[ -z "${NEW_ADDR}" ]]; then
  log "ABORT (seguro): NEW_CONTRACT_ADDRESS não informado. Nenhuma alteração foi feita."
  log "Forneça o endereço do contrato que EXISTE na chain atual (eth_getCode != 0x)."
  exit 2
fi

if [[ ! "${NEW_ADDR}" =~ ^0x[0-9a-fA-F]{40}$ ]]; then
  die "NEW_CONTRACT_ADDRESS inválido: ${NEW_ADDR} (esperado 0x + 40 hex)"
fi

log "6) Gate – validar eth_getCode do NOVO endereço (deve ser != 0x) ANTES de aplicar no SSOT"
kubectl run -n "${NS}" rpc-code-new --rm -i --restart=Never --image=curlimages/curl:8.6.0 -- \
  sh -c "curl -s -X POST ${BESU_RPC} -H 'Content-Type: application/json' \
  -d '{\"jsonrpc\":\"2.0\",\"method\":\"eth_getCode\",\"params\":[\"${NEW_ADDR}\",\"latest\"],\"id\":1}'" \
  | tee "${EVID_DIR}/eth_getCode_new.json" >/dev/null

CODE_NEW="$(cat "${EVID_DIR}/eth_getCode_new.json" | sed -n 's/.*"result":[[:space:]]*"\(0x[0-9a-fA-F]*\)".*/\1/p' | head -n1)"
log "eth_getCode(new) = ${CODE_NEW}"

if [[ "${CODE_NEW}" == "0x" ]]; then
  die "O novo endereço também NÃO tem bytecode (0x). Não vou aplicar no SSOT."
fi

log "✅ Novo endereço tem bytecode. Aplicando no ConfigMap SSOT…"

log "7) Patch do ConfigMap (somente campo address). Mantemos ABI intacta."
kubectl get cm -n "${NS}" trisla-bc-contract-address -o json \
  | tee "${EVID_DIR}/cm_before.json" >/dev/null

# Atualiza o JSON contido na chave contract_address.json (padrão conhecido do projeto)
kubectl patch cm -n "${NS}" trisla-bc-contract-address --type merge \
  -p "{\"data\": {\"contract_address.json\": \"{\\n  \\\"address\\\": \\\"${NEW_ADDR}\\\"\\n}\\n\"}}" \
  | tee "${EVID_DIR}/cm_patch_output.json" >/dev/null

kubectl get cm -n "${NS}" trisla-bc-contract-address -o json \
  | tee "${EVID_DIR}/cm_after.json" >/dev/null

log "8) Reiniciando BC-NSSMF para recarregar SSOT (ConfigMap)."
kubectl rollout restart deploy/"${BC_DEPLOY}" -n "${NS}" | tee "${EVID_DIR}/rollout_restart.txt" >/dev/null
kubectl rollout status deploy/"${BC_DEPLOY}" -n "${NS}" --timeout=180s \
  | tee "${EVID_DIR}/rollout_status.txt" >/dev/null

log "9) Pós-check: confirmar que o BC-NSSMF agora enxerga o endereço atualizado (via arquivo dentro do pod)"
BC_POD2="$(kubectl get pod -n "${NS}" -l app=trisla-bc-nssmf -o jsonpath='{.items[0].metadata.name}')"
kubectl exec -n "${NS}" "${BC_POD2}" -- sh -c "cat /app/src/contracts/contract_address.json" \
  | tee "${EVID_DIR}/bc_contract_address_after_restart.json" >/dev/null

log "10) Teste mínimo – /health/ready e register-sla mínimo (sem Portal) para validar BC↔Besu"
kubectl run -n "${NS}" bc-ready --rm -i --restart=Never --image=curlimages/curl:8.6.0 -- \
  sh -c "curl -s ${BC_SVC}/health/ready" \
  | tee "${EVID_DIR}/bc_health_ready.json" >/dev/null

# register-sla mínimo: usa schema flexível do BC-NSSMF; aqui mandamos payload simples
# Observação: este teste pode retornar 422 se o schema exigir campos extras. Nesse caso, usamos /api/v1/execute-contract.
kubectl run -n "${NS}" bc-register-min --rm -i --restart=Never --image=curlimages/curl:8.6.0 -- \
  sh -c "curl -s -X POST ${BC_SVC}/api/v1/register-sla -H 'Content-Type: application/json' \
  -d '{\"customer\":\"e2e\",\"serviceName\":\"URLLC\",\"slaHash\":\"0x0000000000000000000000000000000000000000000000000000000000000000\",\"slos\":[{\"name\":\"latency\",\"value\":1,\"threshold\":5}]}'" \
  | tee "${EVID_DIR}/bc_register_min.json" >/dev/null

log "✅ Finalizado. Se o 503 sumir, prossiga com o E2E via Portal Backend."
log "Evidências completas em: ${EVID_DIR}"
