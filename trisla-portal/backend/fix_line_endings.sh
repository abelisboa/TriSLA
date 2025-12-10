#!/bin/bash
# Script para corrigir line endings (CRLF → LF) em arquivos Python e Shell
# Essencial para WSL2

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "FIX LINE ENDINGS - TRI-SLA PORTAL BACKEND"
echo "=========================================="
echo ""

# Verificar se dos2unix está disponível
if command -v dos2unix &> /dev/null; then
    echo "Usando dos2unix..."
    
    # Converter todos os arquivos .py
    find src -name "*.py" -type f -exec dos2unix {} \; 2>/dev/null || true
    
    # Converter todos os arquivos .sh
    find . -name "*.sh" -type f -exec dos2unix {} \; 2>/dev/null || true
    
    echo "✅ Line endings corrigidos com dos2unix"
else
    echo "dos2unix não encontrado, usando sed..."
    
    # Converter usando sed (mais lento mas funciona sempre)
    find src -name "*.py" -type f -exec sed -i 's/\r$//' {} \;
    find . -name "*.sh" -type f -exec sed -i 's/\r$//' {} \;
    
    echo "✅ Line endings corrigidos com sed"
fi

echo ""
echo "=========================================="
echo "✅ CONCLUÍDO"
echo "=========================================="
echo ""

