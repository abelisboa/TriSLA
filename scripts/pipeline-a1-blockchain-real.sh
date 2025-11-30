#!/bin/bash

set -e

echo "============================================================"
echo "🚀 TriSLA — PIPELINE A1 (Blockchain REAL)"
echo "🔧 Build Local → GHCR → GitHub → Deploy NASP (node006)"
echo "============================================================"

GHCR_USER="abelisboa"
GHCR_REGISTRY="ghcr.io/${GHCR_USER}"
TAG="nasp-a2"

MODULES=(
  "sem-csmf"
  "ml-nsmf"
  "decision-engine"
  "bc-nssmf"
  "sla-agent-layer"
  "nasp-adapter"
  "ui-dashboard"
)

ROOT_DIR="$(pwd)"

echo "============================================================"
echo "🔐 Login no Docker Hub e GHCR"
echo "============================================================"

# Verificar se Docker está rodando
if ! docker info > /dev/null 2>&1; then
  echo "❌ Docker não está rodando. Inicie o Docker Desktop e tente novamente."
  exit 1
fi

# Login no Docker Hub (para imagens base públicas, mas ajuda com credenciais)
echo "📝 Login no Docker Hub (opcional, para imagens base)..."
echo "   Pressione Enter para pular (imagens públicas não precisam de login)"
read -t 5 DOCKER_HUB_USER || DOCKER_HUB_USER=""
if [ -n "${DOCKER_HUB_USER}" ]; then
  echo "   Digite a senha do Docker Hub:"
  read -s DOCKER_HUB_PASS
  echo "${DOCKER_HUB_PASS}" | docker login -u "${DOCKER_HUB_USER}" --password-stdin || echo "⚠️ Login Docker Hub falhou (continuando...)"
else
  echo "   Pulando login Docker Hub (usando imagens públicas)"
fi

# Login no GHCR
echo ""
echo "📝 Login no GHCR (obrigatório)..."
echo "Digite o TOKEN GHCR (com permissões read/write):"
read -s GHCR_TOKEN

echo "${GHCR_TOKEN}" | docker login ghcr.io -u "${GHCR_USER}" --password-stdin
echo "✔ Login GHCR OK"

echo "============================================================"
echo "📦 Preparando imagens base"
echo "============================================================"

# Fazer pull das imagens base necessárias
echo "📥 Fazendo pull da imagem base python:3.10-slim..."
if docker pull python:3.10-slim; then
  echo "✔ Imagem base python:3.10-slim baixada"
else
  echo "⚠️ Falha ao fazer pull da imagem base. Tentando continuar..."
  echo "   Se o build falhar, verifique sua conexão com Docker Hub"
fi

echo "📥 Fazendo pull da imagem base node:18-alpine (para UI)..."
docker pull node:18-alpine 2>/dev/null || echo "⚠️ node:18-alpine não encontrado (será baixado durante build)"

echo "============================================================"
echo "📦 Build + Push das imagens — TAG=${TAG}"
echo "============================================================"

for module in "${MODULES[@]}"; do
  IMAGE="${GHCR_REGISTRY}/trisla-${module}:${TAG}"
  MODULE_PATH="${ROOT_DIR}/apps/${module}"

  echo "------------------------------------------------------------"
  echo "📦 Build: ${module}"
  echo "------------------------------------------------------------"

  if [ ! -d "${MODULE_PATH}" ]; then
    echo "⚠️ Diretório não encontrado: ${MODULE_PATH}"
    continue
  fi

  if [ ! -f "${MODULE_PATH}/Dockerfile" ]; then
    echo "⚠️ Dockerfile não encontrado em: ${MODULE_PATH}"
    continue
  fi

  echo "   Construindo imagem..."
  if docker build -t "${IMAGE}" "${MODULE_PATH}"; then
    echo "   ✔ Build OK"
    echo "   Enviando para GHCR..."
    if docker push "${IMAGE}"; then
      echo "✔ OK — ${IMAGE}"
    else
      echo "❌ Falha ao fazer push de ${IMAGE}"
      exit 1
    fi
  else
    echo "❌ Falha ao construir ${module}"
    exit 1
  fi
done

echo "============================================================"
echo "📝 Atualizando Helm Chart (values.yaml)"
echo "============================================================"

VALUES_FILE="helm/trisla/values.yaml"

if [ ! -f "${VALUES_FILE}" ]; then
  echo "❌ Arquivo não encontrado: ${VALUES_FILE}"
  exit 1
fi

# Atualizar tag apenas nos módulos TriSLA (não Kafka, Prometheus, etc.)
for module in "${MODULES[@]}"; do
  # Converter nome do módulo para formato do Helm (ex: sem-csmf -> semCsmf)
  case "${module}" in
    "sem-csmf")
      HELM_MODULE="semCsmf"
      ;;
    "ml-nsmf")
      HELM_MODULE="mlNsmf"
      ;;
    "decision-engine")
      HELM_MODULE="decisionEngine"
      ;;
    "bc-nssmf")
      HELM_MODULE="bcNssmf"
      ;;
    "sla-agent-layer")
      HELM_MODULE="slaAgentLayer"
      ;;
    "nasp-adapter")
      HELM_MODULE="naspAdapter"
      ;;
    "ui-dashboard")
      HELM_MODULE="uiDashboard"
      ;;
    *)
      HELM_MODULE="${module}"
      ;;
  esac
  
  # Atualizar tag do módulo específico
  sed -i "/^${HELM_MODULE}:/,/^[a-zA-Z]/ s/\(tag: \).*/\1${TAG}/" "${VALUES_FILE}"
  echo "  ✔ ${HELM_MODULE}: tag atualizada para ${TAG}"
done

echo "✔ TAG ${TAG} aplicada a todos os módulos TriSLA no Helm Chart"

echo "============================================================"
echo "⬆ Commit + Push GitHub"
echo "============================================================"

git add .
git commit -m "🚀 TriSLA A1 — Build + GHCR + Helm atualizado (tag: ${TAG})" || echo "⚠️ Nenhuma mudança para commitar"
git push origin main

echo "✔ Código enviado ao GitHub"

echo "============================================================"
echo "🌐 Deploy remoto no NASP via SSH (2 saltos)"
echo "============================================================"

ssh -t porvir5g@ppgca.unisinos.br << EOF1
echo "🔐 Conectando ao node006..."
ssh -t node006 << 'EOF2'

cd /home/porvir5g/gtp5g/trisla

echo "🧹 Limpando deploy anterior..."
kubectl delete namespace trisla --ignore-not-found=true
sleep 5

echo "📂 Criando namespace trisla..."
kubectl create namespace trisla

echo "🔐 Criando secret GHCR..."
kubectl delete secret ghcr-secret -n trisla --ignore-not-found=true
kubectl create secret docker-registry ghcr-secret \\
  --docker-server=ghcr.io \\
  --docker-username=abelisboa \\
  --docker-password=${GHCR_TOKEN} \\
  --namespace=trisla

echo "🚀 Helm deploy TriSLA A1..."
helm upgrade --install trisla ./helm/trisla \\
  --namespace trisla \\
  --values ./helm/trisla/values-nasp.yaml \\
  --timeout 25m \\
  --wait

echo "============================================================"
echo "🔎 Verificação dos pods..."
echo "============================================================"
kubectl get pods -n trisla -o wide

echo "============================================================"
echo "🎉 DEPLOY A1 COMPLETO! Blockchain REAL ativo."
echo "============================================================"

EOF2
EOF1

echo "============================================================"
echo "🎉 PIPELINE A1 FINALIZADO COM SUCESSO!"
echo "============================================================"

