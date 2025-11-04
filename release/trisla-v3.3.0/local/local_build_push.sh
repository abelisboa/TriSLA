#!/bin/bash
# ============================================================
# Script: local_build_push.sh
# Objetivo: Build e Push de imagens Docker (TriSLA Portal)
# Autor: Abel Lisboa (TriSLA@NASP)
# ============================================================

set -e
BASE_DIR="$(dirname "$(pwd)")"
BACKEND_DIR="$BASE_DIR/apps/api"
FRONTEND_DIR="$BASE_DIR/apps/ui"
GITHUB_USER="abelisboa"
IMAGE_BACKEND="ghcr.io/${GITHUB_USER}/trisla-api:latest"
IMAGE_FRONTEND="ghcr.io/${GITHUB_USER}/trisla-ui:latest"

echo "🚀 Iniciando build completo do TriSLA Portal..."
sleep 1

# ------------------------------------------------------------
# 1. Backend - FastAPI
# ------------------------------------------------------------
echo "🔧 [1/4] Construindo imagem do backend (FastAPI)..."
cd "$BACKEND_DIR"

cat <<'EOF' > Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

docker build -t trisla-api:latest .
docker tag trisla-api:latest $IMAGE_BACKEND
echo "✅ Backend construído e marcado como $IMAGE_BACKEND"
sleep 1

# ------------------------------------------------------------
# 2. Frontend - React + Vite
# ------------------------------------------------------------
echo "🧩 [2/4] Construindo imagem do frontend (React + Vite)..."
cd "$FRONTEND_DIR"

cat <<'EOF' > Dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
EOF

docker build -t trisla-ui:latest .
docker tag trisla-ui:latest $IMAGE_FRONTEND
echo "✅ Frontend construído e marcado como $IMAGE_FRONTEND"
sleep 1

# ------------------------------------------------------------
# 3. Login no GitHub Container Registry
# ------------------------------------------------------------
echo "🔑 [3/4] Efetuando login no GitHub Container Registry..."
echo "Digite seu token do GitHub (com permissão write:packages):"
read -s GITHUB_TOKEN
echo $GITHUB_TOKEN | docker login ghcr.io -u $GITHUB_USER --password-stdin
echo "✅ Autenticação concluída!"
sleep 1

# ------------------------------------------------------------
# 4. Push das imagens
# ------------------------------------------------------------
echo "📦 [4/4] Publicando imagens no GHCR..."
docker push $IMAGE_BACKEND
docker push $IMAGE_FRONTEND
echo "✅ Push concluído com sucesso!"

# ------------------------------------------------------------
# 5. Resumo final
# ------------------------------------------------------------
echo "🏁 Build e push finalizados!"
echo "🔹 Backend: $IMAGE_BACKEND"
echo "🔹 Frontend: $IMAGE_FRONTEND"
echo "✨ Pronto para deploy via Helm no NASP!"
