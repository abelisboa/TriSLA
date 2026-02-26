#!/bin/bash
set -e

OWNER="abelisboa"

echo "=========================================================="
echo "TORNANDO TODOS os packages trisla-* PUBLICOS"
echo "=========================================================="

PACKAGES=$(gh api \
  -H "Accept: application/vnd.github+json" \
  /user/packages?package_type=container \
  --jq '.[].name' | grep '^trisla-')

for pkg in $PACKAGES; do
  echo "→ Tornando público: $pkg"

  gh api \
    --method PATCH \
    -H "Accept: application/vnd.github+json" \
    /user/packages/container/$pkg \
    -f visibility=public

done

echo "=========================================================="
echo "CONCLUÍDO"
echo "=========================================================="
