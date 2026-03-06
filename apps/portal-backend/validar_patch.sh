#!/bin/bash
# Script de Validação do PATCH COMPLETO - Backend TriSLA Portal

BACKEND_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$BACKEND_DIR"

echo "============================================================"
echo "  VALIDAÇÃO DO PATCH COMPLETO - Backend TriSLA Portal"
echo "============================================================"
echo ""

# Teste 1: Importação do run.py
echo "[TESTE 1] Validando importação do run.py..."
if python3 -c "import run; print('OK')" 2>/dev/null | grep -q "OK"; then
    echo "  ✅ PASS: run.py pode ser importado"
else
    echo "  ❌ FAIL: run.py não pode ser importado"
    exit 1
fi
echo ""

# Teste 2: Verificar estrutura do run.py
echo "[TESTE 2] Verificando estrutura do run.py..."
if [ -f "run.py" ]; then
    echo "  ✅ PASS: Arquivo run.py existe"
    
    if grep -q "def is_wsl2()" run.py; then
        echo "  ✅ PASS: Função is_wsl2() encontrada"
    else
        echo "  ⚠️  WARN: Função is_wsl2() não encontrada"
    fi
    
    if grep -q "reload_dirs" run.py; then
        echo "  ✅ PASS: reload_dirs configurado"
    else
        echo "  ❌ FAIL: reload_dirs não configurado"
    fi
    
    if grep -q "reload_excludes" run.py; then
        echo "  ✅ PASS: reload_excludes configurado"
    else
        echo "  ❌ FAIL: reload_excludes não configurado"
    fi
else
    echo "  ❌ FAIL: Arquivo run.py não encontrado"
    exit 1
fi
echo ""

# Teste 3: Verificar portal_manager.sh
echo "[TESTE 3] Verificando portal_manager.sh..."
PORTAL_MANAGER="../../scripts/portal_manager.sh"
if [ -f "$PORTAL_MANAGER" ]; then
    echo "  ✅ PASS: portal_manager.sh existe"
    
    if grep -q "is_wsl2()" "$PORTAL_MANAGER"; then
        echo "  ✅ PASS: Função is_wsl2() no portal_manager"
    fi
    
    if grep -q "run.py" "$PORTAL_MANAGER"; then
        echo "  ✅ PASS: portal_manager usa run.py"
    fi
    
    if grep -q "Opção 7" "$PORTAL_MANAGER" || grep -q "PROD" "$PORTAL_MANAGER"; then
        echo "  ✅ PASS: Opção PROD encontrada no menu"
    fi
else
    echo "  ⚠️  WARN: portal_manager.sh não encontrado em $PORTAL_MANAGER"
fi
echo ""

# Teste 4: Verificar configuração CORS
echo "[TESTE 4] Verificando configuração CORS..."
if [ -f "src/main.py" ]; then
    if grep -q "CORSMiddleware" src/main.py; then
        echo "  ✅ PASS: CORSMiddleware configurado"
    else
        echo "  ❌ FAIL: CORSMiddleware não configurado"
    fi
    
    if grep -q "allow_methods" src/main.py; then
        echo "  ✅ PASS: allow_methods configurado"
    fi
else
    echo "  ❌ FAIL: src/main.py não encontrado"
fi
echo ""

# Teste 5: Verificar dependências corrigidas
echo "[TESTE 5] Verificando correção de dependências..."
if [ -f "requirements.txt" ]; then
    if grep -q "opentelemetry-sdk==1.21.0" requirements.txt || grep -q "opentelemetry-sdk>=1.21.0" requirements.txt; then
        echo "  ✅ PASS: Versão do OpenTelemetry SDK ajustada"
    else
        echo "  ⚠️  WARN: Verificar versão do OpenTelemetry SDK"
    fi
    
    if ! grep -q "opentelemetry-sdk==1.22.0" requirements.txt; then
        echo "  ✅ PASS: Versão conflitante 1.22.0 removida"
    fi
else
    echo "  ⚠️  WARN: requirements.txt não encontrado"
fi
echo ""

# Teste 6: Verificar estrutura de diretórios
echo "[TESTE 6] Verificando estrutura de diretórios..."
if [ -d "src" ]; then
    echo "  ✅ PASS: Diretório src/ existe"
else
    echo "  ❌ FAIL: Diretório src/ não encontrado"
fi

if [ -d "venv" ]; then
    echo "  ✅ PASS: Ambiente virtual existe"
else
    echo "  ⚠️  WARN: Ambiente virtual não encontrado (execute: python3 -m venv venv)"
fi
echo ""

echo "============================================================"
echo "  RESUMO DA VALIDAÇÃO"
echo "============================================================"
echo ""
echo "✅ Arquivos principais verificados:"
echo "   - run.py"
echo "   - portal_manager.sh"
echo "   - src/main.py"
echo "   - requirements.txt"
echo ""
echo "📋 Próximos passos:"
echo "   1. Instalar dependências: bash instalar_dependencias.sh"
echo "   2. Testar execução: python3 run.py"
echo "   3. Testar portal manager: bash ../../scripts/portal_manager.sh"
echo ""
echo "============================================================"

