#!/usr/bin/env bash
set -euo pipefail

NS="${NS:-trisla}"
DEPLOY="${DEPLOY:?Informe DEPLOY=<deployment-name>}"

log(){ echo "[$(date -u +%H:%M:%S)] $*"; }

log "=========================================================="
log "FORCE CLEAN DEPLOYMENT: $DEPLOY"
log "Namespace: $NS"
log "=========================================================="

log "[1/4] Escalando para 0"
kubectl -n "$NS" scale deploy "$DEPLOY" --replicas=0

sleep 5

log "[2/4] Aguardando pods terminarem"
kubectl -n "$NS" wait --for=delete pod -l app="$DEPLOY" --timeout=60s || true

log "[3/4] Escalando para 1"
kubectl -n "$NS" scale deploy "$DEPLOY" --replicas=1

log "[4/4] Aguardando rollout"
kubectl -n "$NS" rollout status deploy/"$DEPLOY" --timeout=180s || true

log "=========================================================="
log "DEPLOYMENT $DEPLOY REINICIALIZADO"
log "=========================================================="
