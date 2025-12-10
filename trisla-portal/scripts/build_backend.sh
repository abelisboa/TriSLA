#!/bin/bash
# Script para build da imagem Docker do backend

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"

echo "🔨 Building backend Docker image..."
echo "Backend directory: $BACKEND_DIR"

cd "$BACKEND_DIR"

# Verificar se Dockerfile existe
if [ ! -f "Dockerfile" ]; then
    echo "❌ Erro: Dockerfile não encontrado em $BACKEND_DIR"
    exit 1
fi

# Build da imagem
IMAGE_NAME="ghcr.io/abelisboa/trisla-portal-backend:latest"

echo "📦 Building image: $IMAGE_NAME"
docker build -t "$IMAGE_NAME" .

echo "✅ Backend image built successfully: $IMAGE_NAME"
echo "💡 Para fazer push, execute: ./scripts/push_backend.sh"

