#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# TRISLA AUTO FIX IMAGES
# Corrige automaticamente:
# - :latest
# - imagens sem tag
# - versões divergentes
# - registry incorreto
# ============================================================

NS="${NS:-trisla}"
EXPECTED_VERSION="${EXPECTED_VERSION:-v3.11.2}"
REGISTRY="${REGISTRY:-ghcr.io/abelisboa}"
VALUES_FILE="helm/trisla/values.yaml"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_DIR="./evidencias_autofix_${TS}"

mkdir -p "$OUT_DIR"

echo "======================================================"
echo "TRISLA AUTO FIX IMAGES"
echo "Namespace         : $NS"
echo "Expected Version  : $EXPECTED_VERSION"
echo "Registry          : $REGISTRY"
echo "Timestamp         : $TS"
echo "Output            : $OUT_DIR"
echo "======================================================"
echo

# ------------------------------------------------------------
# FASE 1 — Backup
# ------------------------------------------------------------

cp "$VALUES_FILE" "${VALUES_FILE}.backup.${TS}"
echo "Backup criado: ${VALUES_FILE}.backup.${TS}"
echo

# ------------------------------------------------------------
# FASE 2 — Correção determinística values.yaml
# ------------------------------------------------------------

echo "Corrigindo imagens externas determinísticas..."

# Kafka
sed -i 's|apache/kafka:latest|apache/kafka:3.6.1|g' "$VALUES_FILE"
sed -i 's|repository: apache/kafka|repository: apache/kafka|g' "$VALUES_FILE"
sed -i 's|tag: .*|tag: 3.6.1|g' "$VALUES_FILE" || true

# iperf3
sed -i 's|networkstatic/iperf3"|networkstatic/iperf3:3.16"|g' "$VALUES_FILE"
sed -i 's|networkstatic/iperf3$|networkstatic/iperf3:3.16|g' "$VALUES_FILE"

echo "Kafka e iperf3 fixados."
echo

# ------------------------------------------------------------
# FASE 3 — Uniformização TriSLA
# ------------------------------------------------------------

echo "Uniformizando microserviços TriSLA para $EXPECTED_VERSION..."

SERVICES=(
  sem-csmf
  ml-nsmf
  decision-engine
  bc-nssmf
  sla-agent-layer
  traffic-exporter
  ui-dashboard
  portal-backend
  portal-frontend
  nasp-adapter
)

for svc in "${SERVICES[@]}"; do
  sed -i "s|repository: .*trisla-${svc}|repository: trisla-${svc}|g" "$VALUES_FILE"
  sed -i "/trisla-${svc}/,/tag:/ s/tag:.*/tag: ${EXPECTED_VERSION}/" "$VALUES_FILE"
done

echo "Serviços atualizados."
echo

# ------------------------------------------------------------
# FASE 4 — Garantir Registry Global
# ------------------------------------------------------------

sed -i "s|imageRegistry: .*|imageRegistry: ${REGISTRY}|g" "$VALUES_FILE"

echo "Registry global garantido."
echo

# ------------------------------------------------------------
# FASE 5 — Helm Upgrade
# ------------------------------------------------------------

echo "Executando Helm upgrade..."
helm upgrade trisla helm/trisla -n "$NS" | tee "$OUT_DIR/helm_upgrade.log"

echo
echo "Aguardando rollout..."

kubectl rollout status deployment/trisla-besu -n "$NS" | tee -a "$OUT_DIR/rollout.log" || true
kubectl rollout status deployment/trisla-decision-engine -n "$NS" | tee -a "$OUT_DIR/rollout.log" || true

echo
echo "Coletando imagens finais..."

kubectl get deploy -n "$NS" -o yaml | grep image: > "$OUT_DIR/final_images.txt"

echo
echo "======================================================"
echo "AUTO FIX FINALIZADO"
echo "Verifique evidências em: $OUT_DIR"
echo "======================================================"
