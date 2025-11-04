#!/usr/bin/env bash
# ============================================================
# Build Local - TriSLA Dashboard v3.2.4
# Build das imagens Docker localmente
# ============================================================

set -e

GITHUB_USER="abelisboa"
REPO="trisla-public"
BACKEND_IMAGE="ghcr.io/${GITHUB_USER}/${REPO}/trisla-dashboard-backend:latest"
FRONTEND_IMAGE="ghcr.io/${GITHUB_USER}/${REPO}/trisla-dashboard-frontend:latest"

echo "======================================================"
echo "🔨 Build Local - TriSLA Dashboard v3.2.4"
echo "======================================================"
echo ""

# Build Backend
echo "📦 [1/2] Building backend image..."
cd backend
docker build -t ${BACKEND_IMAGE} .
docker tag ${BACKEND_IMAGE} trisla-dashboard-backend:latest
echo "✅ Backend image built: ${BACKEND_IMAGE}"
cd ..

# Build Frontend
echo "📦 [2/2] Building frontend image..."
cd frontend
docker build -t ${FRONTEND_IMAGE} .
docker tag ${FRONTEND_IMAGE} trisla-dashboard-frontend:latest
echo "✅ Frontend image built: ${FRONTEND_IMAGE}"
cd ..

echo ""
echo "======================================================"
echo "✅ Build concluído!"
echo "======================================================"
echo ""
echo "Para testar localmente:"
echo "  docker-compose up"
echo ""
echo "Para fazer push das imagens:"
echo "  docker push ${BACKEND_IMAGE}"
echo "  docker push ${FRONTEND_IMAGE}"
