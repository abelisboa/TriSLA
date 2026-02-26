#!/usr/bin/env bash
set -euo pipefail

CHART_DIR="${CHART_DIR:-./helm/trisla}"

echo "Corrigindo includes trisla.image para padrão seguro..."

find "$CHART_DIR/templates" -type f -name "*.yaml" | while read file; do
  sed -i \
    's/include "trisla.image" (dict "image" \([^)]*\))/include "trisla.image" (dict "image" \1 "Values" .Values)/g' \
    "$file"
done

echo "Includes corrigidos."
