#!/usr/bin/env bash
set -euo pipefail

NS="${1:-trisla}"

echo "=================================================="
echo "TriSLA — NASP ADAPTER RUNTIME ENV AUDIT"
echo "Namespace : ${NS}"
echo "=================================================="

POD=$(kubectl get pods -n "${NS}" -l app=trisla-nasp-adapter -o jsonpath='{.items[0].metadata.name}')

echo "Pod: $POD"
echo "------------------------------------------"
echo "[1] ENV reais do container:"
kubectl exec -n "${NS}" "$POD" -- printenv | sort

echo "------------------------------------------"
echo "[2] Variáveis críticas:"
kubectl exec -n "${NS}" "$POD" -- printenv | grep -E "OTLP|3GPP|CAPACITY|NASP|MODE|ENV" || true

echo "------------------------------------------"
echo "[3] Health check:"
kubectl exec -n "${NS}" "$POD" -- curl -s http://localhost:8085/health

echo
echo "=================================================="
