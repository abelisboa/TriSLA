#!/bin/bash
# ============================================
# Script para Copiar Arquivos para o NASP
# ============================================
# Copia arquivos via ppgca.unisinos.br → node006
# ============================================

set -e

PPGCA_HOST="ppgca.unisinos.br"
PPGCA_USER="porvir5g"
NODE1_HOST="node006"
NODE1_USER="porvir5g"
NODE1_PATH="~/gtp5g"

echo "📋 Copiando arquivos para o NASP..."
echo ""
echo "Caminho: Local → ppgca.unisinos.br → node006 (node1)"
echo ""

# Arquivo a copiar
FILE="${1:-scripts/discover-nasp-endpoints.sh}"

if [ ! -f "$FILE" ]; then
    echo "❌ Arquivo não encontrado: $FILE"
    exit 1
fi

echo "📁 Arquivo: $FILE"
echo ""

# Opção 1: Copiar via ppgca (2 etapas)
echo "1️⃣ Copiando para ppgca primeiro..."
scp "$FILE" ${PPGCA_USER}@${PPGCA_HOST}:~/

if [ $? -eq 0 ]; then
    echo "✅ Arquivo copiado para ppgca"
    echo ""
    echo "2️⃣ Próximos passos:"
    echo "   ssh ${PPGCA_USER}@${PPGCA_HOST}"
    echo "   scp $(basename $FILE) ${NODE1_USER}@${NODE1_HOST}:${NODE1_PATH}/"
    echo "   ssh ${NODE1_HOST}"
    echo "   cd ${NODE1_PATH}"
    echo "   chmod +x $(basename $FILE)"
    echo "   ./$(basename $FILE)"
else
    echo "❌ Erro ao copiar para ppgca"
    exit 1
fi

echo ""
echo "✅ Processo iniciado!"

