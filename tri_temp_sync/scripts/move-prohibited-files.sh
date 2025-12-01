#!/bin/bash
# ============================================
# Script: Move Prohibited Files from Root
# ============================================
# Move automaticamente arquivos proibidos da raiz para pastas corretas
# ============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Move Prohibited Files - TriSLA                         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Verificar se está no diretório correto
if [ ! -f "README.md" ] || [ ! -d "helm" ] || [ ! -d "scripts" ]; then
    echo -e "${RED}❌ Erro: Execute este script no diretório raiz do projeto TriSLA${NC}"
    echo "   No node1 do NASP: cd ~/gtp5g/trisla"
    echo "   Localmente: cd /caminho/para/TriSLA-clean"
    exit 1
fi

# Criar diretórios se não existirem
mkdir -p docs/reports
mkdir -p configs

MOVED_COUNT=0
SKIPPED_COUNT=0

# Lista de arquivos a mover
declare -A FILES_TO_MOVE=(
    ["AUDIT_REPORT_COMPLETE.md"]="docs/reports/"
    ["DEVOPS_AUDIT_REPORT.md"]="docs/reports/"
    ["GITHUB_SAFETY_REPORT.md"]="docs/reports/"
    ["RELEASE_CHECKLIST_v3.5.0.md"]="docs/reports/"
    ["RELEASE_RENAME_REPORT.md"]="docs/reports/"
    ["RELEASE_v3.5.0_SUMMARY.md"]="docs/reports/"
    ["VALIDATION_REPORT_FINAL.md"]="docs/reports/"
    ["ROOT_PROTECTION_REPORT.md"]="docs/reports/"
    ["PUSH_COMPLETO_SUCESSO.md"]="docs/reports/"
    ["PUSH_LOCAL_WINDOWS.md"]="docs/reports/"
    ["PUSH_TO_GITHUB_v3.5.0.md"]="docs/reports/"
    ["RELEASE_COMMANDS_v3.5.0.md"]="docs/reports/"
    ["docker-compose.yml"]="configs/"
)

echo -e "${YELLOW}🔍 Movendo arquivos proibidos da raiz...${NC}"
echo ""

for file in "${!FILES_TO_MOVE[@]}"; do
    dest="${FILES_TO_MOVE[$file]}"
    
    if [ -f "$file" ]; then
        # Verificar se já existe no destino
        if [ -f "$dest$file" ]; then
            echo -e "${YELLOW}⚠️  $file já existe em $dest (pulando)${NC}"
            SKIPPED_COUNT=$((SKIPPED_COUNT + 1))
        else
            echo -e "${GREEN}📦 Movendo $file → $dest${NC}"
            mv "$file" "$dest"
            MOVED_COUNT=$((MOVED_COUNT + 1))
        fi
    else
        echo -e "${YELLOW}⏭️  $file não encontrado (pulando)${NC}"
        SKIPPED_COUNT=$((SKIPPED_COUNT + 1))
    fi
done

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Relatório Final${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}✅ Arquivos movidos: $MOVED_COUNT${NC}"
echo -e "${YELLOW}⏭️  Arquivos pulados: $SKIPPED_COUNT${NC}"
echo ""

if [ $MOVED_COUNT -gt 0 ]; then
    echo -e "${GREEN}✅ Operação concluída com sucesso!${NC}"
    echo ""
    echo -e "${YELLOW}📋 Próximos passos:${NC}"
    echo "   1. Verificar estrutura: ./scripts/enforce-clean-root.sh"
    echo "   2. Commit das mudanças"
    echo "   3. Push para GitHub"
else
    echo -e "${YELLOW}⚠️  Nenhum arquivo foi movido (todos já estão nos locais corretos ou não existem)${NC}"
fi

echo ""

