#!/usr/bin/env bash
set -euo pipefail

IMAGE="ghcr.io/abelisboa/trisla-kafka"
TAG="v3.11.2"
APP_DIR="./apps/kafka"   # ajuste se necessário

echo "=========================================================="
echo "REBUILD OFICIAL TRISLA-KAFKA ${TAG}"
echo "=========================================================="

if [ ! -d "$APP_DIR" ]; then
  echo "ERRO: Diretório $APP_DIR não encontrado."
  exit 1
fi

echo "[1/5] Build da imagem"
docker build -t ${IMAGE}:${TAG} ${APP_DIR}

echo "[2/5] Login GHCR"
echo $GHCR_TOKEN | docker login ghcr.io -u abelisboa --password-stdin

echo "[3/5] Push da imagem"
docker push ${IMAGE}:${TAG}

echo "[4/5] Verificando pull público"
docker pull ${IMAGE}:${TAG}

echo "[5/5] Concluído"
echo "Imagem ${IMAGE}:${TAG} publicada com sucesso."
