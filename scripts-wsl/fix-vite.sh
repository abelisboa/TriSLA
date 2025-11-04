#!/bin/bash
# Script para corrigir problemas do Vite
# Uso: ./scripts-wsl/fix-vite.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🔧 Corrigindo configuração do Vite..."
echo ""

cd "$PROJECT_DIR/frontend"

# Verificar se index.html existe
if [ ! -f "index.html" ]; then
    echo "❌ index.html não encontrado em frontend/"
    echo "   Criando index.html..."
    cat > index.html << 'EOF'
<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale-width=1.0" />
    <title>TriSLA Dashboard</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
EOF
    echo "   ✅ index.html criado"
else
    echo "   ✅ index.html existe"
fi

# Verificar se src/main.tsx existe
if [ ! -f "src/main.tsx" ]; then
    echo "❌ src/main.tsx não encontrado"
    exit 1
else
    echo "   ✅ src/main.tsx existe"
fi

# Limpar processos antigos do Vite
echo ""
echo "🧹 Limpando processos antigos..."
pkill -f vite 2>/dev/null || true
sleep 2

echo ""
echo "✅ Correções aplicadas!"
echo ""
echo "Agora execute: ./scripts-wsl/start-frontend.sh"





