#!/bin/bash
# ============================================
# Quick Git Setup - Executar no WSL
# ============================================

set -e

GITHUB_REPO="abelisboa/TriSLA"
GITHUB_URL="https://github.com/${GITHUB_REPO}.git"

echo "🚀 Quick Git Setup"
echo ""

# 1. Inicializar
if [ ! -d ".git" ]; then
    echo "📁 Inicializando Git..."
    git init
    git branch -M main
    echo "✅ Git inicializado"
else
    echo "✅ Git já inicializado"
fi

# 2. Remote
git remote remove origin 2>/dev/null || true
git remote add origin "$GITHUB_URL"
echo "✅ Remote configurado: $GITHUB_URL"

# 3. Status
echo ""
echo "📋 Status:"
git status --short | head -10

# 4. Add
echo ""
echo "➕ Adicionando arquivos..."
git add .

# 5. Commit
echo ""
echo "💾 Fazendo commit..."
git commit -m "🚀 TriSLA: Arquitetura completa para garantia de SLA em redes 5G/O-RAN

✨ Módulos completos, integração real com NASP, UI Dashboard, observabilidade completa, CI/CD automatizado, pronto para produção real" || {
    echo "⚠️  Nenhuma mudança para commitar ou commit já existe"
}

# 6. Push
echo ""
echo "📤 Fazendo push..."
echo "⚠️  Se pedir autenticação:"
echo "   Usuário: seu_usuario_github"
echo "   Senha: seu_personal_access_token"
echo "   (Criar token em: https://github.com/settings/tokens)"
echo ""

git push -u origin main --force 2>&1 || {
    echo ""
    echo "⚠️  Push falhou. Tentando pull primeiro..."
    git pull origin main --allow-unrelated-histories || true
    git push -u origin main
}

echo ""
echo "✅ Concluído!"
echo "🔗 Verificar: https://github.com/$GITHUB_REPO"

