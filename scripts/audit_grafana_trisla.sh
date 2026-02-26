#!/bin/bash
set -e

NAMESPACE_MONITORING="monitoring"
NAMESPACE_TRISLA="trisla"
EVIDENCE_DIR="evidencias_grafana_audit_$(date -u +%Y%m%dT%H%M%SZ)"

mkdir -p $EVIDENCE_DIR

echo "==============================================="
echo "TriSLA — Auditoria do Grafana Atual"
echo "Evidence: $EVIDENCE_DIR"
echo "==============================================="

echo "1️⃣ Verificando pods Grafana..."
kubectl get pods -n $NAMESPACE_MONITORING | grep grafana | tee $EVIDENCE_DIR/pods.txt

echo "2️⃣ Verificando serviços Grafana..."
kubectl get svc -n $NAMESPACE_MONITORING | grep grafana | tee $EVIDENCE_DIR/services.txt

echo "3️⃣ Exportando ConfigMaps Grafana..."
kubectl get configmap -n $NAMESPACE_MONITORING | grep grafana | tee $EVIDENCE_DIR/configmaps.txt

echo "4️⃣ Listando dashboards provisionados..."
kubectl get configmap -n $NAMESPACE_MONITORING -o yaml | grep -i dashboard | tee $EVIDENCE_DIR/dashboards_detected.txt

echo "5️⃣ Verificando datasource Tempo..."
kubectl get configmap -n $NAMESPACE_MONITORING -o yaml | grep -i tempo | tee $EVIDENCE_DIR/tempo_references.txt

echo "==============================================="
echo "✅ Auditoria concluída"
echo "==============================================="
