#!/bin/bash
# ============================================================
# TriSLA + Prometheus Diagnostic Script
# Autor: Abel Lisboa / Assistente GPT-5
# Data: $(date +%F)
# ============================================================
# Objetivo:
#   Diagnosticar problemas de "targets DOWN" no Prometheus,
#   verificando DNS, serviços, pods, portas e configurações.
# ============================================================

NAMESPACE_MON="monitoring"
NAMESPACE_TRISLA="trisla"
PROM_PORT=9090
TMP_REPORT="/tmp/trisla_prometheus_report.txt"
PROM_CM_NAME="prometheus-kube-prometheus-prometheus"

echo "============================================================"
echo "🔍 INICIANDO DIAGNÓSTICO TRI-SLA + PROMETHEUS"
echo "============================================================"
echo "" > $TMP_REPORT

# ------------------------------------------------------------
# 1. Verificar se porta 9090 já está em uso
# ------------------------------------------------------------
echo "📡 [1/8] Verificando porta local 9090..."
if sudo lsof -i :$PROM_PORT &>/dev/null; then
    echo "⚠️ Porta 9090 em uso. Processo(s):" | tee -a $TMP_REPORT
    sudo lsof -i :$PROM_PORT | tee -a $TMP_REPORT
else
    echo "✅ Porta 9090 livre." | tee -a $TMP_REPORT
fi

# ------------------------------------------------------------
# 2. Verificar pods do Prometheus
# ------------------------------------------------------------
echo ""
echo "📦 [2/8] Verificando pods Prometheus..."
kubectl get pods -n $NAMESPACE_MON -o wide | grep prometheus | tee -a $TMP_REPORT

# ------------------------------------------------------------
# 3. Verificar serviços Prometheus e TriSLA
# ------------------------------------------------------------
echo ""
echo "🌐 [3/8] Verificando serviços..."
echo "-> Serviços em '$NAMESPACE_MON':" | tee -a $TMP_REPORT
kubectl get svc -n $NAMESPACE_MON | tee -a $TMP_REPORT
echo "" | tee -a $TMP_REPORT
echo "-> Serviços em '$NAMESPACE_TRISLA':" | tee -a $TMP_REPORT
kubectl get svc -n $NAMESPACE_TRISLA | tee -a $TMP_REPORT

# ------------------------------------------------------------
# 4. Verificar resolução DNS dentro do pod Prometheus
# ------------------------------------------------------------
PROM_POD=$(kubectl get pods -n $NAMESPACE_MON -l app.kubernetes.io/name=prometheus -o jsonpath='{.items[0].metadata.name}')
if [ -n "$PROM_POD" ]; then
    echo ""
    echo "🔎 [4/8] Testando resolução DNS interna..."
    for host in hibrido-prometheus.monitoring.svc.cluster.local trisla-api.trisla.svc.cluster.local; do
        echo "→ Testando $host ..." | tee -a $TMP_REPORT
        kubectl exec -n $NAMESPACE_MON $PROM_POD -- nslookup $host 2>&1 | tee -a $TMP_REPORT
        echo "" | tee -a $TMP_REPORT
    done
else
    echo "⚠️ Nenhum pod Prometheus encontrado!" | tee -a $TMP_REPORT
fi

# ------------------------------------------------------------
# 5. Verificar ConfigMap do Prometheus
# ------------------------------------------------------------
echo ""
echo "🧾 [5/8] Verificando ConfigMap Prometheus..."
kubectl -n $NAMESPACE_MON get configmap $PROM_CM_NAME -o yaml | grep -E "job_name|targets" | tee -a $TMP_REPORT

# ------------------------------------------------------------
# 6. Verificar estado do CoreDNS
# ------------------------------------------------------------
echo ""
echo "🧠 [6/8] Verificando pods CoreDNS..."
kubectl get pods -n kube-system | grep coredns | tee -a $TMP_REPORT

# ------------------------------------------------------------
# 7. Verificar pods TriSLA (API, Portal, Métricas)
# ------------------------------------------------------------
echo ""
echo "⚙️ [7/8] Verificando pods TriSLA..."
kubectl get pods -n $NAMESPACE_TRISLA -o wide | tee -a $TMP_REPORT

# ------------------------------------------------------------
# 8. Resumo final
# ------------------------------------------------------------
echo ""
echo "📊 [8/8] Resumo final gerado em: $TMP_REPORT"
echo "============================================================"
echo "Para reiniciar CoreDNS (se necessário):"
echo "kubectl rollout restart -n kube-system deployment coredns"
echo ""
echo "Para reiniciar Prometheus:"
echo "kubectl rollout restart -n $NAMESPACE_MON deployment prometheus-kube-prometheus-prometheus"
echo ""
echo "Para liberar porta 9090 local:"
echo "sudo kill -9 \$(sudo lsof -t -i :9090)"
echo "============================================================"
