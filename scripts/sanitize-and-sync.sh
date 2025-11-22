#!/bin/bash
# ============================================
# Script de Sanitização e Sincronização Final
# ============================================

set -e

echo "=== TRI-SLA CLEAN: SANITIZAÇÃO E SINCRONIZAÇÃO FINAL ==="
echo ""

# 1. Atualizar o repositório com o último estado do GitHub
echo "1. Atualizando repositório com último estado do GitHub..."
git pull origin main --rebase || echo "⚠️  Pull falhou ou não há mudanças remotas"
echo ""

# 2. Garantir .gitignore correto
echo "2. Atualizando .gitignore..."
cat << 'EOF' > .gitignore
# === Python virtual environments ===
.venv/
*/.venv/

# === Python caches ===
__pycache__/
*.pyc

# === Dados locais ===
*.db
*.sqlite
*.jsonld
*.owl
*.ttl

# === Pastas que NUNCA devem ir para o GitHub ===
PROMPTS_*/
PROMPTS_EXPORT/
PROMPTS_V3/
TriSLA_PROMPTS_REORG/
TriSLA-Prompts*/
cleanup*/
audit*/
RELATORIO*/
docs/*INTERNAL*
scripts/.venv/
src/**/__pycache__/

# === Testes e cargas ===
tests/load/*.json

# === IDE ===
.vscode/
.idea/
EOF
echo "[OK] .gitignore atualizado"
echo ""

# 3. Remover do Git qualquer pasta proibida que ainda esteja versionada
echo "3. Removendo pastas proibidas do Git (se existirem)..."
git rm -r --cached PROMPTS_EXPORT/ 2>/dev/null || true
git rm -r --cached PROMPTS_V3/ 2>/dev/null || true
git rm -r --cached TriSLA_PROMPTS_REORG/ 2>/dev/null || true
git rm -r --cached TriSLA-Prompts*/ 2>/dev/null || true
echo "[OK] Pastas proibidas removidas do cache do Git"
echo ""

# 4. Garantir que arquivos sensíveis não subam
echo "4. Removendo arquivos sensíveis do Git (se existirem)..."
git rm --cached *.db 2>/dev/null || true
git rm --cached *.jsonld 2>/dev/null || true
git rm --cached *.owl 2>/dev/null || true
echo "[OK] Arquivos sensíveis removidos do cache do Git"
echo ""

# 5. Adicionar apenas arquivos oficiais do repositório
echo "5. Adicionando apenas arquivos oficiais do repositório..."
git add apps/ proto/ monitoring/ docker-compose.yml docker-compose.production.yml docker-compose.alternative.yml README.md docs/*.md .gitignore 2>/dev/null || true
git add helm/ ansible/ scripts/ tests/ 2>/dev/null || true
echo "[OK] Arquivos oficiais adicionados"
echo ""

# 6. Verificar status antes do commit
echo "6. Verificando status antes do commit..."
git status --short | head -20
echo ""

# 7. Commit claro e limpo (se houver mudanças)
echo "7. Criando commit de sanitização..."
if git diff --cached --quiet; then
    echo "⚠️  Nenhuma mudança para commitar"
else
    git commit -m "Sanitização final: remoção de arquivos privados + sync TriSLA-clean"
    echo "[OK] Commit criado"
fi
echo ""

# 8. Enviar mudanças para o GitHub
echo "8. Enviando mudanças para o GitHub..."
if git log origin/main..HEAD --oneline | grep -q .; then
    git push origin main
    echo "[OK] Push concluído"
else
    echo "⚠️  Nenhuma mudança para enviar"
fi
echo ""

echo "=== SANITIZAÇÃO CONCLUÍDA COM SUCESSO ==="

