#!/bin/bash

echo "🔧 Corrigindo deployment do TriSLA Portal..."

# Conectar ao node1 e executar comandos
ssh porvir5g@node1 << 'EOF'
echo "📋 Status atual do Helm..."
helm list -n trisla

echo "🗑️ Removendo release problemática..."
helm uninstall trisla-portal -n trisla --wait

echo "🧹 Limpando recursos órfãos..."
kubectl delete all -n trisla --all --ignore-not-found

echo "📦 Reinstalando com configuração corrigida..."
cd ~/gtp5g/trisla-portal
helm install trisla-portal ./helm/trisla-portal/ \
  -n trisla \
  --create-namespace \
  --wait \
  --timeout=10m

echo "✅ Verificando status da instalação..."
kubectl get pods -n trisla
kubectl get services -n trisla
kubectl get deployments -n trisla

echo "📊 Status do Helm..."
helm status trisla-portal -n trisla
EOF

echo "🎉 Correção concluída!"


