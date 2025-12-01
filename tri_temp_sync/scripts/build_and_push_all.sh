#!/usr/bin/env bash
set -euo pipefail

# ============================================
# TriSLA - Build and Push All Images to GHCR
# ============================================
# Script para construir e publicar todas as imagens Docker
# do TriSLA no GitHub Container Registry (GHCR)
# ============================================

GITHUB_USERNAME="${GITHUB_USERNAME:-abelisboa}"
GHCR_NAMESPACE="ghcr.io/${GITHUB_USERNAME}"

SERVICES=(
  "bc-nssmf"
  "ml-nsmf"
  "sem-csmf"
  "decision-engine"
  "sla-agent-layer"
  "ui-dashboard"
  "nasp-adapter"
)

# Verificar se Docker está disponível
if ! command -v docker &>/dev/null; then
  echo "❌ docker não encontrado. Ajuste para usar podman/nerdctl se necessário."
  exit 1
fi

# Verificar se GHCR_TOKEN está definido
if [[ -z "${GHCR_TOKEN:-}" ]]; then
  echo "⚠️ Variável GHCR_TOKEN não definida."
  echo "   Exporte GHCR_TOKEN antes de rodar este script:"
  echo "   export GHCR_TOKEN='seu_token_aqui'"
  exit 1
fi

echo "🔐 Efetuando login no GHCR..."
echo "${GHCR_TOKEN}" | docker login ghcr.io -u "${GITHUB_USERNAME}" --password-stdin

# Criar diretório de logs
LOG_DIR="logs"
mkdir -p "${LOG_DIR}"
BUILD_LOG="${LOG_DIR}/build_and_push_$(date +%Y%m%d_%H%M%S).log"

echo "📦 Iniciando build e push de imagens..."
echo "   Log: ${BUILD_LOG}"

for service in "${SERVICES[@]}"; do
  SERVICE_DIR="apps/${service}"
  
  if [[ ! -d "${SERVICE_DIR}" ]]; then
    echo "⚠️ Diretório ${SERVICE_DIR} não encontrado. Pulando..."
    continue
  fi

  IMAGE_NAME="${GHCR_NAMESPACE}/trisla-${service}:latest"
  
  echo ""
  echo "=========================================="
  echo "📦 Construindo ${IMAGE_NAME}..."
  echo "=========================================="
  
  # Build da imagem
  if docker build -t "${IMAGE_NAME}" "./${SERVICE_DIR}" >> "${BUILD_LOG}" 2>&1; then
    echo "✅ Build concluído: ${IMAGE_NAME}"
  else
    echo "❌ Erro no build: ${IMAGE_NAME}"
    echo "   Verifique o log: ${BUILD_LOG}"
    exit 1
  fi

  echo "🚀 Enviando ${IMAGE_NAME} para GHCR..."
  
  # Push da imagem
  if docker push "${IMAGE_NAME}" >> "${BUILD_LOG}" 2>&1; then
    echo "✅ Push concluído: ${IMAGE_NAME}"
  else
    echo "❌ Erro no push: ${IMAGE_NAME}"
    echo "   Verifique o log: ${BUILD_LOG}"
    exit 1
  fi
done

echo ""
echo "=========================================="
echo "✅ Todas as imagens foram construídas e enviadas com sucesso!"
echo "=========================================="
echo ""
echo "📊 Resumo:"
for service in "${SERVICES[@]}"; do
  IMAGE_NAME="${GHCR_NAMESPACE}/trisla-${service}:latest"
  echo "   ✅ ${IMAGE_NAME}"
done
echo ""
echo "📝 Log completo: ${BUILD_LOG}"
echo ""


