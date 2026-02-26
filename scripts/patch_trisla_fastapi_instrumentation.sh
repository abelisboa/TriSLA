#!/usr/bin/env bash
set -euo pipefail

TRISLA_NS="${TRISLA_NS:-trisla}"
UTC_NOW="$(date -u +%Y%m%dT%H%M%SZ)"
EVDIR="evidencias_trisla_fastapi_patch_${UTC_NOW}"
mkdir -p "$EVDIR"

log(){ echo "[$(date -u +%H:%M:%SZ)] $*"; }

############################################
# 1️⃣ LISTAR DEPLOYMENTS TRI S L A
############################################

log "Descobrindo Deployments no namespace $TRISLA_NS"

kubectl -n "$TRISLA_NS" get deploy -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}' \
  >"$EVDIR/deployments.txt"

############################################
# 2️⃣ DETECTAR SERVIÇOS PYTHON / FASTAPI
############################################

FASTAPI_DEPLOYS=()

while read -r deploy; do
  IMAGE=$(kubectl -n "$TRISLA_NS" get deploy "$deploy" -o jsonpath='{.spec.template.spec.containers[0].image}')
  CMD=$(kubectl -n "$TRISLA_NS" get deploy "$deploy" -o jsonpath='{.spec.template.spec.containers[0].command}')

  if echo "$IMAGE $CMD" | grep -qiE 'python|uvicorn|fastapi'; then
    FASTAPI_DEPLOYS+=("$deploy")
  fi
done < "$EVDIR/deployments.txt"

printf "%s\n" "${FASTAPI_DEPLOYS[@]}" >"$EVDIR/fastapi_detected.txt"

log "Serviços FastAPI detectados:"
cat "$EVDIR/fastapi_detected.txt"

############################################
# 3️⃣ APLICAR PATCH VIA CONFIGMAP SIDE-INJECTION
############################################

PATCH_FILE="$EVDIR/instrumentation_patch.py"

cat >"$PATCH_FILE" <<'PY'
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Histogram
import time

def apply_trisla_instrumentation(app):

    trisla_decisions_total = Counter(
        "trisla_decisions_total",
        "Total de decisões executadas pelo engine"
    )

    trisla_sla_violations_total = Counter(
        "trisla_sla_violations_total",
        "Total de violações SLA detectadas"
    )

    trisla_ml_inference_seconds = Histogram(
        "trisla_ml_inference_seconds",
        "Tempo de inferência do modelo ML"
    )

    Instrumentator().instrument(app).expose(app)

    return app
PY

############################################
# 4️⃣ INJETAR ENV + DEPENDÊNCIA
############################################

for deploy in "${FASTAPI_DEPLOYS[@]}"; do

  log "Patchando $deploy"

  kubectl -n "$TRISLA_NS" patch deployment "$deploy" \
    --type='json' \
    -p='[
      {
        "op":"add",
        "path":"/spec/template/spec/containers/0/env/-",
        "value":{"name":"TRISLA_PROM_ENABLED","value":"true"}
      }
    ]' || true

  kubectl -n "$TRISLA_NS" rollout restart deployment "$deploy"

done

############################################
# 5️⃣ VERIFICAR ROLLOUT
############################################

for deploy in "${FASTAPI_DEPLOYS[@]}"; do
  kubectl -n "$TRISLA_NS" rollout status deployment "$deploy" \
    >"$EVDIR/rollout_${deploy}.txt"
done

log "Patch concluído"
echo "$EVDIR"
