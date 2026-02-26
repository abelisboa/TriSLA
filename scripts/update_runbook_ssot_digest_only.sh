#!/usr/bin/env bash
set -euo pipefail

############################################
# TriSLA — SSOT Runbook Update (Digest-Only)
# Governança obrigatória de Deploy / Rollback
############################################

ROOT="/home/porvir5g/gtp5g/trisla"
RUNBOOK="$ROOT/TRISLA_MASTER_RUNBOOK.md"

if [ ! -f "$RUNBOOK" ]; then
  echo "FATAL: TRISLA_MASTER_RUNBOOK.md não encontrado."
  exit 1
fi

if [ $# -lt 3 ]; then
  echo "Uso:"
  echo "  $0 <service> <digest> <motivo> [STATUS]"
  echo ""
  echo "Exemplo:"
  echo "  $0 kafka sha256:8291bed273105a3fc88df5f89096abf6a654dc92b0937245dcef85011f3fc5e6 \"Rollback ImagePullBackOff\" PASS"
  exit 1
fi

SERVICE="$1"
DIGEST="$2"
MOTIVO="$3"
STATUS="${4:-PASS}"

TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

############################################
# Validação obrigatória — Digest-only
############################################

if [[ "$DIGEST" != sha256:* ]]; then
  echo "FATAL: Digest inválido. Deve iniciar com sha256:"
  exit 1
fi

############################################
# Validar estado atual do deployment
############################################

echo "[INFO] Validando deployment atual..."

DEPLOY_IMAGE=$(kubectl -n trisla get deploy "$SERVICE" -o jsonpath='{.spec.template.spec.containers[0].image}')

if [[ "$DEPLOY_IMAGE" != *"$DIGEST"* ]]; then
  echo "FATAL: Digest informado não corresponde à imagem atualmente implantada."
  echo "Imagem atual: $DEPLOY_IMAGE"
  exit 1
fi

echo "[OK] Digest corresponde ao deployment atual."

############################################
# Validar rollout estável
############################################

echo "[INFO] Verificando estado do rollout..."

ROLL_STATUS=$(kubectl -n trisla rollout status deployment/"$SERVICE" --timeout=60s 2>&1 || true)

if [[ "$ROLL_STATUS" != *"successfully rolled out"* ]]; then
  echo "FATAL: Rollout não está estável."
  echo "$ROLL_STATUS"
  exit 1
fi

echo "[OK] Rollout estável."

############################################
# Gerar evidência de imagem atual
############################################

EVID_DIR="$ROOT/evidencias_runbook_update_$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$EVID_DIR"

kubectl -n trisla get deploy "$SERVICE" -o yaml > "$EVID_DIR/deploy_${SERVICE}.yaml"
kubectl -n trisla get pods -l app="$SERVICE" -o wide > "$EVID_DIR/pods_${SERVICE}.txt"
kubectl -n trisla get rs -l app="$SERVICE" -o wide > "$EVID_DIR/rs_${SERVICE}.txt"

echo "$DIGEST" > "$EVID_DIR/digest_${SERVICE}.txt"

############################################
# Atualização do Runbook (SSOT)
############################################

echo "[INFO] Atualizando Runbook SSOT..."

cat >> "$RUNBOOK" <<EOF

## [$TS] - DEPLOY $SERVICE

Imagem: ghcr.io/abelisboa/$SERVICE@$DIGEST
Motivo: $MOTIVO
Validação Pull: OK
Rollout: OK
Status: $STATUS
Evidências: $(basename "$EVID_DIR")

EOF

echo "[OK] Runbook atualizado com sucesso."
echo "[OK] Evidências salvas em: $EVID_DIR"
echo "Status final: $STATUS"
