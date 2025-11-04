#!/bin/bash
# Script para adicionar import React em todos os arquivos que usam JSX
# Uso: ./scripts-wsl/fix-all-react-imports.sh

cd ~/trisla-dashboard-local/frontend

echo "🔧 Adicionando import React em todos os arquivos..."
echo ""

# Lista de arquivos que precisam de React
FILES=(
    "src/App.tsx"
    "src/components/Layout.tsx"
    "src/components/MetricCard.tsx"
    "src/pages/Dashboard.tsx"
    "src/pages/Metrics.tsx"
    "src/pages/SlicesManagement.tsx"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        # Verificar se já tem import React
        if ! grep -q "^import React" "$file"; then
            echo "   ✅ Adicionando import React em $file"
            # Adicionar import React no início (após primeira linha vazia se houver)
            sed -i '1i import React from '\''react'\''' "$file"
        else
            echo "   ⏭️  $file já tem import React"
        fi
    else
        echo "   ⚠️  $file não encontrado"
    fi
done

echo ""
echo "✅ Correções aplicadas!"
echo ""
echo "🔄 Reinicie o Vite:"
echo "   pkill -f vite"
echo "   npm run dev"





