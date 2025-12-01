#!/usr/bin/env bash
set -euo pipefail

echo "=============================================="
echo "🔧 FIX TRISLA — CD DEFINITIVO (NASP)"
echo "=============================================="

NAMESPACE="trisla"

echo "➡️ Removendo pods antigos..."
kubectl delete pod -n ${NAMESPACE} --all || true

echo "➡️ Recriando secret GHCR..."
kubectl delete secret ghcr-secret -n ${NAMESPACE} --ignore-not-found

kubectl create secret docker-registry ghcr-secret \
  -n ${NAMESPACE} \
  --docker-server=ghcr.io \
  --docker-username=abelisboa \
  --docker-password="${GHCR_PAT}" \
  --docker-email="dev@trisla.io"

echo "➡️ Rodando helm upgrade..."
helm upgrade --install trisla ./helm/trisla \
  -n ${NAMESPACE} \
  -f ./helm/trisla/values-nasp.yaml \
  --cleanup-on-fail

echo "➡️ Aguardando subidas..."
kubectl get pods -n ${NAMESPACE} -o wide
echo "=============================================="
echo "🎉 CORREÇÃO FINALIZADA — CD ESTÁVEL!"
echo "=============================================="
