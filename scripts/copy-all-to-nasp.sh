#!/bin/bash
# ============================================
# Script para Copiar Todo o Projeto para o NASP
# ============================================
# Copia projeto completo via ppgca → node006
# ============================================

set -e

PPGCA_HOST="ppgca.unisinos.br"
PPGCA_USER="porvir5g"
NODE1_HOST="node006"
NODE1_USER="porvir5g"
NODE1_PATH="~/gtp5g"

echo "📋 Copiando projeto completo para o NASP..."
echo ""

# Criar arquivo temporário com comandos
cat > /tmp/copy-to-nasp-commands.sh <<'EOF'
#!/bin/bash
# Comandos para executar no ppgca

echo "Copiando para node006..."
scp -r trisla/ porvir5g@node006:~/gtp5g/

echo "✅ Projeto copiado!"
echo ""
echo "Próximos passos:"
echo "  ssh node006"
echo "  cd ~/gtp5g/trisla"
echo "  chmod +x scripts/*.sh"
EOF

chmod +x /tmp/copy-to-nasp-commands.sh

echo "1️⃣ Copiando projeto para ppgca..."
# Criar tarball
tar -czf /tmp/trisla.tar.gz \
    --exclude='TriSLA_PROMPTS' \
    --exclude='.git' \
    --exclude='node_modules' \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    .

scp /tmp/trisla.tar.gz ${PPGCA_USER}@${PPGCA_HOST}:~/
scp /tmp/copy-to-nasp-commands.sh ${PPGCA_USER}@${PPGCA_HOST}:~/

echo "✅ Arquivos copiados para ppgca"
echo ""
echo "2️⃣ Próximos passos no ppgca:"
echo "   ssh ${PPGCA_USER}@${PPGCA_HOST}"
echo "   tar -xzf trisla.tar.gz"
echo "   mv trisla.tar.gz trisla/"
echo "   cd trisla"
echo "   bash copy-to-nasp-commands.sh"
echo ""
echo "3️⃣ Depois no node1:"
echo "   ssh node006"
echo "   cd ~/gtp5g/trisla"
echo "   ./scripts/discover-nasp-endpoints.sh"

