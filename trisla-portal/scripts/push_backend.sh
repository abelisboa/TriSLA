#!/bin/bash
# Script para push da imagem Docker do backend para ghcr.io

set -e

IMAGE_NAME="ghcr.io/abelisboa/trisla-portal-backend:latest"

echo "📤 Pushing backend image to ghcr.io..."
echo "Image: $IMAGE_NAME"

# Verificar se a imagem existe localmente
if ! docker image inspect "$IMAGE_NAME" > /dev/null 2>&1; then
    echo "❌ Erro: Imagem $IMAGE_NAME não encontrada localmente"
    echo "💡 Execute primeiro: ./scripts/build_backend.sh"
    exit 1
fi

# Fazer login no GitHub Container Registry (se necessário)
echo "🔐 Verificando autenticação no ghcr.io..."
if ! docker info | grep -q "ghcr.io"; then
    echo "⚠️  Você pode precisar fazer login no ghcr.io:"
    echo "   echo \$GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin"
fi

# Push da imagem
echo "📤 Pushing $IMAGE_NAME..."
docker push "$IMAGE_NAME"

echo "✅ Backend image pushed successfully to ghcr.io"

