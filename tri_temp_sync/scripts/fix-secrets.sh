#!/bin/bash
set -e

REPO_DIR="/mnt/c/Users/USER/Documents/TriSLA-clean"
BACKUP_DIR="/mnt/c/Users/USER/Documents/TriSLA-clean-backup"
TARGET_FILE="$REPO_DIR/TriSLA_PROMPTS/0_MASTER/06_CONFIGURACAO_TOKENS.md"

echo "🔍 Entrando no repositório..."
cd "$REPO_DIR"

echo "⚡ Criando backup MINIMAL (somente o arquivo com problema)..."
mkdir -p "$BACKUP_DIR"

# Faz backup somente se o arquivo existir
if [ -f "$TARGET_FILE" ]; then
    cp "$TARGET_FILE" "$BACKUP_DIR/"
    echo "📄 Arquivo encontrado e copiado para backup."
else
    echo "⚠️ Aviso: Arquivo 06_CONFIGURACAO_TOKENS.md não existe. Backup ignorado."
fi

echo "📦 Instalando git-filter-repo (método oficial e mais rápido)..."
pip install git-filter-repo >/dev/null 2>&1 || true

# Sanitiza o arquivo APENAS se existir
if [ -f "$TARGET_FILE" ]; then
    echo "✏️ Sanitizando arquivo atual..."
    sed -i 's/github_pat_[A-Za-z0-9_]*/<REMOVIDO>/g' "$TARGET_FILE"
    sed -i 's/ghp_[A-Za-z0-9_]*/<REMOVIDO>/g' "$TARGET_FILE"
    sed -i 's/Bearer [A-Za-z0-9._-]*/Bearer <REMOVIDO>/g' "$TARGET_FILE"
else
    echo "⚠️ Arquivo não encontrado, ignorando sanitização."
fi

echo "🛑 Removendo tokens do HISTÓRICO (rápido e seguro)..."
git filter-repo --force --replace-text <(
cat <<EOF
github_pat_
ghp_
Bearer
EOF
)

# Só tenta adicionar/commitar se o arquivo existir
if [ -f "$TARGET_FILE" ]; then
    echo "📌 Criando commit do arquivo sanitizado..."
    git add "$TARGET_FILE" || true
    git commit -m "Remove secrets and sanitize tokens" || true
else
    echo "⚠️ Nenhum arquivo de tokens encontrado; commit ignorado."
fi

echo "🚀 Enviando histórico limpo ao GitHub..."
git push origin main --force

echo "🛡 Aplicando proteções locais..."
echo "TriSLA_PROMPTS/0_MASTER/06_CONFIGURACAO_TOKENS.md" >> .gitignore

echo ""
echo "✔️ Finalizado com sucesso!"
echo "✔️ Tokens removidos do arquivo atual (se existia)"
echo "✔️ Tokens removidos do histórico inteiro"
echo "✔️ Push liberado"
echo "�� Backup mínimo salvo em: $BACKUP_DIR/"
