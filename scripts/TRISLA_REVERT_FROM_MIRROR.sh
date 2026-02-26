#!/usr/bin/env bash
set -euo pipefail

TS=$(date -u +%Y%m%dT%H%M%SZ)

echo "=========================================="
echo "TRISLA REVERT FROM MIRROR"
echo "Timestamp: $TS"
echo "=========================================="

VALUES_FILE="helm/trisla/values.yaml"

cp $VALUES_FILE ${VALUES_FILE}.backup.$TS

echo "Substituindo mirror-* por imagens oficiais..."

sed -i 's|ghcr.io/abelisboa/mirror-ghcr-io-abelisboa-trisla-bc-nssmf|ghcr.io/abelisboa/trisla-bc-nssmf|g' $VALUES_FILE
sed -i 's|ghcr.io/abelisboa/mirror-ghcr-io-abelisboa-trisla-besu|ghcr.io/abelisboa/trisla-besu|g' $VALUES_FILE
sed -i 's|ghcr.io/abelisboa/mirror-ghcr-io-abelisboa-trisla-decision-engine|ghcr.io/abelisboa/trisla-decision-engine|g' $VALUES_FILE
sed -i 's|ghcr.io/abelisboa/mirror-ghcr-io-abelisboa-trisla-ml-nsmf|ghcr.io/abelisboa/trisla-ml-nsmf|g' $VALUES_FILE
sed -i 's|ghcr.io/abelisboa/mirror-ghcr-io-abelisboa-trisla-nasp-adapter|ghcr.io/abelisboa/trisla-nasp-adapter|g' $VALUES_FILE
sed -i 's|ghcr.io/abelisboa/mirror-ghcr-io-abelisboa-trisla-sem-csmf|ghcr.io/abelisboa/trisla-sem-csmf|g' $VALUES_FILE
sed -i 's|ghcr.io/abelisboa/mirror-ghcr-io-abelisboa-trisla-sla-agent-layer|ghcr.io/abelisboa/trisla-sla-agent-layer|g' $VALUES_FILE
sed -i 's|ghcr.io/abelisboa/mirror-ghcr-io-abelisboa-trisla-traffic-exporter|ghcr.io/abelisboa/trisla-traffic-exporter|g' $VALUES_FILE
sed -i 's|ghcr.io/abelisboa/mirror-ghcr-io-abelisboa-trisla-ui-dashboard|ghcr.io/abelisboa/trisla-ui-dashboard|g' $VALUES_FILE

echo "Fixando imagens externas determinísticas..."

sed -i 's|apache/kafka:latest|apache/kafka:3.6.1|g' $VALUES_FILE
sed -i 's|networkstatic/iperf3|networkstatic/iperf3:3.16|g' $VALUES_FILE

echo "Executando Helm upgrade..."

helm upgrade trisla helm/trisla -n trisla

echo "Aguardando rollout..."

kubectl rollout status deployment/trisla-besu -n trisla
kubectl rollout status deployment/trisla-decision-engine -n trisla
kubectl rollout status deployment/trisla-ml-nsmf -n trisla
kubectl rollout status deployment/trisla-sem-csmf -n trisla
kubectl rollout status deployment/trisla-bc-nssmf -n trisla
kubectl rollout status deployment/trisla-sla-agent-layer -n trisla
kubectl rollout status deployment/trisla-traffic-exporter -n trisla
kubectl rollout status deployment/trisla-ui-dashboard -n trisla

echo "=========================================="
echo "REVERT FINALIZADO"
echo "=========================================="
