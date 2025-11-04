#!/bin/bash
# Script completo de setup para WSL
# Verifica e cria/copia todos os arquivos necessários
# Uso: ./scripts-wsl/setup-complete.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_DIR"

echo "🚀 Setup Completo do TriSLA Dashboard - WSL"
echo "============================================="
echo ""

# Verificar se está no WSL
if [ ! -d "/mnt/c" ]; then
    echo "⚠️  Este script é para WSL. Se você está no Windows, use os scripts PowerShell."
    exit 1
fi

# 1. Verificar e copiar arquivos do Windows se necessário
WINDOWS_PATH="/mnt/c/Users/USER/Documents/trisla-deploy/trisla-dashboard-local"

if [ -d "$WINDOWS_PATH" ]; then
    echo "📁 Arquivos encontrados no Windows"
    echo "   Origem: $WINDOWS_PATH"
    echo "   Se quiser copiar arquivos do Windows, execute:"
    echo "   ./scripts-wsl/copy-from-windows.sh"
    echo ""
else
    echo "ℹ️  Caminho do Windows não encontrado ou já está no WSL"
    echo ""
fi

# 2. Verificar estrutura
echo "1️⃣ Verificando estrutura..."
echo ""

# Verificar diretórios
for dir in backend frontend scripts-wsl; do
    if [ ! -d "$dir" ]; then
        echo "   ❌ Diretório $dir não encontrado!"
        echo "   Execute: ./scripts-wsl/copy-from-windows.sh"
        exit 1
    else
        echo "   ✅ $dir/"
    fi
done

# 3. Dar permissão aos scripts
echo ""
echo "2️⃣ Configurando permissões..."
chmod +x scripts-wsl/*.sh 2>/dev/null || true
echo "   ✅ Scripts executáveis"

# 4. Verificar dependências do sistema
echo ""
echo "3️⃣ Verificando dependências do sistema..."

MISSING_DEPS=()

if ! command -v python3 &> /dev/null; then
    MISSING_DEPS+=("python3")
fi

if ! command -v node &> /dev/null; then
    MISSING_DEPS+=("nodejs")
fi

if ! command -v npm &> /dev/null; then
    MISSING_DEPS+=("npm (via nodejs)")
fi

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo "   ❌ Dependências faltando: ${MISSING_DEPS[*]}"
    echo ""
    echo "   Instale com:"
    echo "   sudo apt update"
    echo "   sudo apt install -y python3 python3-pip python3-venv curl git build-essential"
    echo "   curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -"
    echo "   sudo apt-get install -y nodejs"
    exit 1
else
    echo "   ✅ Python: $(python3 --version)"
    echo "   ✅ Node.js: $(node --version)"
    echo "   ✅ npm: $(npm --version)"
fi

# 5. Instalar dependências do projeto
echo ""
echo "4️⃣ Instalando dependências do projeto..."
echo "   Isso pode levar alguns minutos..."
echo ""

if [ -f "scripts-wsl/install-dependencies.sh" ]; then
    ./scripts-wsl/install-dependencies.sh
else
    echo "   ⚠️  Script install-dependencies.sh não encontrado"
    echo "   Execute manualmente:"
    echo "   cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    echo "   cd frontend && npm install"
fi

# 6. Verificar configuração SSH
echo ""
echo "5️⃣ Verificando SSH..."
if [ -f ~/.ssh/config ]; then
    echo "   ✅ ~/.ssh/config existe"
else
    echo "   ⚠️  SSH não configurado"
    echo "   Execute: ./scripts-wsl/setup-ssh.sh"
fi

# Conclusão
echo ""
echo "✅ Setup completo!"
echo ""
echo "🚀 Próximos passos:"
echo "   1. Configure SSH (se necessário):"
echo "      ./scripts-wsl/setup-ssh.sh"
echo ""
echo "   2. Inicie o dashboard:"
echo "      ./scripts-wsl/start-all.sh"
echo ""
echo "   3. Acesse: http://localhost:5173"





