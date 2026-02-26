#!/bin/bash
set -e

NAMESPACE="monitoring"

echo "Habilitando exemplars no Prometheus..."

kubectl -n $NAMESPACE patch configmap prometheus-kube-prometheus-prometheus \
  --type merge \
  -p '{"data":{"prometheus.yml":"global:\n  scrape_interval: 15s\n  evaluation_interval: 15s\n  external_labels:\n    monitor: \"trisla\"\n  enable_exemplar_storage: true\n"}}'

kubectl -n $NAMESPACE rollout restart deployment prometheus-kube-prometheus-prometheus

echo "Exemplars habilitados."
