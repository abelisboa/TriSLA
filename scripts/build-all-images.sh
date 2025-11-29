#!/bin/bash
set -e

MODULES=(
  "bc-nssmf"
  "ml-nsmf"
  "sem-csmf"
  "sla-agent-layer"
  "decision-engine"
  "ui-dashboard"
  "nasp-adapter"
)

for module in "${MODULES[@]}"; do
  echo "🔥 Building image for trisla-${module}..."
  docker build -t ghcr.io/abelisboa/trisla-${module}:latest apps/${module}
  docker push ghcr.io/abelisboa/trisla-${module}:latest
done

echo "🎯 All images built & pushed successfully."
