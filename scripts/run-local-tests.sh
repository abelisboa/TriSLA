#!/bin/bash
# ============================================
# Script: Executar Testes Locais do TriSLA
# ============================================
# Executa testes automatizados que podem ser feitos localmente
# ============================================

set -e

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$BASE_DIR"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     TriSLA - Executar Testes Locais                       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Verificar se pytest está instalado
if ! command -v pytest >/dev/null 2>&1; then
    echo "❌ pytest não está instalado"
    echo "   Instale com: pip install pytest pytest-asyncio httpx"
    exit 1
fi

# Executar testes unitários
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 Executando Testes Unitários"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ -d "tests/unit" ]; then
    pytest tests/unit/ -v --tb=short
else
    echo "⚠️  Diretório de testes unitários não encontrado"
fi

echo ""

# Executar testes de integração
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔗 Executando Testes de Integração"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ -d "tests/integration" ]; then
    pytest tests/integration/ -v --tb=short || echo "⚠️  Alguns testes de integração falharam (pode ser esperado se serviços não estiverem rodando)"
else
    echo "⚠️  Diretório de testes de integração não encontrado"
fi

echo ""

# Executar testes E2E (se disponíveis)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 Executando Testes End-to-End"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ -d "tests/e2e" ]; then
    pytest tests/e2e/ -v --tb=short || echo "⚠️  Alguns testes E2E falharam (pode ser esperado se serviços não estiverem rodando)"
else
    echo "⚠️  Diretório de testes E2E não encontrado"
fi

echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Testes Concluídos"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

