#!/bin/bash
# Script para listar e verificar arquivos necessários no WSL
# Uso: ./scripts-wsl/list-files-to-copy.sh

echo "📋 Verificando arquivos necessários..."
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_DIR"

# Arquivos de documentação
DOCS=(
    "GUIA_MIGRACAO_WSL.md"
    "INICIO_RAPIDO_WSL.md"
    "README_WSL.md"
    "ANALISE_WINDOWS_VS_LINUX_WSL.md"
)

echo "📚 Arquivos de documentação:"
for doc in "${DOCS[@]}"; do
    if [ -f "$doc" ]; then
        echo "   ✅ $doc"
    else
        echo "   ❌ $doc (NÃO ENCONTRADO)"
    fi
done
echo ""

# Scripts
echo "🔧 Scripts WSL:"
if [ -d "scripts-wsl" ]; then
    for script in scripts-wsl/*.sh; do
        if [ -f "$script" ]; then
            if [ -x "$script" ]; then
                echo "   ✅ $(basename $script) (executável)"
            else
                echo "   ⚠️  $(basename $script) (não executável)"
            fi
        fi
    done
else
    echo "   ❌ Diretório scripts-wsl não encontrado"
fi
echo ""

# Diretórios principais
echo "📁 Diretórios principais:"
for dir in backend frontend; do
    if [ -d "$dir" ]; then
        echo "   ✅ $dir/"
    else
        echo "   ❌ $dir/ (NÃO ENCONTRADO)"
    fi
done
echo ""

# Arquivos principais
echo "📄 Arquivos principais:"
MAIN_FILES=(
    "backend/main.py"
    "backend/requirements.txt"
    "frontend/package.json"
)
for file in "${MAIN_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file (NÃO ENCONTRADO)"
    fi
done





