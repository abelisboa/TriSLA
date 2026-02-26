#!/bin/bash

NS="trisla"
RELEASE="trisla"
BASE_DIR="/home/porvir5g/gtp5g/trisla"
RUNBOOK="$BASE_DIR/TRISLA_MASTER_RUNBOOK.md"
OUTPUT_DIR="$BASE_DIR/AUDIT_$(date +%Y%m%d_%H%M%S)"

mkdir -p "$OUTPUT_DIR"

echo "================================================="
echo " TRI-SLA v3.11.2 — AUDITORIA COMPLETA NÃO-DESTRUTIVA"
echo "================================================="
echo "Output em: $OUTPUT_DIR"
echo ""

############################################
echo "[1] CLUSTER INFO"
############################################
kubectl version > "$OUTPUT_DIR/cluster_version.txt" 2>&1
kubectl cluster-info > "$OUTPUT_DIR/cluster_info.txt" 2>&1

############################################
echo "[2] NAMESPACE OVERVIEW"
############################################
kubectl get all -n $NS -o wide > "$OUTPUT_DIR/all_resources.txt" 2>&1
kubectl get events -n $NS --sort-by=.lastTimestamp > "$OUTPUT_DIR/events.txt" 2>&1

############################################
echo "[3] HELM STATUS"
############################################
helm status $RELEASE -n $NS > "$OUTPUT_DIR/helm_status.txt" 2>&1
helm get values $RELEASE -n $NS -a > "$OUTPUT_DIR/helm_values.txt" 2>&1
helm get manifest $RELEASE -n $NS > "$OUTPUT_DIR/helm_manifest.txt" 2>&1

############################################
echo "[4] DEPLOYMENTS & IMAGES"
############################################
kubectl get deployment -n $NS -o yaml > "$OUTPUT_DIR/deployments.yaml" 2>&1

############################################
echo "[5] PODS RAW + DESCRIBE"
############################################
kubectl get pods -n $NS -o yaml > "$OUTPUT_DIR/pods.yaml" 2>&1

for pod in $(kubectl get pods -n $NS -o jsonpath='{.items[*].metadata.name}' 2>/dev/null); do
    kubectl describe pod $pod -n $NS > "$OUTPUT_DIR/pod_describe_$pod.txt" 2>&1
done

############################################
echo "[6] REPLICASETS"
############################################
kubectl get rs -n $NS -o yaml > "$OUTPUT_DIR/replicasets.yaml" 2>&1

############################################
echo "[7] PVC"
############################################
kubectl get pvc -n $NS -o yaml > "$OUTPUT_DIR/pvcs.yaml" 2>&1

############################################
echo "[8] STORAGECLASS"
############################################
kubectl get storageclass -o yaml > "$OUTPUT_DIR/storageclasses.yaml" 2>&1

############################################
echo "[9] KAFKA FILTER"
############################################
kubectl get pods -n $NS | grep -i kafka > "$OUTPUT_DIR/kafka_pods.txt" 2>&1 || true

############################################
echo "[10] IMAGE IDs EM RUNTIME"
############################################
kubectl get pods -n $NS -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{range .status.containerStatuses[*]}  {.imageID}{"\n"}{end}{"\n"}{end}' \
> "$OUTPUT_DIR/runtime_image_ids.txt" 2>&1

############################################
echo "[11] RUNBOOK SNAPSHOT"
############################################
if [ -f "$RUNBOOK" ]; then
    cp "$RUNBOOK" "$OUTPUT_DIR/runbook_snapshot.md"
fi

############################################
echo "AUDITORIA FINALIZADA"
echo "Arquivos gerados em:"
echo "$OUTPUT_DIR"
echo "================================================="
