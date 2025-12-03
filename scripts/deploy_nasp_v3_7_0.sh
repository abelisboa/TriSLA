#!/bin/bash
set -e

echo "==============================================="
echo "🚀 TriSLA — Deploy NASP v3.7.0-nasp"
echo "==============================================="

###############################################
# 1. Login no GHCR
###############################################
echo "🔐 Login no GHCR..."
echo $GHCR_TOKEN | docker login ghcr.io -u abelisboa --password-stdin

###############################################
# 2. Namespace
###############################################
echo "📦 Recriando namespace trisla..."
kubectl delete namespace trisla --ignore-not-found=true
kubectl create namespace trisla

###############################################
# 3. Secret GHCR
###############################################
echo "🔐 Criando secret ghcr-secret..."
kubectl create secret docker-registry ghcr-secret \
  --namespace=trisla \
  --docker-server=ghcr.io \
  --docker-username=abelisboa \
  --docker-password="$GHCR_TOKEN" \
  --docker-email="placeholder@example.com"

###############################################
# 4. Limpeza preventiva
###############################################
echo "🧹 Limpando objetos antigos..."
kubectl delete pod --all -n trisla --ignore-not-found=true
kubectl delete deployment --all -n trisla --ignore-not-found=true
kubectl delete svc --all -n trisla --ignore-not-found=true

###############################################
# 5. Atualizar repositório local no node1
###############################################
echo "📥 Atualizando repositório TriSLA..."
cd ~/gtp5g/trisla
git pull

###############################################
# 6. Executar deploy Helm
###############################################
echo "🚀 Iniciando deploy Helm da versão v3.7.0-nasp..."
helm upgrade --install trisla ./helm/trisla \
  -n trisla \
  -f ./helm/trisla/values-nasp.yaml \
  --cleanup-on-fail \
  --debug

###############################################
# 7. Verificação de pods
###############################################
echo "🔍 Verificando pods..."
kubectl get pods -n trisla -o wide

###############################################
# 8. Logs iniciais
###############################################
echo "📝 Logs iniciais do Decision Engine:"
kubectl logs -n trisla -l app=decision-engine --tail=50

echo "📝 Logs iniciais do ML-NSMF:"
kubectl logs -n trisla -l app=ml-nsmf --tail=50

echo "📝 Logs iniciais do SEM-CSMF:"
kubectl logs -n trisla -l app=sem-csmf --tail=50

echo "📝 Logs iniciais do BC-NSSMF:"
kubectl logs -n trisla -l app=bc-nssmf --tail=50

echo "==============================================="
echo "🎉 Deploy concluído — TriSLA v3.7.0-nasp"
echo "==============================================="
