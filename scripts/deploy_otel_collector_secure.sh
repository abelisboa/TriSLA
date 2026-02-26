#!/usr/bin/env bash
set -euo pipefail

NAMESPACE="trisla"
COLLECTOR_NAME="trisla-otel-collector"
CONFIGMAP_NAME="trisla-otel-config"
EVIDENCE_DIR="/home/porvir5g/gtp5g/trisla/evidencias_otel_$(date -u +%Y%m%dT%H%M%SZ)"

echo "=================================================="
echo "TriSLA — OpenTelemetry Collector Secure Deployment"
echo "Namespace : ${NAMESPACE}"
echo "Evidence  : ${EVIDENCE_DIR}"
echo "=================================================="

mkdir -p "${EVIDENCE_DIR}"

echo "🔎 Verificando namespace..."
kubectl get ns "${NAMESPACE}" >/dev/null

echo "🧹 Removendo instâncias anteriores (se existirem)..."
kubectl -n "${NAMESPACE}" delete deployment "${COLLECTOR_NAME}" --ignore-not-found
kubectl -n "${NAMESPACE}" delete service "${COLLECTOR_NAME}" --ignore-not-found
kubectl -n "${NAMESPACE}" delete configmap "${CONFIGMAP_NAME}" --ignore-not-found

echo "📦 Criando ConfigMap do Collector..."
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: ${CONFIGMAP_NAME}
  namespace: ${NAMESPACE}
data:
  otel-collector-config.yaml: |
    receivers:
      otlp:
        protocols:
          grpc:
          http:

    processors:
      batch:
      memory_limiter:
        check_interval: 1s
        limit_mib: 512
        spike_limit_mib: 128

    exporters:
      logging:
        loglevel: info

    service:
      pipelines:
        traces:
          receivers: [otlp]
          processors: [memory_limiter, batch]
          exporters: [logging]
EOF

echo "🚀 Criando Deployment do Collector..."
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ${COLLECTOR_NAME}
  namespace: ${NAMESPACE}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ${COLLECTOR_NAME}
  template:
    metadata:
      labels:
        app: ${COLLECTOR_NAME}
    spec:
      containers:
      - name: otel-collector
        image: otel/opentelemetry-collector:0.92.0
        args:
          - "--config=/etc/otel/otel-collector-config.yaml"
        ports:
        - containerPort: 4317
        - containerPort: 4318
        resources:
          requests:
            cpu: 200m
            memory: 256Mi
          limits:
            cpu: 1000m
            memory: 1Gi
        volumeMounts:
        - name: config
          mountPath: /etc/otel
        readinessProbe:
          tcpSocket:
            port: 4317
          initialDelaySeconds: 5
          periodSeconds: 5
        livenessProbe:
          tcpSocket:
            port: 4317
          initialDelaySeconds: 10
          periodSeconds: 10
      volumes:
      - name: config
        configMap:
          name: ${CONFIGMAP_NAME}
EOF

echo "🌐 Criando Service..."
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Service
metadata:
  name: ${COLLECTOR_NAME}
  namespace: ${NAMESPACE}
spec:
  selector:
    app: ${COLLECTOR_NAME}
  ports:
    - name: otlp-grpc
      port: 4317
      targetPort: 4317
    - name: otlp-http
      port: 4318
      targetPort: 4318
  type: ClusterIP
EOF

echo "⏳ Aguardando rollout..."
kubectl -n "${NAMESPACE}" rollout status deployment/${COLLECTOR_NAME}

echo "📊 Coletando evidências..."
kubectl -n "${NAMESPACE}" get pods -o wide > "${EVIDENCE_DIR}/pods.txt"
kubectl -n "${NAMESPACE}" get svc > "${EVIDENCE_DIR}/services.txt"
kubectl -n "${NAMESPACE}" describe deployment ${COLLECTOR_NAME} > "${EVIDENCE_DIR}/deployment.txt"
kubectl -n "${NAMESPACE}" logs deployment/${COLLECTOR_NAME} > "${EVIDENCE_DIR}/collector_logs.txt"

echo "🔎 Testando conectividade interna..."
kubectl -n "${NAMESPACE}" run otel-test --rm -it --image=busybox --restart=Never -- \
  sh -c "nc -zv ${COLLECTOR_NAME} 4317" || true

echo "=================================================="
echo "✅ OpenTelemetry Collector implantado com sucesso"
echo "Evidence disponível em:"
echo "${EVIDENCE_DIR}"
echo "=================================================="
