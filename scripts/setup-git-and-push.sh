#!/bin/bash
# ============================================
# Script Completo: Setup Git + Push
# ============================================
# Inicializa Git, adiciona arquivos e faz push
# ============================================

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

GITHUB_REPO="abelisboa/TriSLA"
GITHUB_URL="https://github.com/${GITHUB_REPO}.git"

echo -e "${GREEN}🚀 Setup completo do Git e Push para GitHub...${NC}"
echo ""

# 1. Inicializar Git (se necessário)
if [ ! -d ".git" ]; then
    echo -e "${YELLOW}📁 Inicializando Git...${NC}"
    git init
    git branch -M main
    git remote add origin "$GITHUB_URL" 2>/dev/null || {
        git remote set-url origin "$GITHUB_URL"
    }
    echo -e "${GREEN}✅ Git inicializado${NC}"
else
    echo -e "${GREEN}✅ Git já inicializado${NC}"
    # Atualizar remote
    git remote set-url origin "$GITHUB_URL" 2>/dev/null || {
        git remote add origin "$GITHUB_URL"
    }
fi
echo ""

# 2. Verificar .gitignore
if [ ! -f ".gitignore" ]; then
    echo -e "${RED}❌ Erro: .gitignore não encontrado${NC}"
    exit 1
fi
echo -e "${GREEN}✅ .gitignore encontrado${NC}"
echo ""

# 3. Verificar o que será commitado
echo -e "${YELLOW}📋 Arquivos que serão adicionados:${NC}"
git status --short | head -20
echo ""

# 4. Adicionar arquivos
echo -e "${YELLOW}➕ Adicionando arquivos...${NC}"
git add .
echo -e "${GREEN}✅ Arquivos adicionados${NC}"
echo ""

# 5. Verificar se há mudanças para commit
if git diff --staged --quiet; then
    echo -e "${YELLOW}⚠️  Nenhuma mudança para commitar${NC}"
    echo "   Verificando se já existe commit..."
    if git rev-parse --verify HEAD >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Já existe commit${NC}"
    else
        echo -e "${RED}❌ Nenhum commit encontrado${NC}"
        exit 1
    fi
else
    # 6. Fazer commit
    echo -e "${YELLOW}💾 Fazendo commit...${NC}"
    COMMIT_MSG="🚀 TriSLA: Arquitetura completa para garantia de SLA em redes 5G/O-RAN

✨ Funcionalidades:
- Módulos completos (SEM-CSMF, ML-NSMF, Decision Engine, BC-NSSMF, SLA-Agent Layer)
- Integração real com NASP (RAN, Transport, Core)
- UI Dashboard responsivo e moderno
- Observabilidade completa (OTLP, Prometheus, Grafana)
- CI/CD automatizado (GitHub Actions)
- Helm charts para deploy em produção
- Testes unitários, integração e E2E

🔧 Configuração:
- Valores reais do NASP configurados
- Endpoints dos controladores descobertos
- Scripts de build, deploy e validação
- Documentação completa de deploy

📦 Deploy:
- Pronto para produção real
- Não usa simulação
- Executa ações reais no NASP"
    
    git commit -m "$COMMIT_MSG"
    echo -e "${GREEN}✅ Commit realizado${NC}"
    echo ""
fi

# 7. Verificar se precisa fazer push
echo -e "${YELLOW}🔍 Verificando status do push...${NC}"
LOCAL=$(git rev-parse @ 2>/dev/null || echo "")
REMOTE=$(git rev-parse @{u} 2>/dev/null || echo "")

if [ -z "$LOCAL" ]; then
    echo -e "${RED}❌ Erro: Nenhum commit local encontrado${NC}"
    exit 1
fi

if [ -z "$REMOTE" ]; then
    echo -e "${YELLOW}📤 Fazendo push inicial...${NC}"
    git push -u origin main || {
        echo -e "${YELLOW}⚠️  Push falhou. Tentando com force (se o repositório remoto estiver vazio)...${NC}"
        read -p "Deseja fazer force push? (s/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Ss]$ ]]; then
            git push -u origin main --force
        else
            echo -e "${YELLOW}⚠️  Push cancelado. Execute manualmente: git push -u origin main${NC}"
            exit 1
        fi
    }
elif [ "$LOCAL" != "$REMOTE" ]; then
    echo -e "${YELLOW}📤 Fazendo push...${NC}"
    git push origin main || {
        echo -e "${RED}❌ Push falhou. Verifique se tem permissão e se o repositório existe${NC}"
        exit 1
    }
else
    echo -e "${GREEN}✅ Já está atualizado com o remoto${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Setup completo!${NC}"
echo ""
echo "📋 Próximos passos:"
echo "   1. Verificar no GitHub: https://github.com/$GITHUB_REPO"
echo "   2. Acompanhar build: https://github.com/$GITHUB_REPO/actions"
echo "   3. Verificar imagens: https://github.com/$GITHUB_REPO/pkgs/container"
echo ""

