#!/usr/bin/env bash
set -euo pipefail

NS="trisla"
TEMPO_DEP="trisla-tempo"
TEMPO_SVC="trisla-tempo"
COLLECTOR_CM="trisla-otel-config"
EVIDENCE_DIR="/home/porvir5g/gtp5g/trisla/evidencias_tempo_$(date -u +%Y%m%dT%H%M%SZ)"

echo "=================================================="
echo "TriSLA — Deploy Grafana Tempo + Collector Integration"
echo "Namespace : $NS"
echo "Evidence  : $EVIDENCE_DIR"
echo "=================================================="

mkdir -p "$EVIDENCE_DIR"

echo "1️⃣ Deploying Grafana Tempo..."

cat <<EOF | kubectl apply -n "$NS" -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: $TEMPO_DEP
spec:
  replicas: 1
  selector:
    matchLabels:
      app: $TEMPO_DEP
  template:
    metadata:
      labels:
        app: $TEMPO_DEP
    spec:
      containers:
        - name: tempo
          image: grafana/tempo:2.4.1
          args:
            - "-config.file=/etc/tempo.yaml"
          ports:
            - containerPort: 3200
            - containerPort: 4317
          volumeMounts:
            - name: config
              mountPath: /etc/tempo.yaml
              subPath: tempo.yaml
      volumes:
        - name: config
          configMap:
            name: $TEMPO_DEP-config
---
apiVersion: v1
kind: Service
metadata:
  name: $TEMPO_SVC
spec:
  type: ClusterIP
  selector:
    app: $TEMPO_DEP
  ports:
    - name: http
      port: 3200
      targetPort: 3200
    - name: otlp
      port: 4317
      targetPort: 4317
EOF

echo "2️⃣ Criando ConfigMap do Tempo..."

cat <<EOF | kubectl apply -n "$NS" -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: $TEMPO_DEP-config
data:
  tempo.yaml: |
    server:
      http_listen_port: 3200

    distributor:
      receivers:
        otlp:
          protocols:
            grpc:

    ingester:
      trace_idle_period: 10s
      max_block_bytes: 1048576
      max_block_duration: 5m

    compactor:
      compaction:
        block_retention: 1h

    storage:
      trace:
        backend: local
        local:
          path: /tmp/tempo
EOF

echo "3️⃣ Aguardando rollout do Tempo..."
kubectl -n "$NS" rollout status deployment/$TEMPO_DEP

echo "4️⃣ Atualizando Collector para exportar para Tempo..."

kubectl -n "$NS" get configmap $COLLECTOR_CM -o yaml > "$EVIDENCE_DIR/collector_before.yaml"

kubectl -n "$NS" patch configmap $COLLECTOR_CM --type merge -p '
data:
  otel-collector-config.yaml: |
    receivers:
      otlp:
        protocols:
          grpc:

    processors:
      memory_limiter:
        check_interval: 1s
        limit_mib: 512
        spike_limit_mib: 128

      batch:

    exporters:
      otlp/tempo:
        endpoint: trisla-tempo:4317
        tls:
          insecure: true

    service:
      pipelines:
        traces:
          receivers: [otlp]
          processors: [memory_limiter, batch]
          exporters: [otlp/tempo]
'

echo "5️⃣ Reiniciando Collector..."
kubectl -n "$NS" rollout restart deployment/trisla-otel-collector
kubectl -n "$NS" rollout status deployment/trisla-otel-collector

echo "6️⃣ Evidências..."
kubectl -n "$NS" get pods -o wide > "$EVIDENCE_DIR/pods.txt"
kubectl -n "$NS" get svc -o wide > "$EVIDENCE_DIR/services.txt"
kubectl -n "$NS" logs deployment/$TEMPO_DEP --tail=200 > "$EVIDENCE_DIR/tempo_logs.txt"
kubectl -n "$NS" logs deployment/trisla-otel-collector --tail=200 > "$EVIDENCE_DIR/collector_logs.txt"

echo "=================================================="
echo "✅ Tempo implantado e integrado ao Collector."
echo "Evidências em: $EVIDENCE_DIR"
echo "=================================================="
