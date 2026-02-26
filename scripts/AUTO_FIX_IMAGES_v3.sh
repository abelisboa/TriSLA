#!/usr/bin/env bash
set -euo pipefail

NS="${NS:-trisla}"
EXPECTED_VERSION="${EXPECTED_VERSION:-v3.11.2}"
REGISTRY="${REGISTRY:-ghcr.io/abelisboa}"
BESU_VERSION="${BESU_VERSION:-v3.11.0}"
NASP_VERSION="${NASP_VERSION:-v3.9.28}"

VALUES_FILE="helm/trisla/values.yaml"
CHART_DIR="helm/trisla"

TS="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_DIR="./evidencias_autofix_${TS}"

mkdir -p "$OUT_DIR"

echo "======================================================"
echo "TRISLA AUTO FIX IMAGES v3 (YAML SAFE)"
echo "Namespace         : $NS"
echo "Expected Version  : $EXPECTED_VERSION"
echo "Besu Version      : $BESU_VERSION"
echo "NASP Version      : $NASP_VERSION"
echo "Registry          : $REGISTRY"
echo "Timestamp         : $TS"
echo "======================================================"
echo

if ! command -v yq >/dev/null 2>&1; then
  echo "ERRO: yq não instalado."
  exit 2
fi

cp "$VALUES_FILE" "$VALUES_FILE.backup.$TS"
echo "Backup criado."
echo

echo "FASE 1 — Fixando dependências externas"
yq -i '.kafka.image.repository = "apache/kafka"' "$VALUES_FILE"
yq -i '.kafka.image.tag = "3.6.1"' "$VALUES_FILE"

echo "FASE 2 — Uniformizando serviços TriSLA"

SERVICES=(
  semCsmf
  mlNsmf
  decisionEngine
  bcNssmf
  slaAgentLayer
  trafficExporter
  uiDashboard
)

for svc in "${SERVICES[@]}"; do
  yq -i ".${svc}.image.repository = \"trisla-${svc//[A-Z]/-\L&}\"" "$VALUES_FILE"
  yq -i ".${svc}.image.tag = \"$EXPECTED_VERSION\"" "$VALUES_FILE"
done

echo "FASE 3 — Exceções controladas"

# BESU
yq -i '.besu.image.repository = "trisla-besu"' "$VALUES_FILE"
yq -i ".besu.image.tag = \"$BESU_VERSION\"" "$VALUES_FILE"

# NASP
yq -i '.naspAdapter.image.repository = "trisla-nasp-adapter"' "$VALUES_FILE"
yq -i ".naspAdapter.image.tag = \"$NASP_VERSION\"" "$VALUES_FILE"

echo "FASE 4 — Garantindo registry global"
yq -i ".global.imageRegistry = \"$REGISTRY\"" "$VALUES_FILE"

echo
echo "FASE 5 — Render de validação"
helm template trisla "$CHART_DIR" -n "$NS" -f "$VALUES_FILE" > "$OUT_DIR/render.yaml"

if grep -q ':latest' "$OUT_DIR/render.yaml"; then
  echo "ERRO: :latest detectado no render."
  exit 10
fi

echo "OK: render limpo."
echo

echo "FASE 6 — Helm upgrade"
helm upgrade trisla "$CHART_DIR" -n "$NS" -f "$VALUES_FILE"

echo
echo "FASE 7 — Rollout"
kubectl rollout status deploy/trisla-decision-engine -n "$NS" || true
kubectl rollout status deploy/trisla-besu -n "$NS" || true

echo
echo "FASE 8 — Evidências finais"
kubectl get deploy -n "$NS" -o wide > "$OUT_DIR/deploys.txt"
kubectl get pods -n "$NS" -o wide > "$OUT_DIR/pods.txt"

echo
echo "======================================================"
echo "AUTO FIX v3 FINALIZADO"
echo "Evidências: $OUT_DIR"
echo "======================================================"
