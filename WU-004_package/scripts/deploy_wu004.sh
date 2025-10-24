#!/bin/bash
set -e
GHCR_USER="abelisboa"
GHCR_BASE="ghcr.io/${GHCR_USER}"
NASP_PATH="/home/porvir5g/gtp5g/trisla-nsp"
ZIP_NAME="WU-004_package.zip"

if [ -z "$GHCR_TOKEN" ]; then
  echo "❌ Variável GHCR_TOKEN não encontrada. Use: export GHCR_TOKEN=ghp_xxxxx"
  exit 1
fi

echo $GHCR_TOKEN | docker login ghcr.io -u ${GHCR_USER} --password-stdin

for MODULE in ai semantic integration blockchain monitoring; do
  echo "🔨 Build $MODULE"
  docker build --no-cache -t ${GHCR_BASE}/trisla-${MODULE}:latest ./WU-004_package/src/${MODULE}
  docker push ${GHCR_BASE}/trisla-${MODULE}:latest
done

zip -r ${ZIP_NAME} WU-004_package > /dev/null
scp ${ZIP_NAME} porvir5g@node1:${NASP_PATH}/
