#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# TRISLA IMAGE UNIFORMITY GUARD
# Validação determinística de imagens no namespace trisla
# ============================================================

NS="${NS:-trisla}"
EXPECTED_VERSION="${EXPECTED_VERSION:-v3.11.2}"
EXPECTED_REGISTRY="ghcr.io/abelisboa"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_DIR="./evidencias_uniformity_${TS}"

mkdir -p "$OUT_DIR"

echo "======================================================"
echo "TRISLA IMAGE UNIFORMITY GUARD"
echo "Namespace         : $NS"
echo "Expected Version  : $EXPECTED_VERSION"
echo "Expected Registry : $EXPECTED_REGISTRY"
echo "Timestamp         : $TS"
echo "Output            : $OUT_DIR"
echo "======================================================"
echo

echo "FASE 1 — Coletando imagens dos Deployments"
echo "-------------------------------------------"

kubectl get deploy -n "$NS" -o jsonpath='{range .items[*]}{.metadata.name}{"|"}{range .spec.template.spec.containers[*]}{.image}{" "}{end}{"\n"}{end}' \
  > "$OUT_DIR/deploy_images_raw.txt"

awk -F'|' '
{
  split($2,a," ");
  for(i in a) if(a[i]!="") print $1 "|" a[i]
}' "$OUT_DIR/deploy_images_raw.txt" \
  > "$OUT_DIR/deploy_images_parsed.txt"

echo "Total containers encontrados: $(wc -l < "$OUT_DIR/deploy_images_parsed.txt")"
echo

BAD=0

echo "FASE 2 — Validação individual"
echo "-------------------------------------------"

while IFS='|' read -r deploy image; do

  echo "Verificando: $deploy -> $image"

  # 1️⃣ Bloqueio latest
  if [[ "$image" == *":latest" ]]; then
    echo "  ❌ ERRO: uso de :latest"
    BAD=1
  fi

  # 2️⃣ Bloqueio sem tag
  last="${image##*/}"
  if [[ "$last" != *":"* ]]; then
    echo "  ❌ ERRO: imagem sem tag explícita"
    BAD=1
  fi

  # 3️⃣ Verificação registry esperado (apenas para imagens trisla)
  if [[ "$image" == *"trisla-"* ]]; then
    if [[ "$image" != "$EXPECTED_REGISTRY/"* ]]; then
      echo "  ❌ ERRO: registry inesperado"
      BAD=1
    fi
  fi

  # 4️⃣ Verificação versão uniforme
  if [[ "$image" == *"trisla-"* ]]; then
    tag="${image##*:}"
    if [[ "$tag" != "$EXPECTED_VERSION" ]]; then
      echo "  ❌ ERRO: versão divergente ($tag)"
      BAD=1
    fi
  fi

done < "$OUT_DIR/deploy_images_parsed.txt"

echo
echo "FASE 3 — Resumo"
echo "-------------------------------------------"

if [[ $BAD -eq 1 ]]; then
  echo "❌ SISTEMA NÃO UNIFORME"
  echo "Falhas detectadas. Verifique: $OUT_DIR"
  exit 1
else
  echo "✅ SISTEMA 100% UNIFORME E DETERMINÍSTICO"
  exit 0
fi
