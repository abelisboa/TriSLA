#!/bin/bash

echo "🔧 Atualizando deployment com correção do uvicorn..."

# Conectar ao node1 e executar comandos
ssh porvir5g@node1 << 'EOF'
echo "📋 Status atual..."
kubectl get pods -n trisla

echo "🗑️ Removendo deployment atual..."
helm uninstall trisla-portal -n trisla --wait

echo "🧹 Limpando recursos..."
kubectl delete all -n trisla --all --ignore-not-found

echo "📦 Reinstalando com correção..."
cd ~/gtp5g/trisla-portal
helm install trisla-portal ./helm/trisla-portal/ \
  -n trisla \
  --create-namespace \
  --wait \
  --timeout=10m

echo "✅ Verificando status..."
kubectl get pods -n trisla
kubectl get services -n trisla

echo "📊 Verificando logs do API..."
kubectl logs -n trisla -l app=trisla-portal -c trisla-api
EOF

echo "🎉 Atualização concluída!"


