#!/usr/bin/env bash
set -euo pipefail

NS="trisla"
NODE_IP="${NODE_IP:-<node1_ip>}"

echo "🔎 Verificando pods..."
kubectl get pods -n "$NS" -l app=trisla-portal -o wide

echo "⏳ Aguardando readiness..."
kubectl -n "$NS" wait --for=condition=Ready pod -l app=trisla-portal --timeout=180s

echo "🩺 Testando API pelo NodePort..."
curl -f "http://${NODE_IP}:30800/api/v1/health" || { echo "❌ Falhou"; exit 1; }
echo
echo "🌐 Teste UI (HTTP 200 esperado na raiz):"
curl -s -o /dev/null -w "%{http_code}\n" "http://${NODE_IP}:30173/"
