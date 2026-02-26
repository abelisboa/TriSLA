#!/usr/bin/env bash
set -euo pipefail

NS="trisla"
REL="trisla"
APP_DIR="/home/porvir5g/gtp5g/trisla/apps/nasp-adapter"
IMAGE_REPO="ghcr.io/abelisboa/trisla-nasp-adapter"

TS="$(date -u +%Y%m%dT%H%M%SZ)"
EVD="/home/porvir5g/gtp5g/trisla/evidencias_build/nasp_adapter_${TS}"
mkdir -p "${EVD}"

echo "=================================================="
echo "TriSLA — BUILD + PUSH + DEPLOY (DIGEST ONLY)"
echo "Namespace : ${NS}"
echo "Release   : ${REL}"
echo "Context   : ${APP_DIR}"
echo "Evidence  : ${EVD}"
echo "=================================================="

# ---------------------------------------------------
# 1️⃣ Validação
# ---------------------------------------------------

if [[ ! -f "${APP_DIR}/Dockerfile" ]]; then
  echo "❌ Dockerfile não encontrado em ${APP_DIR}"
  exit 1
fi

# ---------------------------------------------------
# 2️⃣ Build com tag temporária (não usada no deploy)
# ---------------------------------------------------

TMP_TAG="build-${TS}"

echo "1️⃣ Building image..."
docker build -t "${IMAGE_REPO}:${TMP_TAG}" "${APP_DIR}" | tee "${EVD}/docker_build.txt"

# ---------------------------------------------------
# 3️⃣ Push
# ---------------------------------------------------

echo "2️⃣ Pushing image..."
docker push "${IMAGE_REPO}:${TMP_TAG}" | tee "${EVD}/docker_push.txt"

# ---------------------------------------------------
# 4️⃣ Extração do digest real
# ---------------------------------------------------

DIGEST=$(docker inspect --format='{{index .RepoDigests 0}}' "${IMAGE_REPO}:${TMP_TAG}" | cut -d@ -f2)

if [[ -z "${DIGEST}" ]]; then
  echo "❌ Não foi possível extrair digest"
  exit 1
fi

echo "${DIGEST}" | tee "${EVD}/digest.txt"
echo "Digest: ${DIGEST}"

# ---------------------------------------------------
# 5️⃣ Deploy via Helm (digest only)
# ---------------------------------------------------

echo "3️⃣ Deploy via Helm..."

helm upgrade "${REL}" helm/trisla \
  -n "${NS}" \
  --reuse-values \
  --set naspAdapter.image.repository="${IMAGE_REPO}" \
  --set naspAdapter.image.digest="${DIGEST}" \
  | tee "${EVD}/helm_upgrade.txt"

# ---------------------------------------------------
# 6️⃣ Rollout
# ---------------------------------------------------

echo "4️⃣ Aguardando rollout..."
kubectl rollout status -n "${NS}" deploy/trisla-nasp-adapter --timeout=180s | tee "${EVD}/rollout_status.txt"

# ---------------------------------------------------
# 7️⃣ Confirmação do digest em execução
# ---------------------------------------------------

echo "5️⃣ Validando digest real em execução..."

POD=$(kubectl get pods -n "${NS}" -l app=trisla-nasp-adapter -o jsonpath='{.items[0].metadata.name}')
kubectl get pod -n "${NS}" "${POD}" -o jsonpath='{.status.containerStatuses[0].imageID}' \
  | tee "${EVD}/runtime_digest.txt"

echo
echo "=================================================="
echo "DEPLOY COMPLETED COM SUCESSO"
echo "Digest aplicado: ${DIGEST}"
echo "Evidence: ${EVD}"
echo "=================================================="
