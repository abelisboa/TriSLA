#!/bin/bash
# Script para build e push da imagem frontend v3.7.32
# Execute este script no WSL: bash build_and_push_v3.7.32.sh

set -e  # Parar em caso de erro

echo "🔨 Building frontend image v3.7.32..."

cd /mnt/c/Users/USER/Documents/TriSLA-clean/trisla-portal/frontend

# Verificar se Dockerfile existe
if [ ! -f "Dockerfile" ]; then
    echo "❌ Erro: Dockerfile não encontrado!"
    exit 1
fi

# Build da imagem
docker build -t ghcr.io/abelisboa/trisla-portal-frontend:v3.7.32 \
  --build-arg NEXT_PUBLIC_TRISLA_API_BASE_URL=http://localhost:8001/api/v1 \
  .

echo "✅ Build concluído com sucesso!"
echo ""
echo "📤 Fazendo push da imagem..."

# Push da imagem
docker push ghcr.io/abelisboa/trisla-portal-frontend:v3.7.32

echo "✅ Push concluído com sucesso!"
echo ""
echo "🔍 Verificando imagem..."

# Verificar se a imagem foi criada
docker images | grep trisla-portal-frontend | grep v3.7.32

echo ""
echo "✅ Imagem ghcr.io/abelisboa/trisla-portal-frontend:v3.7.32 pronta!"
echo ""
echo "📋 Próximos passos:"
echo "   1. Conectar ao NASP: ssh porvir5g@ppgca.unisinos.br"
echo "   2. SSH para node006: ssh node006"
echo "   3. Deploy: helm upgrade --install trisla-portal ./helm/trisla-portal -n trisla --create-namespace --wait"

