#!/usr/bin/env bash
set -euo pipefail

NS="${1:-trisla}"
OUT_BASE="/home/porvir5g/gtp5g/trisla/evidencias_hardening"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
EVD="${OUT_BASE}/nasp_adapter_restart_${TS}"
mkdir -p "${EVD}"

echo "=================================================="
echo "TriSLA — FORCE RESTART NASP ADAPTER (EVIDENCE)"
echo "Namespace : ${NS}"
echo "Evidence  : ${EVD}"
echo "=================================================="

echo "[1] Estado atual do Deployment (imagem no template)..."
kubectl get deploy -n "${NS}" trisla-nasp-adapter -o wide | tee "${EVD}/deploy_wide.txt"
kubectl get deploy -n "${NS}" trisla-nasp-adapter -o jsonpath='{.spec.template.spec.containers[0].image}'; echo | tee "${EVD}/deploy_image.txt"

echo "[2] Pod atual (antes do restart)..."
kubectl get pods -n "${NS}" -l app=trisla-nasp-adapter -o wide | tee "${EVD}/pods_before.txt"
POD_BEFORE="$(kubectl get pods -n "${NS}" -l app=trisla-nasp-adapter -o jsonpath='{.items[0].metadata.name}')"
echo "POD_BEFORE=${POD_BEFORE}" | tee "${EVD}/pod_before.txt"
kubectl get pod -n "${NS}" "${POD_BEFORE}" -o jsonpath='{.status.containerStatuses[0].imageID}'; echo | tee "${EVD}/imageid_before.txt"
kubectl get pod -n "${NS}" "${POD_BEFORE}" -o jsonpath='{.metadata.creationTimestamp}'; echo | tee "${EVD}/created_before.txt"

echo "[3] Forçando restart do Deployment..."
kubectl rollout restart -n "${NS}" deployment/trisla-nasp-adapter | tee "${EVD}/rollout_restart.txt"

echo "[4] Aguardando rollout..."
kubectl rollout status -n "${NS}" deployment/trisla-nasp-adapter --timeout=180s | tee "${EVD}/rollout_status.txt"

echo "[5] Pod após restart..."
kubectl get pods -n "${NS}" -l app=trisla-nasp-adapter -o wide | tee "${EVD}/pods_after.txt"
POD_AFTER="$(kubectl get pods -n "${NS}" -l app=trisla-nasp-adapter -o jsonpath='{.items[0].metadata.name}')"
echo "POD_AFTER=${POD_AFTER}" | tee "${EVD}/pod_after.txt"
kubectl get pod -n "${NS}" "${POD_AFTER}" -o jsonpath='{.status.containerStatuses[0].imageID}'; echo | tee "${EVD}/imageid_after.txt"
kubectl get pod -n "${NS}" "${POD_AFTER}" -o jsonpath='{.metadata.creationTimestamp}'; echo | tee "${EVD}/created_after.txt"

echo "[6] Logs recentes (primeiros 120s pós-giro)..."
kubectl logs -n "${NS}" "pod/${POD_AFTER}" --since=120s --tail=200 | tee "${EVD}/logs_after_120s.txt" || true

echo "=================================================="
echo "COMPLETED"
echo "Evidence: ${EVD}"
echo "=================================================="
