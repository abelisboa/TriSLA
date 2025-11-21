#!/bin/bash
# ============================================
# Script de Rollback - TriSLA
# ============================================

set -e

RELEASE_NAME="trisla"
NAMESPACE="trisla"

echo "🔄 Iniciando rollback do TriSLA..."

# 1. Verificar histórico do Helm
echo "1️⃣ Verificando histórico do Helm..."
helm history $RELEASE_NAME -n $NAMESPACE

# 2. Rollback para versão anterior
echo "2️⃣ Executando rollback..."
read -p "Rollback para qual revisão? (ou Enter para última): " REVISION

if [ -z "$REVISION" ]; then
    helm rollback $RELEASE_NAME -n $NAMESPACE
else
    helm rollback $RELEASE_NAME $REVISION -n $NAMESPACE
fi

# 3. Aguardar rollback
echo "3️⃣ Aguardando rollback..."
sleep 30

# 4. Verificar status
echo "4️⃣ Verificando status..."
kubectl get pods -n $NAMESPACE

echo "✅ Rollback concluído!"

