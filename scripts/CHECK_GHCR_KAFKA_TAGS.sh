#!/usr/bin/env bash
set -euo pipefail

echo "=========================================================="
echo "VERIFICAÇÃO GHCR — trisla-kafka"
echo "=========================================================="

IMAGE="ghcr.io/abelisboa/trisla-kafka"

echo
echo "Testando pull das versões conhecidas..."
echo "----------------------------------------------------------"

for TAG in v3.11.2 v3.11.1 v3.11.0 latest; do
  echo "→ Testando ${TAG}..."
  if docker pull ${IMAGE}:${TAG} >/dev/null 2>&1; then
    echo "  OK: ${TAG} existe"
  else
    echo "  NÃO ENCONTRADA: ${TAG}"
  fi
done

echo
echo "=========================================================="
echo "FIM VERIFICAÇÃO GHCR"
echo "=========================================================="
