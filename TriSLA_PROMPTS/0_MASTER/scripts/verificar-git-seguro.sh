#!/bin/bash
# ============================================
# Script de Verificação Git Seguro
# ============================================
# Verifica se há arquivos sensíveis antes de fazer push
# ============================================

set -e

echo "🔍 Verificando segurança antes do push..."
echo ""

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRO=0

# 1. Verificar se TriSLA_PROMPTS está sendo commitado
echo "1️⃣ Verificando se TriSLA_PROMPTS está no staging..."
if git ls-files --cached | grep -q "TriSLA_PROMPTS"; then
    echo -e "${RED}❌ ERRO: TriSLA_PROMPTS/ está sendo commitado!${NC}"
    echo "   Execute: git rm -r --cached TriSLA_PROMPTS/"
    ERRO=1
else
    echo -e "${GREEN}✅ OK: TriSLA_PROMPTS/ não está no staging${NC}"
fi
echo ""

# 2. Verificar se há secrets no código
echo "2️⃣ Verificando por possíveis secrets..."
SECRETS=$(git diff --cached | grep -iE "password|secret|key|token|api_key|private_key" | grep -v "example\|template\|test" || true)
if [ -n "$SECRETS" ]; then
    echo -e "${RED}❌ ERRO: Possíveis secrets encontrados no código:${NC}"
    echo "$SECRETS" | head -5
    echo -e "${YELLOW}⚠️  Revise antes de fazer commit!${NC}"
    ERRO=1
else
    echo -e "${GREEN}✅ OK: Nenhum secret óbvio encontrado${NC}"
fi
echo ""

# 3. Verificar arquivos .env
echo "3️⃣ Verificando arquivos .env..."
if git ls-files --cached | grep -q "\.env$"; then
    echo -e "${RED}❌ ERRO: Arquivos .env estão sendo commitados!${NC}"
    echo "   Adicione .env ao .gitignore"
    ERRO=1
else
    echo -e "${GREEN}✅ OK: Nenhum .env no staging${NC}"
fi
echo ""

# 4. Verificar chaves privadas
echo "4️⃣ Verificando chaves privadas..."
if git ls-files --cached | grep -qE "\.(key|pem|p12|pfx)$"; then
    echo -e "${RED}❌ ERRO: Chaves privadas estão sendo commitadas!${NC}"
    ERRO=1
else
    echo -e "${GREEN}✅ OK: Nenhuma chave privada no staging${NC}"
fi
echo ""

# 5. Verificar inventories locais
echo "5️⃣ Verificando inventories locais..."
if git ls-files --cached | grep -qE "inventory.*\.local|inventory\.local"; then
    echo -e "${RED}❌ ERRO: Inventories locais estão sendo commitados!${NC}"
    ERRO=1
else
    echo -e "${GREEN}✅ OK: Nenhum inventory local no staging${NC}"
fi
echo ""

# 6. Verificar valores de produção
echo "6️⃣ Verificando values.yaml com dados reais..."
if git diff --cached --name-only | grep -qE "values.*\.(yaml|yml)$"; then
    VALUES_FILES=$(git diff --cached --name-only | grep -E "values.*\.(yaml|yml)$")
    for file in $VALUES_FILES; do
        if git diff --cached "$file" | grep -qE "192\.168\.|10\.|password|secret" && ! git diff --cached "$file" | grep -q "example\|template"; then
            echo -e "${RED}❌ ERRO: $file pode conter dados reais!${NC}"
            ERRO=1
        fi
    done
    if [ $ERRO -eq 0 ]; then
        echo -e "${GREEN}✅ OK: Values files parecem seguros${NC}"
    fi
else
    echo -e "${GREEN}✅ OK: Nenhum values.yaml no staging${NC}"
fi
echo ""

# 7. Resumo
echo "=========================================="
if [ $ERRO -eq 0 ]; then
    echo -e "${GREEN}✅ Verificação concluída: Tudo seguro para commit!${NC}"
    exit 0
else
    echo -e "${RED}❌ Verificação falhou: Corrija os erros antes de fazer commit!${NC}"
    exit 1
fi

