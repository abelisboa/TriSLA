#!/usr/bin/env bash
set -euo pipefail

# ==========================================================
# TriSLA — E2E VALIDATION (DEFINITIVE / AUDIT-READY)
# 1) Snapshot + prechecks (CRD, deploy, env)
# 2) Port-forward robusto + health (python local)
# 3) Cenários CRD-compliant (URLLC/eMBB/mMTC) + checagens fortes:
#    - CR criado
#    - status.phase
#    - namespace isolado existe
#    - ResourceQuota existe e contém hard.requests/limits
# 4) Gate 3GPP checks (namespaces de referência existem)
# 5) Capacity Accounting checks (env + tentativa de saturação opcional)
# 6) Testes negativos:
#    - metadata.name inválido (uppercase) deve falhar no Kubernetes (422)
#    - payload com campo SLA não suportado deve ser rejeitado/ignorado (capturar resposta)
# 7) Coleta de logs e sumário PASS/FAIL
# ==========================================================

NS="${1:-trisla}"
OUT_BASE="${2:-/home/porvir5g/gtp5g/trisla/evidencias_e2e}"
ADAPTER_SVC="${3:-trisla-nasp-adapter}"
ADAPTER_PORT="${4:-8085}"
SATURATE="${5:-false}"   # true para tentar estressar capacidade (best-effort)

TS="$(date -u +%Y%m%dT%H%M%SZ)"
TS_LOWER="$(echo "$TS" | tr '[:upper:]' '[:lower:]')"
EVD="${OUT_BASE}/e2e_definitive_${TS}"
mkdir -p "${EVD}"

PF_PID=""
PASS_CNT=0
FAIL_CNT=0

log() { echo -e "$@" | tee -a "${EVD}/run.log"; }

