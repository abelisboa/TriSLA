#!/usr/bin/env bash

# ============================================================
# 🛰️ TriSLA — Public Release Preparation Script (v3.3.0)
# Autor: Abel Lisboa
# Descrição: Prepara o repositório TriSLA para publicação pública.
# ============================================================

set -e

echo "🚀 Iniciando processo de preparação pública TriSLA v3.3.0..."
echo "📁 Diretório atual: $(pwd)"
echo "------------------------------------------------------------"

# 1️⃣ Cria backup de segurança completo
BACKUP_DIR="backup_git"
mkdir -p "$BACKUP_DIR"
git bundle create "$BACKUP_DIR/trisla_public_backup_$(date +%Y%m%d_%H%M).bundle" main
echo "✅ Backup completo criado em $BACKUP_DIR"

# 2️⃣ Atualiza .gitignore com política pública segura
cat << 'GITIGNORE' > .gitignore
# ============================================================
# 🛰️ TriSLA Public .gitignore (v3.3.0)
# ============================================================

# Ambiente e cache
.env*
*.log
*.bak
*.tmp
__pycache__/
*.pyc
*.pyo
node_modules/
dist/
build/
.vscode/
.idea/

# Backups e evidências
backup_*/
docs/evidencias/
docs/WU-*/
trisla_dissertacao_completo/
ARTIGO_*/
Overleaf/
Dissertacao_*/

# Scripts e anotações internas
PROMPTS/
ANALISE_*/
COMANDOS_*/
EXECUTAR_*/
SETUP_*/
README_TRISLA_PRIVATE.md
README_EXEC.md
README_WSL.md

# Inventários e segredos
ansible/inventory*
ansible/group_vars/*
group_vars/
nasp/

# Submódulos privados
trisla/
trisla-portal/
trisla-portal-public/
trisla-public/

# Binários grandes
buildx-v0.29.1.linux-amd64

# Mantém apenas o necessário
!apps/
!helm/
!docs/
!scripts/
!monitoring/
!README.md
!LICENSE
!CHANGELOG.md
!docker-compose.yaml
GITIGNORE
echo "✅ .gitignore atualizado"

# 3️⃣ Remove submódulos indevidos
echo "🧹 Removendo submódulos embutidos..."
git rm -f --cached trisla trisla-portal trisla-portal-public trisla-public 2>/dev/null || true

# 4️⃣ Remove binário grande se existir
if [ -f "buildx-v0.29.1.linux-amd64" ]; then
  git rm -f --cached buildx-v0.29.1.linux-amd64 || true
  echo "⚙️ Binário buildx removido do controle Git."
fi

# 5️⃣ Validação de labels Helm
if [ -f "scripts/fix_label_ports_and_versions_v2.sh" ]; then
  echo "🔍 Validando templates Helm..."
  bash scripts/fix_label_ports_and_versions_v2.sh || true
fi

# 6️⃣ Revalida Helm charts
if command -v helm >/dev/null 2>&1; then
  echo "🧠 Executando helm lint..."
  helm lint ./helm/trisla-portal || echo "⚠️ Helm lint retornou warnings."
fi

# 7️⃣ Commit de sincronização pública
echo "🧾 Gerando commit de sincronização..."
git add .gitignore
git add .
git commit -m '🛰️ TriSLA v3.3.0 — Public Release Cleanup and Validation'

# 8️⃣ Criação do pacote de release
RELEASE_FILE="TriSLA-Public-v3.3.0.zip"
echo "📦 Gerando pacote: $RELEASE_FILE ..."
zip -r "$RELEASE_FILE" apps helm docs scripts docker-compose.yaml README.md CHANGELOG.md 1>/dev/null
echo "✅ Pacote gerado: $RELEASE_FILE"

# 9️⃣ Push para o repositório público
echo "🌐 Publicando alterações..."
git push origin main --force-with-lease

echo "------------------------------------------------------------"
echo "✅ Publicação TriSLA-Public v3.3.0 concluída com sucesso!"
echo "📦 Pacote: $(pwd)/$RELEASE_FILE"
echo "🔗 Repositório: https://github.com/abelisboa/TriSLA"
echo "------------------------------------------------------------"

