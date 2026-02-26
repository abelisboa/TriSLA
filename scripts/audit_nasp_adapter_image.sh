#!/usr/bin/env bash
set -euo pipefail

NS="${1:-trisla}"
BASE="/home/porvir5g/gtp5g/trisla"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="${BASE}/evidencias_hardening/nasp_adapter_image_audit_${TS}"

mkdir -p "${OUT}"

echo "==============================================="
echo "TriSLA — NASP Adapter Image Audit (Determinístico)"
echo "Namespace : ${NS}"
echo "Output    : ${OUT}"
echo "==============================================="

echo "1️⃣ Deployment YAML..."
kubectl get deploy -n ${NS} trisla-nasp-adapter -o yaml > ${OUT}/deployment.yaml

echo "2️⃣ Imagem declarada no Deployment..."
IMAGE_DECLARED=$(kubectl get deploy -n ${NS} trisla-nasp-adapter \
  -o jsonpath='{.spec.template.spec.containers[0].image}')
echo "${IMAGE_DECLARED}" | tee ${OUT}/image_declared.txt

echo "3️⃣ Descobrindo Pod real via label app=trisla-nasp-adapter..."
POD=$(kubectl get pods -n ${NS} -l app=trisla-nasp-adapter \
  -o jsonpath='{.items[0].metadata.name}')

if [ -z "${POD}" ]; then
  echo "❌ Nenhum pod encontrado!"
  kubectl get pods -n ${NS} --show-labels | tee ${OUT}/pods_list.txt
  exit 1
fi

echo "Pod encontrado: ${POD}" | tee ${OUT}/pod_name.txt

echo "4️⃣ Digest real da imagem em execução..."
kubectl get pod -n ${NS} ${POD} \
  -o jsonpath='{.status.containerStatuses[0].imageID}' \
  | tee ${OUT}/running_image_id.txt

echo "5️⃣ Logs recentes..."
kubectl logs -n ${NS} ${POD} --since=10m \
  > ${OUT}/logs_10m.txt || true

echo "6️⃣ Health check..."
kubectl port-forward -n ${NS} deploy/trisla-nasp-adapter 18085:8085 >/dev/null 2>&1 &
PF=$!
sleep 2
curl -s http://127.0.0.1:18085/health | tee ${OUT}/health.json
kill ${PF} 2>/dev/null || true

echo "==============================================="
echo "AUDIT COMPLETED"
echo "Evidence: ${OUT}"
echo "==============================================="
