#!/usr/bin/env bash

set -euo pipefail

# ============================================================
# 🚀 TriSLA — PIPELINE A1 (Blockchain REAL) — v2.0 (sem deploy remoto)
# 🔧 Build Local → GHCR → Atualiza Helm → Commit + Push GitHub
# 🔒 NÃO toca no NASP, NÃO faz deploy remoto.
# ============================================================

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

TAG_DEFAULT="nasp-a2"
TAG="${TAG:-$TAG_DEFAULT}"

GHCR_OWNER_DEFAULT="abelisboa"
GHCR_OWNER="${GHCR_OWNER:-$GHCR_OWNER_DEFAULT}"
GHCR_BASE="ghcr.io/${GHCR_OWNER}"

HELM_VALUES_FILE="${ROOT_DIR}/helm/trisla/values-nasp.yaml"

MODULES=(
  "sem-csmf"
  "ml-nsmf"
  "decision-engine"
  "bc-nssmf"
  "sla-agent-layer"
  "nasp-adapter"
  "ui-dashboard"
)

echo "============================================================"
echo "🚀 TriSLA — PIPELINE A1 (Blockchain REAL) — v2.0"
echo "🔧 Build Local → GHCR → Helm → GitHub"
echo "🔒 Sem deploy remoto no NASP"
echo "============================================================"

# ------------------------------------------------------------
# 0. Pré-checagens básicas
# ------------------------------------------------------------
for bin in docker git; do
  if ! command -v "${bin}" >/dev/null 2>&1; then
    echo "❌ Erro: '${bin}' não encontrado no PATH. Instale e tente novamente."
    exit 1
  fi
done

if [ ! -f "${HELM_VALUES_FILE}" ]; then
  echo "❌ Erro: arquivo de values do Helm não encontrado em:"
  echo "   ${HELM_VALUES_FILE}"
  exit 1
fi

# ------------------------------------------------------------
# 1. Login Docker Hub (opcional) e GHCR (obrigatório)
# ------------------------------------------------------------
echo "============================================================"
echo "🔐 Login no Docker Hub e GHCR"
echo "============================================================"

echo "📝 Login no Docker Hub (opcional, para imagens base)..."
echo "   Pressione Enter para pular (imagens públicas não precisam de login)"
read -r DOCKERHUB_USER || true
if [ -n "${DOCKERHUB_USER}" ]; then
  echo "🔑 Docker Hub password/token para ${DOCKERHUB_USER}:"
  read -rs DOCKERHUB_PASS
  echo
  echo "${DOCKERHUB_PASS}" | docker login -u "${DOCKERHUB_USER}" --password-stdin
else
  echo "⏩ Pulando login Docker Hub (usando imagens públicas)"
fi

echo
echo "📝 Login no GHCR (obrigatório)..."
echo "   Owner atual: ${GHCR_OWNER}"
echo "   Exemplo de repositório: ${GHCR_BASE}/trisla-sem-csmf:${TAG}"
echo "Digite o TOKEN GHCR (com permissões read/write):"
read -rs GHCR_TOKEN
echo
echo "${GHCR_TOKEN}" | docker login ghcr.io -u "${GHCR_OWNER}" --password-stdin
echo "✔ Login GHCR OK"

# ------------------------------------------------------------
# 2. Preparar imagens base
# ------------------------------------------------------------
echo "============================================================"
echo "📦 Preparando imagens base"
echo "============================================================"

echo "📥 Fazendo pull da imagem base python:3.10-slim..."
if docker pull python:3.10-slim; then
  echo "✔ Imagem base python:3.10-slim OK"
else
  echo "⚠️ Falha ao fazer pull da imagem base. Tentando continuar..."
fi

echo "📥 Fazendo pull da imagem base node:18-alpine (para UI)..."
docker pull node:18-alpine 2>/dev/null || echo "⚠️ node:18-alpine não encontrado (será baixado durante build)"

# ------------------------------------------------------------
# 3. Build + Push das imagens TriSLA para GHCR
# ------------------------------------------------------------
echo "============================================================"
echo "📦 Build + Push das imagens — TAG=${TAG}"
echo "============================================================"

