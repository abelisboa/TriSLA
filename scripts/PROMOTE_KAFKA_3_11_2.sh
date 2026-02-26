#!/usr/bin/env bash
set -euo pipefail

IMAGE_BASE="ghcr.io/abelisboa/trisla-kafka"
SOURCE_TAG="v3.11.0"
TARGET_TAG="v3.11.2"

echo "=========================================================="
echo "PROMOVENDO KAFKA ${SOURCE_TAG} → ${TARGET_TAG}"
echo "=========================================================="

echo "[1/4] Verificando imagem local..."
podman images | grep trisla-kafka | grep ${SOURCE_TAG}

echo "[2/4] Retag da imagem..."
podman tag ${IMAGE_BASE}:${SOURCE_TAG} ${IMAGE_BASE}:${TARGET_TAG}

echo "[3/4] Push para GHCR..."
podman push ${IMAGE_BASE}:${TARGET_TAG}

echo "[4/4] Confirmando digest publicado..."
podman inspect ${IMAGE_BASE}:${TARGET_TAG} --format '{{.Digest}}'

echo "=========================================================="
echo "PROMOÇÃO CONCLUÍDA COM SUCESSO"
echo "=========================================================="