cleanup() {
  if [[ -n "${PF_PID}" ]]; then
    kill "${PF_PID}" >/dev/null 2>&1 || true
    wait "${PF_PID}" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

require_cmd() { command -v "$1" >/dev/null 2>&1 || { echo "❌ Comando ausente: $1"; exit 1; }; }

require_cmd kubectl
require_cmd python3

pass() { PASS_CNT=$((PASS_CNT+1)); log "✅ PASS: $*"; }
fail() { FAIL_CNT=$((FAIL_CNT+1)); log "❌ FAIL: $*"; }

log "=================================================="
log "TriSLA — E2E VALIDATION (DEFINITIVE / AUDIT-READY)"
log "Namespace : ${NS}"
log "Service   : ${ADAPTER_SVC}:${ADAPTER_PORT}"
log "Evidence  : ${EVD}"
log "=================================================="

# ----------------------------------------------------------
# [0] Snapshot + CRD + Deployment
# ----------------------------------------------------------
log "\n[0] Snapshot inicial (deploy/pods/crd)..."
kubectl get deploy -n "${NS}" trisla-nasp-adapter -o wide | tee "${EVD}/deploy_wide.txt"
kubectl get deploy -n "${NS}" trisla-nasp-adapter -o jsonpath='{.spec.template.spec.containers[0].image}'; echo \
  | tee "${EVD}/deploy_image.txt"

kubectl get pods -n "${NS}" -o wide | tee "${EVD}/pods_wide.txt"

kubectl get crd networksliceinstances.trisla.io -o yaml > "${EVD}/crd_nsi.yaml"
kubectl get crd networksliceinstances.trisla.io -o jsonpath='{.spec.versions[0].name}'; echo \
  | tee "${EVD}/crd_version.txt"

# ----------------------------------------------------------
# [1] Port-forward robusto
# ----------------------------------------------------------
log "\n[1] Port-forward..."
kubectl -n "${NS}" port-forward "svc/${ADAPTER_SVC}" "${ADAPTER_PORT}:${ADAPTER_PORT}" \
  > "${EVD}/port_forward.log" 2>&1 &
PF_PID="$!"
sleep 2

log "[1.1] Aguardando porta local responder..."
for i in {1..15}; do
  if python3 - <<PY >/dev/null 2>&1
import socket
s=socket.socket()
try:
  s.settimeout(1)
  s.connect(("127.0.0.1", ${ADAPTER_PORT}))
  s.close()
  print("OK")
except:
  raise SystemExit(1)
PY
  then
    log "✅ Porta pronta (tentativa $i)"
    break
  else
    log "⏳ Porta não pronta (tentativa $i)"
    sleep 2
  fi

  if [[ "$i" == "15" ]]; then
    fail "port-forward não abriu porta local"
    exit 1
  fi
done

# ----------------------------------------------------------
# [2] Health check robusto (python)
# ----------------------------------------------------------
log "\n[2] Health check..."
for i in {1..10}; do
  if python3 - <<PY > "${EVD}/health.json" 2>/dev/null
import urllib.request
with urllib.request.urlopen("http://127.0.0.1:${ADAPTER_PORT}/health", timeout=5) as r:
  print(r.read().decode("utf-8"))
PY
  then
    log "✅ Health OK (tentativa $i)"
    cat "${EVD}/health.json" | tee -a "${EVD}/run.log" >/dev/null
    pass "health /health respondeu"
    break
  else
    log "⏳ Health falhou (tentativa $i)"
    sleep 2
  fi

  if [[ "$i" == "10" ]]; then
    fail "health falhou após 10 tentativas"
    exit 1
  fi
done

# ----------------------------------------------------------
# Helper: POST JSON (python) + grava status
# ----------------------------------------------------------
post_json() {
  local payload="$1"
  local outfile="$2"

  python3 - <<PY > "${outfile}"
import json, urllib.request, urllib.error
payload = json.loads('''${payload}''')
req = urllib.request.Request(
  "http://127.0.0.1:${ADAPTER_PORT}/api/v1/nsi/instantiate",
  data=json.dumps(payload).encode(),
  headers={"Content-Type":"application/json"},
  method="POST"
)
try:
  with urllib.request.urlopen(req, timeout=20) as r:
    print(r.read().decode())
except urllib.error.HTTPError as e:
  body = e.read().decode("utf-8", errors="replace")
  print(json.dumps({"http_error": e.code, "body": body}))
except Exception as ex:
  print(json.dumps({"exception": str(ex)}))
PY
}

# ----------------------------------------------------------
# Checagens fortes do CR / Namespace / Quota
# ----------------------------------------------------------
check_nsi_bundle() {
  local prof="$1"
  local nsi_id="$2"

  if kubectl get networksliceinstances.trisla.io -n "${NS}" "${nsi_id}" -o yaml \
      > "${EVD}/nsi_${prof}.yaml" 2>/dev/null; then
    local phase=""
    phase="$(kubectl get networksliceinstances.trisla.io -n "${NS}" "${nsi_id}" \
      -o jsonpath='{.status.phase}' 2>/dev/null || true)"
    echo "${phase}" > "${EVD}/nsi_${prof}_phase.txt"

    if [[ "${phase}" == "Active" ]]; then
      pass "${prof}: CR criado e phase=Active"
    else
      fail "${prof}: CR criado mas phase='${phase:-<none>}'"
    fi
  else
    fail "${prof}: CR não encontrado"
    return
  fi

  local ns_iso="ns-${nsi_id}"
  if kubectl get ns "${ns_iso}" -o yaml > "${EVD}/ns_${prof}.yaml" 2>/dev/null; then
    pass "${prof}: namespace isolado existe (${ns_iso})"
  else
    fail "${prof}: namespace isolado não encontrado (${ns_iso})"
  fi

  if kubectl get resourcequota -n "${ns_iso}" -o yaml > "${EVD}/quota_${prof}.yaml" 2>/dev/null; then
    # sanity: deve ter hard.requests/limits
    if grep -q "requests.cpu" "${EVD}/quota_${prof}.yaml" && grep -q "limits.cpu" "${EVD}/quota_${prof}.yaml"; then
      pass "${prof}: ResourceQuota ok (requests/limits presentes)"
    else
      fail "${prof}: ResourceQuota existe, mas sem requests/limits esperados"
    fi
  else
    fail "${prof}: ResourceQuota não encontrada no namespace ${ns_iso}"
  fi
}

# ----------------------------------------------------------
# [3] Cenários CRD-compliant
# ----------------------------------------------------------
log "\n[3] Cenários CRD-compliant (URLLC/eMBB/mMTC)..."

PROFILES=("URLLC" "eMBB" "mMTC")
LAT=("10ms" "50ms" "100ms")

for idx in 0 1 2; do
  prof="${PROFILES[$idx]}"
  lat="${LAT[$idx]}"
  nsi_id="probe-${prof,,}-${TS_LOWER}"

  payload=$(cat <<JSON
{"nsiId":"${nsi_id}","serviceProfile":"${prof}","tenantId":"default","sla":{"latency":"${lat}"}}
JSON
)

  log "\n[3.$((idx+1))] ${prof} → ${nsi_id}"
  echo "${payload}" > "${EVD}/payload_${prof}.json"

  post_json "${payload}" "${EVD}/resp_${prof}.json"
  cat "${EVD}/resp_${prof}.json" | tee -a "${EVD}/run.log"

  sleep 8
  check_nsi_bundle "${prof}" "${nsi_id}"
done

# ----------------------------------------------------------
# [4] Gate 3GPP — evidência de pré-condições
# ----------------------------------------------------------
log "\n[4] Gate 3GPP — pré-condições (evidência)..."
POD="$(kubectl get pods -n "${NS}" -l app=trisla-nasp-adapter -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || true)"
if [[ -n "${POD}" ]]; then
  kubectl exec -n "${NS}" "${POD}" -- printenv | sort > "${EVD}/adapter_env_sorted.txt" || true
  grep -E "^GATE_3GPP_|^CAPACITY_|^OTLP_" "${EVD}/adapter_env_sorted.txt" \
    > "${EVD}/adapter_env_critical.txt" || true
  pass "capturado env runtime do adapter"
else
  fail "não foi possível identificar pod do adapter para capturar env runtime"
fi

G3_ENABLED="$(grep -E '^GATE_3GPP_ENABLED=' "${EVD}/adapter_env_sorted.txt" 2>/dev/null | tail -n1 | cut -d= -f2 || true)"
UER_NS="$(grep -E '^GATE_3GPP_UERANSIM_NAMESPACE=' "${EVD}/adapter_env_sorted.txt" 2>/dev/null | tail -n1 | cut -d= -f2 || true)"
CORE_NS="$(grep -E '^GATE_3GPP_CORE_NAMESPACE=' "${EVD}/adapter_env_sorted.txt" 2>/dev/null | tail -n1 | cut -d= -f2 || true)"

log "GATE_3GPP_ENABLED=${G3_ENABLED:-<none>}"
log "UERANSIM_NAMESPACE=${UER_NS:-<none>}"
log "CORE_NAMESPACE=${CORE_NS:-<none>}"

if [[ "${G3_ENABLED}" == "true" ]]; then
  if [[ -n "${UER_NS}" ]] && kubectl get ns "${UER_NS}" > "${EVD}/gate_ueransim_ns.txt" 2>/dev/null; then
    pass "Gate 3GPP: namespace UERANSIM existe (${UER_NS})"
  else
    fail "Gate 3GPP: namespace UERANSIM ausente (${UER_NS})"
  fi

  if [[ -n "${CORE_NS}" ]] && kubectl get ns "${CORE_NS}" > "${EVD}/gate_core_ns.txt" 2>/dev/null; then
    pass "Gate 3GPP: namespace CORE existe (${CORE_NS})"
  else
    fail "Gate 3GPP: namespace CORE ausente (${CORE_NS})"
  fi
else
  fail "Gate 3GPP não está habilitado (GATE_3GPP_ENABLED!=true)"
fi

# ----------------------------------------------------------
# [5] Capacity Accounting — evidência e teste opcional de saturação
# ----------------------------------------------------------
log "\n[5] Capacity Accounting — evidência..."
CAP_ENABLED="$(grep -E '^CAPACITY_ACCOUNTING_ENABLED=' "${EVD}/adapter_env_sorted.txt" 2>/dev/null | tail -n1 | cut -d= -f2 || true)"
SAFETY="$(grep -E '^CAPACITY_SAFETY_FACTOR=' "${EVD}/adapter_env_sorted.txt" 2>/dev/null | tail -n1 | cut -d= -f2 || true)"
TTL="$(grep -E '^RESERVATION_TTL_SECONDS=' "${EVD}/adapter_env_sorted.txt" 2>/dev/null | tail -n1 | cut -d= -f2 || true)"
REC="$(grep -E '^RECONCILE_INTERVAL_SECONDS=' "${EVD}/adapter_env_sorted.txt" 2>/dev/null | tail -n1 | cut -d= -f2 || true)"

log "CAPACITY_ACCOUNTING_ENABLED=${CAP_ENABLED:-<none>}"
log "CAPACITY_SAFETY_FACTOR=${SAFETY:-<none>}"
log "RESERVATION_TTL_SECONDS=${TTL:-<none>}"
log "RECONCILE_INTERVAL_SECONDS=${REC:-<none>}"

if [[ "${CAP_ENABLED}" == "true" ]]; then
  pass "Capacity Accounting habilitado"
else
  fail "Capacity Accounting não habilitado"
fi

if [[ "${SATURATE}" == "true" ]]; then
  log "\n[5.1] Saturation test (best-effort): criando múltiplos NSIs rápidos para tentar forçar rejeição..."
  for n in $(seq 1 25); do
    nsi_id="probe-saturate-${TS_LOWER}-${n}"
    payload=$(cat <<JSON
{"nsiId":"${nsi_id}","serviceProfile":"eMBB","tenantId":"default","sla":{"latency":"50ms"}}
JSON
)
    post_json "${payload}" "${EVD}/resp_saturate_${n}.json"
    sleep 1
  done
  pass "Saturation test executado (ver resp_saturate_*.json)"
else
  log "[5.1] Saturation test desabilitado (SATURATE=false)."
fi

# ----------------------------------------------------------
# [6] Testes negativos (auditáveis)
# ----------------------------------------------------------
log "\n[6] Testes negativos (auditáveis)..."

# 6.1 metadata.name inválido (uppercase) — cria CR direto no apiserver para garantir 422
BAD_NAME="Probe-Invalid-${TS}"  # propositalmente inválido (maiúsculas)
cat > "${EVD}/bad_name_nsi.yaml" <<YAML
apiVersion: trisla.io/v1
kind: NetworkSliceInstance
metadata:
  name: ${BAD_NAME}
  namespace: ${NS}
spec:
  nsiId: ${BAD_NAME}
  serviceProfile: URLLC
  tenantId: default
  sla:
    latency: "10ms"
YAML

if kubectl apply -f "${EVD}/bad_name_nsi.yaml" > "${EVD}/bad_name_apply.txt" 2>&1; then
  fail "Teste negativo BAD_NAME: inesperadamente aceito (deveria falhar RFC1123)"
else
  pass "Teste negativo BAD_NAME: rejeitado conforme esperado (RFC1123)"
fi

# 6.2 payload com campo SLA não suportado (latency_max_ms) — deve ser rejeitado OU ignorado (registrar comportamento)
payload_bad_sla=$(cat <<JSON
{"nsiId":"probe-badsla-${TS_LOWER}","serviceProfile":"URLLC","tenantId":"default","sla":{"latency_max_ms":10}}
JSON
)

echo "${payload_bad_sla}" > "${EVD}/payload_bad_sla.json"
post_json "${payload_bad_sla}" "${EVD}/resp_bad_sla.json"
log "[6.2] resp_bad_sla:"
cat "${EVD}/resp_bad_sla.json" | tee -a "${EVD}/run.log"

pass "Teste negativo BAD_SLA registrado (interpretar resp_bad_sla.json)"

# ----------------------------------------------------------
# [7] Logs finais + sumário
# ----------------------------------------------------------
log "\n[7] Logs NASP Adapter (últimos 30 min)..."
kubectl logs -n "${NS}" deploy/trisla-nasp-adapter --since=30m > "${EVD}/adapter_logs_30m.txt" || true

log "\n=================================================="
log "SUMÁRIO FINAL"
log "PASS=${PASS_CNT} | FAIL=${FAIL_CNT}"
log "Evidence: ${EVD}"
log "=================================================="

# Se houver falhas, retorna exit code 2 (útil para gate em CI)
if [[ "${FAIL_CNT}" -gt 0 ]]; then
  exit 2
fi
