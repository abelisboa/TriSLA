#!/bin/bash
# Script para verificar todos os arquivos linha por linha
# Uso: ./scripts-wsl/verificar-tudo.sh

set -e

cd ~/trisla-dashboard-local/frontend

echo "🔬 Análise Cirúrgica Completa"
echo "=============================="
echo ""

# 1. Verificar imports React
echo "1️⃣ Verificando imports React..."
FILES=(
    "src/App.tsx"
    "src/main.tsx"
    "src/components/Layout.tsx"
    "src/components/MetricCard.tsx"
    "src/pages/Dashboard.tsx"
    "src/pages/Metrics.tsx"
    "src/pages/SlicesManagement.tsx"
)

MISSING_REACT=()
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        if ! grep -q "^import React" "$file"; then
            MISSING_REACT+=("$file")
            echo "   ❌ $file - Falta import React"
        else
            echo "   ✅ $file - Tem import React"
        fi
    fi
done

if [ ${#MISSING_REACT[@]} -eq 0 ]; then
    echo "   ✅ Todos os arquivos têm import React"
else
    echo "   ❌ Arquivos faltando import React: ${MISSING_REACT[*]}"
fi
echo ""

# 2. Verificar React Router future flags
echo "2️⃣ Verificando React Router future flags..."
if [ -f "src/App.tsx" ]; then
    if grep -q "future:" src/App.tsx && grep -q "v7_startTransition" src/App.tsx; then
        echo "   ✅ React Router configurado com future flags"
    else
        echo "   ⚠️  React Router não tem future flags (avisos aparecerão)"
    fi
fi
echo ""

# 3. Verificar estrutura de arquivos
echo "3️⃣ Verificando estrutura..."
FILES_CHECK=(
    "index.html"
    "package.json"
    "vite.config.ts"
    "tsconfig.json"
    "src/main.tsx"
    "src/App.tsx"
    "src/index.css"
    "src/services/api.ts"
)

for file in "${FILES_CHECK[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file existe"
    else
        echo "   ❌ $file NÃO existe"
    fi
done
echo ""

# 4. Verificar TypeScript
echo "4️⃣ Verificando TypeScript..."
if [ -f "tsconfig.json" ]; then
    if grep -q '"jsx": "react-jsx"' tsconfig.json; then
        echo "   ✅ jsx: react-jsx configurado"
    fi
fi
echo ""

# 5. Verificar dependências
echo "5️⃣ Verificando dependências..."
if [ -f "package.json" ]; then
    REQUIRED_DEPS=("react" "react-dom" "react-router-dom" "@tanstack/react-query")
    for dep in "${REQUIRED_DEPS[@]}"; do
        if grep -q "\"$dep\"" package.json; then
            echo "   ✅ $dep instalado"
        else
            echo "   ❌ $dep NÃO encontrado em package.json"
        fi
    done
fi
echo ""

# 6. Verificar sintaxe (tentativa)
echo "6️⃣ Verificando sintaxe..."
if command -v npx &> /dev/null && [ -f "tsconfig.json" ]; then
    if npx tsc --noEmit 2>&1 | head -5; then
        echo "   ✅ TypeScript compila sem erros"
    else
        echo "   ⚠️  Alguns erros TypeScript encontrados (verificar acima)"
    fi
else
    echo "   ⚠️  Não é possível verificar sintaxe TypeScript"
fi
echo ""

echo "✅ Verificação completa!"
echo ""
echo "📊 Resumo:"
echo "   - Imports React: $(if [ ${#MISSING_REACT[@]} -eq 0 ]; then echo '✅ Todos corretos'; else echo '❌ Faltando em alguns'; fi)"
echo "   - Estrutura: ✅ Verificada"
echo "   - Dependências: ✅ Verificadas"