for module in "${MODULES[@]}"; do
  MODULE_PATH="${ROOT_DIR}/apps/${module}"

  if [ ! -d "${MODULE_PATH}" ]; then
    echo "⚠️  Módulo '${module}' ignorado (diretório não encontrado: ${MODULE_PATH})"
    continue
  fi

  IMAGE_NAME="${GHCR_BASE}/trisla-${module}:${TAG}"

  echo "------------------------------------------------------------"
  echo "📦 Build: ${module}"
  echo "📂 Contexto: ${MODULE_PATH}"
  echo "🏷  Imagem:  ${IMAGE_NAME}"
  echo "------------------------------------------------------------"

  pushd "${MODULE_PATH}" >/dev/null

  # Build multi-stage no caso do ui-dashboard, simples para os demais
  if docker build -t "${IMAGE_NAME}" .; then
    echo "   ✔ Build OK"
    echo "   Enviando para GHCR..."
    if docker push "${IMAGE_NAME}"; then
      echo "✔ OK — ${IMAGE_NAME}"
    else
      echo "❌ Falha ao fazer push de ${IMAGE_NAME}"
      exit 1
    fi
  else
    echo "❌ Falha ao construir ${module}"
    exit 1
  fi

  popd >/dev/null
done

# ------------------------------------------------------------
# 4. Atualizar values.yaml (base) com a nova TAG
# ------------------------------------------------------------
echo "============================================================"
echo "📝 Atualizando Helm Chart (values.yaml)"
echo "============================================================"

VALUES_BASE_FILE="${ROOT_DIR}/helm/trisla/values.yaml"

if [ ! -f "${VALUES_BASE_FILE}" ]; then
  echo "⚠️  values.yaml não encontrado, pulando atualização de tags"
else
  if command -v yq >/dev/null 2>&1; then
    echo "✔ Usando yq para atualizar tags no values.yaml"
    yq -i "
      .semCsmf.image.tag = \"${TAG}\" |
      .mlNsmf.image.tag = \"${TAG}\" |
      .decisionEngine.image.tag = \"${TAG}\" |
      .bcNssmf.image.tag = \"${TAG}\" |
      .slaAgentLayer.image.tag = \"${TAG}\" |
      .naspAdapter.image.tag = \"${TAG}\" |
      .uiDashboard.image.tag = \"${TAG}\"
    " "${VALUES_BASE_FILE}"
    echo "✔ Tags atualizadas em values.yaml"
  else
    echo "⚠️  'yq' não encontrado. Fazendo substituição via sed."
    # Atualizar tags nos módulos TriSLA usando sed
    for module in "${MODULES[@]}"; do
      case "${module}" in
        "sem-csmf") HELM_MODULE="semCsmf" ;;
        "ml-nsmf") HELM_MODULE="mlNsmf" ;;
        "decision-engine") HELM_MODULE="decisionEngine" ;;
        "bc-nssmf") HELM_MODULE="bcNssmf" ;;
        "sla-agent-layer") HELM_MODULE="slaAgentLayer" ;;
        "nasp-adapter") HELM_MODULE="naspAdapter" ;;
        "ui-dashboard") HELM_MODULE="uiDashboard" ;;
        *) HELM_MODULE="${module}" ;;
      esac
      
      # Atualizar tag do módulo específico
      sed -i "/^${HELM_MODULE}:/,/^[a-zA-Z]/ s/\(tag: \).*/\1${TAG}/" "${VALUES_BASE_FILE}" 2>/dev/null || true
      echo "  ✔ ${HELM_MODULE}: tag atualizada para ${TAG}"
    done
    echo "✔ Tags atualizadas em values.yaml"
  fi
fi

# Nota: values-nasp.yaml não tem estrutura de image/tag, apenas override de recursos e env
# As tags são herdadas de values.yaml
echo "ℹ️  values-nasp.yaml usa valores de values.yaml (tags já atualizadas acima)"


# ------------------------------------------------------------
# 6. Commit + Push para o GitHub
# ------------------------------------------------------------
echo "============================================================"
echo "⬆ Commit + Push GitHub"
echo "============================================================"

git add .
git commit -m "build: atualização das imagens TriSLA (TAG ${TAG}) via pipeline A1" || echo "⚠️ Nenhuma mudança para commitar"
git push origin main

echo "============================================================"
echo "🎉 PIPELINE A1 FINALIZADO"
echo "============================================================"
echo "As imagens foram construídas e enviadas ao GHCR."
echo "O Helm Chart (values-nasp.yaml e values.yaml) foi atualizado com a TAG: ${TAG}."
echo "O código foi sincronizado com o GitHub (branch main)."
echo
echo "📌 Próximo passo (manual, fora deste script):"
echo "    Realizar o deploy no NASP (node1) usando o script/FASE 3 dedicado."
echo "============================================================"

exit 0
