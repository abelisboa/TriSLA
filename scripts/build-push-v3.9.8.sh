#!/bin/bash
# Script para Build e Push v3.9.8
# Uso: export GITHUB_TOKEN=<token> && ./scripts/build-push-v3.9.8.sh

set -e

if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ ERRO: GITHUB_TOKEN não está definido"
    echo "Execute: export GITHUB_TOKEN=<seu_token>"
    exit 1
fi

export TAG=v3.9.8

echo "=== Login no GHCR ==="
echo "$GITHUB_TOKEN" | docker login ghcr.io -u abelisboa --password-stdin

echo "=== Build e Push - Core Modules ==="

echo "[1/9] Building trisla-sem-csmf..."
docker build --no-cache -t ghcr.io/abelisboa/trisla-sem-csmf:$TAG apps/sem-csmf
docker push ghcr.io/abelisboa/trisla-sem-csmf:$TAG

echo "[2/9] Building trisla-ml-nsmf..."
docker build --no-cache -t ghcr.io/abelisboa/trisla-ml-nsmf:$TAG apps/ml-nsmf
docker push ghcr.io/abelisboa/trisla-ml-nsmf:$TAG

echo "[3/9] Building trisla-decision-engine..."
docker build --no-cache -t ghcr.io/abelisboa/trisla-decision-engine:$TAG apps/decision-engine
docker push ghcr.io/abelisboa/trisla-decision-engine:$TAG

echo "[4/9] Building trisla-nasp-adapter..."
docker build --no-cache -t ghcr.io/abelisboa/trisla-nasp-adapter:$TAG apps/nasp-adapter
docker push ghcr.io/abelisboa/trisla-nasp-adapter:$TAG

echo "[5/9] Building trisla-sla-agent-layer..."
docker build --no-cache -t ghcr.io/abelisboa/trisla-sla-agent-layer:$TAG apps/sla-agent-layer
docker push ghcr.io/abelisboa/trisla-sla-agent-layer:$TAG

echo "[6/9] Building trisla-bc-nssmf..."
docker build --no-cache -t ghcr.io/abelisboa/trisla-bc-nssmf:$TAG apps/bc-nssmf
docker push ghcr.io/abelisboa/trisla-bc-nssmf:$TAG

echo "[7/9] Building trisla-ui-dashboard..."
docker build --no-cache -t ghcr.io/abelisboa/trisla-ui-dashboard:$TAG apps/ui-dashboard
docker push ghcr.io/abelisboa/trisla-ui-dashboard:$TAG

echo "[8/9] Building trisla-portal-backend..."
docker build --no-cache -t ghcr.io/abelisboa/trisla-portal-backend:$TAG trisla-portal/backend
docker push ghcr.io/abelisboa/trisla-portal-backend:$TAG

echo "[9/9] Building trisla-portal-frontend..."
docker build --no-cache -t ghcr.io/abelisboa/trisla-portal-frontend:$TAG trisla-portal/frontend
docker push ghcr.io/abelisboa/trisla-portal-frontend:$TAG

echo "✅ Todos os builds e pushes concluídos com sucesso!"
