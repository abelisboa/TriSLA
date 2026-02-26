#!/usr/bin/env bash
set -euo pipefail

NS="trisla"
COLLECTOR_DEP="trisla-otel-collector"
ADAPTER_DEP="trisla-nasp-adapter"
SVC="trisla-otel-collector"
EVIDENCE_DIR="/home/porvir5g/gtp5g/trisla/evidencias_otel_hardening_$(date -u +%Y%m%dT%H%M%SZ)"

echo "=================================================="
echo "TriSLA — OpenTelemetry Hardening Final"
echo "Namespace : $NS"
echo "Evidence  : $EVIDENCE_DIR"
echo "=================================================="

mkdir -p "$EVIDENCE_DIR"

echo "1️⃣ Removendo variáveis OTLP_* customizadas..."
kubectl -n "$NS" set env deployment/"$ADAPTER_DEP" \
  OTLP_ENABLED- \
  OTLP_ENDPOINT- \
  OTLP_PROTOCOL- \
  OTLP_INSECURE-

echo "2️⃣ Padronizando apenas variáveis oficiais OpenTelemetry..."
kubectl -n "$NS" set env deployment/"$ADAPTER_DEP" \
  OTEL_EXPORTER_OTLP_ENDPOINT="$SVC:4317" \
  OTEL_EXPORTER_OTLP_INSECURE=true \
  OTEL_EXPORTER_OTLP_PROTOCOL=grpc

echo "3️⃣ Rollout do NASP Adapter..."
kubectl -n "$NS" rollout status deployment/"$ADAPTER_DEP"

echo "4️⃣ Criando NetworkPolicy restritiva (somente namespace trisla)..."

cat <<EOF | kubectl apply -n "$NS" -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: otel-collector-allow-trisla-only
spec:
  podSelector:
    matchLabels:
      app: $COLLECTOR_DEP
  policyTypes:
    - Ingress
  ingress:
    - from:
        - podSelector: {}
      ports:
        - protocol: TCP
          port: 4317
        - protocol: TCP
          port: 4318
EOF

echo "5️⃣ Validando Collector..."
kubectl -n "$NS" rollout status deployment/"$COLLECTOR_DEP"

echo "6️⃣ Gerando evidências finais..."
kubectl -n "$NS" get pods -o wide > "$EVIDENCE_DIR/pods.txt"
kubectl -n "$NS" get svc "$SVC" -o wide > "$EVIDENCE_DIR/service.txt"
kubectl -n "$NS" get endpoints "$SVC" -o wide > "$EVIDENCE_DIR/endpoints.txt"
kubectl -n "$NS" describe networkpolicy otel-collector-allow-trisla-only > "$EVIDENCE_DIR/networkpolicy.txt"
kubectl -n "$NS" logs deployment/"$COLLECTOR_DEP" --tail=200 > "$EVIDENCE_DIR/collector_logs.txt"
kubectl -n "$NS" logs deployment/"$ADAPTER_DEP" --tail=200 > "$EVIDENCE_DIR/adapter_logs.txt"

echo "=================================================="
echo "✅ Hardening concluído com sucesso."
echo "Evidências em: $EVIDENCE_DIR"
echo "=================================================="
