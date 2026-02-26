#!/bin/bash
set -e

FRONTEND_DIR="$(dirname "$0")/../frontend"
IMAGE="ghcr.io/abelisboa/trisla-portal-frontend:latest"

# Usar variável de ambiente ou fallback para client-side (via túnel SSH)
# Client-side usa localhost:32002, server-side usa trisla-portal-backend:8001
NEXT_PUBLIC_API_URL="${NEXT_PUBLIC_API_URL:-http://localhost:32002/api/v1}"

echo "🔨 Building frontend image..."
echo "📝 NEXT_PUBLIC_API_URL: $NEXT_PUBLIC_API_URL"
docker build \
  --build-arg NEXT_PUBLIC_API_URL="$NEXT_PUBLIC_API_URL" \
  -t $IMAGE \
  "$FRONTEND_DIR"

echo "✅ Build complete. Run ./push_frontend.sh to push the image."
