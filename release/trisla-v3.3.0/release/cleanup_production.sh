#!/bin/bash
# TriSLA - Script de Limpeza para Produção
# Remove arquivos e diretórios não essenciais para produção

set -e

DRY_RUN=false
FORCE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        *)
            echo "Uso: $0 [--dry-run] [--force]"
            exit 1
            ;;
    esac
done

echo "=============================================================="
echo "🧹 TriSLA - Limpeza para Produção"
echo "=============================================================="

if [ "$DRY_RUN" = true ]; then
    echo ""
    echo "⚠️  MODO DRY-RUN - Nenhum arquivo será removido"
fi

# Lista de itens para remover
declare -a items=(
    "trisla_dissertacao_completo"
    "trisla_dissertacao_completo.tar.gz"
    "STATE"
    "kube-prometheus-stack"
    "EXECUTION_GUIDE.md"
    "INSTALLATION_NOTES.md"
    "README_MONITORING_SETUP.md"
    "ansible/logs"
    "scripts"
)

echo ""
echo "📋 Itens identificados para remoção:"
echo "--------------------------------------------------------------"

total_size=0
items_found=0

for item in "${items[@]}"; do
    if [ -e "$item" ]; then
        if [ -d "$item" ]; then
            size=$(du -sm "$item" 2>/dev/null | cut -f1 || echo "0")
            type="Directory"
        else
            size=$(du -sm "$item" 2>/dev/null | cut -f1 || echo "0")
            type="File"
        fi
        
        total_size=$((total_size + size))
        items_found=$((items_found + 1))
        
        echo "  ❌ $item"
        echo "     Tipo: $type | Tamanho: ${size} MB"
        echo ""
    fi
done

echo "--------------------------------------------------------------"
echo "📊 Total a ser liberado: ${total_size} MB"
echo "--------------------------------------------------------------"

if [ $items_found -eq 0 ]; then
    echo ""
    echo "✅ Nenhum item para remover encontrado."
    exit 0
fi

if [ "$FORCE" = false ] && [ "$DRY_RUN" = false ]; then
    read -p "⚠️  Deseja continuar com a remoção? (S/N): " confirmation
    if [ "$confirmation" != "S" ] && [ "$confirmation" != "s" ]; then
        echo ""
        echo "❌ Operação cancelada pelo usuário."
        exit 0
    fi
fi

echo ""
echo "🧹 Iniciando limpeza..."

for item in "${items[@]}"; do
    if [ -e "$item" ]; then
        if [ "$DRY_RUN" = true ]; then
            echo "  [DRY-RUN] Removeria: $item"
        else
            rm -rf "$item"
            echo "  ✅ Removido: $item"
        fi
    fi
done

if [ "$DRY_RUN" = true ]; then
    echo ""
    echo "✅ Modo DRY-RUN concluído. Execute sem --dry-run para remover."
else
    echo ""
    echo "✅ Limpeza concluída!"
    echo "📊 Espaço liberado: ~${total_size} MB"
fi

echo "=============================================================="


