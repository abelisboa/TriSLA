#!/bin/bash
# Script para build da imagem Docker do frontend

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

echo "🔨 Building frontend Docker image..."
echo "Frontend directory: $FRONTEND_DIR"

cd "$FRONTEND_DIR"

# Verificar se Dockerfile existe
if [ ! -f "Dockerfile" ]; then
    echo "❌ Erro: Dockerfile não encontrado em $FRONTEND_DIR"
    exit 1
fi

# Build da imagem
IMAGE_NAME="ghcr.io/abelisboa/trisla-portal-frontend:latest"

echo "📦 Building image: $IMAGE_NAME"
docker build -t "$IMAGE_NAME" .

echo "✅ Frontend image built successfully: $IMAGE_NAME"
echo "💡 Para fazer push, execute: ./scripts/push_frontend.sh"

