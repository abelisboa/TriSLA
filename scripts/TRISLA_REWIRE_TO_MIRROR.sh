#!/usr/bin/env bash
set -euo pipefail

# ==========================================
# TRISLA_REWIRE_TO_MIRROR
# - Reescreve values.yaml para usar mirror-*
# - Garante determinismo total
# ==========================================

NS="trisla"
VALUES="helm/trisla/values.yaml"
TS="$(date -u +%Y%m%dT%H%M%SZ)"

BACKUP="helm/trisla/values.yaml.backup.${TS}"

echo "=========================================="
echo "TRISLA REWIRE TO MIRROR"
echo "Timestamp: ${TS}"
echo "=========================================="

cp "${VALUES}" "${BACKUP}"
echo "Backup criado: ${BACKUP}"
echo

echo "Substituindo imagens oficiais por mirror-*"

sed -i 's|repository: trisla-|repository: mirror-ghcr-io-abelisboa-trisla-|g' "${VALUES}"
sed -i 's|hyperledger/besu:24.2.0|ghcr.io/abelisboa/mirror-hyperledger-besu:24.2.0|g' "${VALUES}"
sed -i 's|apache/kafka:3.6.1|ghcr.io/abelisboa/mirror-apache-kafka:3.6.1|g' "${VALUES}"
sed -i 's|curlimages/curl:8.6.0|ghcr.io/abelisboa/mirror-curlimages-curl:8.6.0|g' "${VALUES}"
sed -i 's|networkstatic/iperf3:3.16|ghcr.io/abelisboa/mirror-networkstatic-iperf3:3.16|g' "${VALUES}"
sed -i 's|python:3.11-slim|ghcr.io/abelisboa/mirror-python:3.11-slim|g' "${VALUES}"

echo
echo "Executando Helm upgrade determinístico..."

helm upgrade trisla helm/trisla -n "${NS}"

echo
echo "Aguardando rollout..."

kubectl rollout status deployment/trisla-besu -n "${NS}"
kubectl rollout status deployment/trisla-bc-nssmf -n "${NS}"
kubectl rollout status deployment/trisla-decision-engine -n "${NS}"
kubectl rollout status deployment/trisla-ml-nsmf -n "${NS}"
kubectl rollout status deployment/trisla-sem-csmf -n "${NS}"
kubectl rollout status deployment/trisla-nasp-adapter -n "${NS}"
kubectl rollout status deployment/trisla-sla-agent-layer -n "${NS}"

echo
echo "Verificação final de imagens em execução:"
kubectl get pods -n "${NS}" -o jsonpath='{range .items[*]}{.spec.containers[*].image}{"\n"}{end}' | sort -u

echo
echo "=========================================="
echo "SISTEMA 100% ESPELHADO EM GHCR"
echo "=========================================="
