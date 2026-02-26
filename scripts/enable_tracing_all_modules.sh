#!/bin/bash
set -e

MODULES=("trisla-ml-nsmf" "trisla-decision-engine")

for module in "${MODULES[@]}"; do
  echo "Configurando OTLP em $module..."

  kubectl -n trisla set env deployment/$module \
    OTLP_ENABLED=true \
    OTLP_ENDPOINT=trisla-otel-collector:4317

  kubectl -n trisla rollout restart deployment/$module
done

echo "Tracing habilitado nos módulos."
