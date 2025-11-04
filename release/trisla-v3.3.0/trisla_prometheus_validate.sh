#!/bin/bash
# ============================================================
# TriSLA Prometheus Validation Script (v1.0)
# Autor: Abel Lisboa
# Local: NASP (node1)
# Objetivo:
#   Validar a integração Prometheus <-> TriSLA API v3.2
#   Confirmar imagem, endpoint /metrics e status no cluster.
# ============================================================

NS_TRISLA="trisla"
NS_MONITORING="monitoring"
PROM_POD=$(kubectl get pods -n $NS_MONITORING -o name | grep prometheus-prometheus-kube-prometheus-prometheus-0)
TRISLA_POD=$(kubectl get pods -n $NS_TRISLA -o name | grep trisla-portal)

echo "============================================================"
echo "🔍 INICIANDO VALIDAÇÃO PROMETHEUS <-> TRI-SLA API"
echo "============================================================"
echo ""

LOG_FILE="/tmp/trisla_prometheus_report.txt"
exec > >(tee -a "$LOG_FILE") 2>&1
echo "📁 Log sendo gravado em: $LOG_FILE"
echo ""

# 1️⃣ Verificar imagem em uso no pod TriSLA
echo "📦 [1/4] Verificando imagem do backend TriSLA API..."
kubectl describe $TRISLA_POD -n $NS_TRISLA | grep "Image:" | grep trisla-api
echo "------------------------------------------------------------"
sleep 1

# 2️⃣ Testar endpoint /metrics via Prometheus pod
echo "🌐 [2/4] Testando endpoint /metrics via DNS interno..."
kubectl exec -it -n $NS_MONITORING $PROM_POD -- sh -c \
  "busybox wget -qO- http://trisla-api-observability.trisla.svc.cluster.local:8000/metrics | head" \
  || echo "❌ Falha ao acessar /metrics"
echo "------------------------------------------------------------"
sleep 1

# 3️⃣ Validar status dos targets Prometheus
echo "📊 [3/4] Verificando status dos targets no Prometheus..."
kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090 >/dev/null 2>&1 &
PID=$!
sleep 4
curl -s http://localhost:9090/api/v1/targets | grep -E '"trisla|trisla-api"' | head -20
kill $PID >/dev/null 2>&1
echo "------------------------------------------------------------"
sleep 1

# 4️⃣ Exibir resumo final
echo "🧾 [4/4] RESUMO FINAL"
echo "------------------------------------------------------------"
echo "✅ Cluster Namespace:        $NS_TRISLA"
echo "✅ Prometheus Namespace:     $NS_MONITORING"
echo "✅ Pod TriSLA:               $TRISLA_POD"
echo "✅ Pod Prometheus:           $PROM_POD"
echo ""
echo "Se /metrics retornou dados e o target estiver UP, integração OK."
echo "============================================================"
