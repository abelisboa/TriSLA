#!/usr/bin/env bash
set -euo pipefail

OWNER="abelisboa"

KEEP_PACKAGES=(
"trisla-bc-nssmf"
"trisla-ml-nsmf"
"trisla-decision-engine"
"trisla-sem-csmf"
"trisla-sla-agent-layer"
"trisla-nasp-adapter"
"trisla-ui-dashboard"
"trisla-portal-backend"
"trisla-portal-frontend"
"trisla-traffic-exporter"
"trisla-kafka"
"trisla-besu"
)

echo "=========================================================="
echo "GHCR STRICT CLEAN — Mantendo apenas packages oficiais"
echo "=========================================================="

ALL_PACKAGES=$(gh api users/$OWNER/packages?package_type=container --jq '.[].name')

for pkg in $ALL_PACKAGES; do
    keep=false
    for allowed in "${KEEP_PACKAGES[@]}"; do
        if [[ "$pkg" == "$allowed" ]]; then
            keep=true
            break
        fi
    done

    if [ "$keep" = false ]; then
        echo "✗ Deletando package: $pkg"
        gh api \
          --method DELETE \
          -H "Accept: application/vnd.github+json" \
          /users/$OWNER/packages/container/$pkg || true
    else
        echo "✓ Mantendo: $pkg"
    fi
done

echo "=========================================================="
echo "CLEANUP FINALIZADO"
echo "=========================================================="
