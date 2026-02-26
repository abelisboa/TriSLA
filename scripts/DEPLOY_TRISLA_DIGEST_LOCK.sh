#!/usr/bin/env bash
set -euo pipefail

NS="${NS:-trisla}"
RELEASE="${RELEASE:-trisla}"
CHART_DIR="${CHART_DIR:-./helm/trisla}"

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
EVID_DIR="./evidencias_deploy_digest/${STAMP}"

log() { echo "[$(date -u +%H:%M:%S)] $*"; }
fail() { echo "ERROR: $*" >&2; exit 1; }

need() { command -v "$1" >/dev/null 2>&1 || fail "comando ausente: $1"; }

need helm
need kubectl
need mkdir

mkdir -p "$EVID_DIR"

log "=========================================================="
log "DEPLOY TRISLA — DIGEST LOCK MODE"
log "Namespace: $NS"
log "=========================================================="

log "[1/5] helm upgrade"
helm upgrade --install "$RELEASE" "$CHART_DIR" -n "$NS" --create-namespace \
  | tee "$EVID_DIR/helm_upgrade.log"

log "[2/5] aguardando rollout"
kubectl rollout status deploy -n "$NS" --timeout=180s | tee "$EVID_DIR/rollout.log"

log "[3/5] capturando pods"
kubectl get pods -n "$NS" -o wide | tee "$EVID_DIR/pods.log"

log "[4/5] validando imagens ativas"
kubectl get pods -n "$NS" -o jsonpath='{..image}' | tr -s '[[:space:]]' '\n' \
  | tee "$EVID_DIR/images_running.txt"

if grep -q ':v' "$EVID_DIR/images_running.txt"; then
  fail "Ainda existem imagens com TAG ativa!"
fi

log "[5/5] status final"
kubectl get all -n "$NS" | tee "$EVID_DIR/cluster_state.log"

log "=========================================================="
log "DEPLOY CONCLUÍDO COM SUCESSO"
log "Evidências: $EVID_DIR"
log "=========================================================="
