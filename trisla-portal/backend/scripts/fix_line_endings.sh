#!/bin/bash
# Script para corrigir terminações de linha em scripts shell
# Converte CRLF (Windows) para LF (Unix)

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$BACKEND_DIR"

echo "Corrigindo terminações de linha em scripts shell..."

# Lista de scripts para corrigir
SCRIPTS=(
    "scripts/rebuild_venv.sh"
    "scripts/validar_instalacao.sh"
    "scripts/fix_line_endings.sh"
)

for script in "${SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        # Remove CR (carriage return) e garante LF
        sed -i 's/\r$//' "$script"
        chmod +x "$script"
        echo "✅ $script corrigido"
    fi
done

echo "✅ Correção concluída!"

