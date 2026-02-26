#!/usr/bin/env bash
set -euo pipefail

NS="${NS:-trisla}"
ROOT="/home/porvir5g/gtp5g/trisla"
TS="$(date +%Y%m%d-%H%M%S)"
EVID_DIR="${ROOT}/evidencias_gates/${TS}-preflight"

mkdir -p "${EVID_DIR}"

echo "=============================================="
echo "TriSLA GLOBAL PREFLIGHT – STRICT VALIDATION"
echo "Namespace: ${NS}"
echo "Evidence: ${EVID_DIR}"
echo "=============================================="

log() { echo -e "$*"; }
save() { cat | tee -a "${EVID_DIR}/preflight.log" >/dev/null; }

FAIL=0

log "🔎 1️⃣ Verificando namespace..."
if ! kubectl get ns "${NS}" >/dev/null 2>&1; then
  log "❌ FAIL: Namespace ${NS} não existe"
  exit 1
fi
log "✅ Namespace OK"

# Deployments críticos oficiais (ajuste somente se o runbook/helm definir outros)
CRITICAL_DEPLOYS=(
  "trisla-sem-csmf"
  "trisla-ml-nsmf"
  "trisla-decision-engine"
  "trisla-bc-nssmf"
  "trisla-nasp-adapter"
  "trisla-sla-agent-layer"
  "trisla-portal-backend"
  "trisla-portal-frontend"
)

log "🔎 2️⃣ Snapshot de pods (para evidência)..."
kubectl get pods -n "${NS}" -o wide | save

log "🔎 3️⃣ Detectando estados críticos (ImagePull/CrashLoop) em pods críticos..."
# pega pods apenas dos apps críticos (por prefixo), evitando completed antigos
for d in "${CRITICAL_DEPLOYS[@]}"; do
  # selecionar pods por prefixo do nome do deployment
  pods="$(kubectl get pods -n "${NS}" --no-headers 2>/dev/null | awk '{print $1}' | grep -E "^${d}-" || true)"
  if [[ -z "${pods}" ]]; then
    log "⚠️ WARN: Nenhum pod encontrado com prefixo ${d}- (pode ser normal se componente não estiver instalado)"
    continue
  fi

  while read -r p; do
    [[ -z "${p}" ]] && continue
    st="$(kubectl get pod -n "${NS}" "${p}" -o jsonpath='{.status.phase}' 2>/dev/null || true)"
    reason="$(kubectl get pod -n "${NS}" "${p}" -o jsonpath='{.status.containerStatuses[0].state.waiting.reason}' 2>/dev/null || true)"
    ready="$(kubectl get pod -n "${NS}" "${p}" -o jsonpath='{.status.containerStatuses[0].ready}' 2>/dev/null || true)"

    if [[ "${reason}" =~ ^(ImagePullBackOff|ErrImagePull|CrashLoopBackOff)$ ]]; then
      log "❌ FAIL: Pod ${p} em ${reason} (ready=${ready})"
      kubectl describe pod -n "${NS}" "${p}" | save
      FAIL=1
    fi
  done <<< "${pods}"
done

log "🔎 4️⃣ Validando deployments críticos (Ready >= 1 e sem stuck rollout irrelevante)..."
for d in "${CRITICAL_DEPLOYS[@]}"; do
  if ! kubectl get deploy -n "${NS}" "${d}" >/dev/null 2>&1; then
    log "⚠️ WARN: Deployment ${d} não existe no namespace ${NS}"
    continue
  fi

  log "➡️ Verificando ${d}"

  # condição: pelo menos 1 ready replica
  readyRep="$(kubectl get deploy -n "${NS}" "${d}" -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo "")"
  readyRep="${readyRep:-0}"

  # condição: progressing reason
  progReason="$(kubectl get deploy -n "${NS}" "${d}" -o jsonpath='{range .status.conditions[?(@.type=="Progressing")]}{.reason}{"\n"}{end}' 2>/dev/null | head -n1 || true)"

  # Se não existe nenhuma réplica ready -> FAIL
  if [[ "${readyRep}" == "0" ]]; then
    log "❌ FAIL: Deployment ${d} sem réplicas READY"
    kubectl describe deploy -n "${NS}" "${d}" | save
    FAIL=1
    continue
  fi

  # Se ProgressDeadlineExceeded, só falhar se também houver pod em ImagePull/CrashLoop (já detectado no gate 3)
  if [[ "${progReason}" == "ProgressDeadlineExceeded" ]]; then
    log "⚠️ WARN: ${d} com ProgressDeadlineExceeded, porém readyReplicas=${readyRep}. (Verificar se há rollout travado)"
    kubectl describe deploy -n "${NS}" "${d}" | save
    continue
  fi

  # tentativa de rollout status com timeout curto (não travar preflight)
  if ! kubectl rollout status deploy "${d}" -n "${NS}" --timeout=20s >/dev/null 2>&1; then
    log "⚠️ WARN: rollout status não concluiu em 20s para ${d} (não necessariamente erro)"
    kubectl describe deploy -n "${NS}" "${d}" | save
  else
    log "✅ ${d} OK (readyReplicas=${readyRep})"
  fi
done

if [[ "${FAIL}" == "1" ]]; then
  log "=============================================="
  log "❌ PREFLIGHT FAILED"
  log "Ver evidências em: ${EVID_DIR}"
  log "=============================================="
  exit 1
fi

log "=============================================="
log "✅ PREFLIGHT PASSED"
log "Evidências em: ${EVID_DIR}"
log "=============================================="
