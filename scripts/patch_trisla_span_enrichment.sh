#!/bin/bash
set -e

echo "Aplicando enriquecimento de spans..."

kubectl -n trisla exec deployment/trisla-nasp-adapter -- \
sed -i '/span.set_attribute/a\        span.set_attribute("trisla.module", "nasp-adapter")' /app/src/main.py

kubectl -n trisla rollout restart deployment/trisla-nasp-adapter
kubectl -n trisla rollout status deployment/trisla-nasp-adapter

echo "Span enrichment aplicado."
