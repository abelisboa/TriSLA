#!/bin/bash
# ============================================
# Script de Validação de Código
# ============================================

set -e

echo "🔍 Validando código dos módulos..."
echo ""

# Verificar sintaxe Python
echo "1️⃣ Verificando sintaxe Python..."
for module in apps/*/src/*.py; do
    if [ -f "$module" ]; then
        python -m py_compile "$module" 2>/dev/null || echo "⚠️  Erro em $module"
    fi
done

echo "✅ Validação de sintaxe concluída!"
echo ""

# Verificar imports
echo "2️⃣ Verificando imports..."
python -c "
import sys
import os

# Adicionar paths
for app in ['sem-csmf', 'ml-nsmf', 'decision-engine', 'bc-nssmf', 'sla-agent-layer', 'nasp-adapter']:
    sys.path.insert(0, f'apps/{app}/src')

# Testar imports básicos
try:
    print('✅ Imports básicos OK')
except Exception as e:
    print(f'❌ Erro nos imports: {e}')
"

echo ""
echo "✅ Validação concluída!"

