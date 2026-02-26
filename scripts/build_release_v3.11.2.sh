#!/bin/bash
# PROMPT_RELEASE_CIENTIFICA_TRISLA_v3.11.2 — Build + Push imagens com tag exata v3.11.2
# Executar em node006: cd /home/porvir5g/gtp5g/trisla && ./scripts/build_release_v3.11.2.sh
# Regra: tag DEVE ser exatamente v3.11.2 (sem prefixos/sufixos)

set -e
TAG=v3.11.2
REGISTRY=ghcr.io/abelisboa
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== Build TriSLA $TAG (from $ROOT) ==="

build_push() {
  local name=$1
  local context=$2
  local dockerfile=${3:-Dockerfile}
  echo "--- $name ---"
  docker build -t "$REGISTRY/$name:$TAG" -f "$context/$dockerfile" "$context"
  docker push "$REGISTRY/$name:$TAG"
}

# Apps em apps/
build_push trisla-sem-csmf     apps/sem-csmf
build_push trisla-ml-nsmf     apps/ml-nsmf
build_push trisla-decision-engine apps/decision-engine
build_push trisla-bc-nssmf    apps/bc-nssmf
build_push trisla-besu        apps/besu
build_push trisla-nasp-adapter apps/nasp-adapter
build_push trisla-sla-agent-layer apps/sla-agent-layer
build_push trisla-ui-dashboard apps/ui-dashboard
build_push trisla-traffic-exporter apps/traffic-exporter

# Portal (backend e frontend)
build_push trisla-portal-backend  trisla-portal/backend
build_push trisla-portal-frontend trisla-portal/frontend

echo "=== FASE 2: Listar imagens $TAG ==="
docker images | grep trisla | grep "$TAG"
