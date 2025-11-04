#!/bin/bash
# Script para configurar SSH no WSL
# Uso: ./scripts-wsl/setup-ssh.sh

set -e

echo "🔑 Configurando SSH no WSL..."
echo ""

# Criar diretório .ssh se não existir
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Verificar se já existe chave SSH
if [ ! -f ~/.ssh/id_rsa ] && [ ! -f ~/.ssh/id_ed25519 ]; then
    echo "📝 Gerando chave SSH..."
    ssh-keygen -t ed25519 -C "trisla-dashboard-wsl" -f ~/.ssh/id_ed25519 -N ""
    echo "   ✅ Chave SSH gerada: ~/.ssh/id_ed25519.pub"
    echo ""
    echo "📋 Adicione esta chave pública ao servidor:"
    echo "---"
    cat ~/.ssh/id_ed25519.pub
    echo "---"
    echo ""
    read -p "Pressione Enter após adicionar a chave ao servidor..."
else
    echo "✅ Chave SSH já existe"
fi

# Criar/atualizar ~/.ssh/config
echo ""
echo "📝 Configurando ~/.ssh/config..."
cat > ~/.ssh/config << 'EOF'
Host jump
    HostName ppgca.unisinos.br
    User porvir5g
    IdentityFile ~/.ssh/id_ed25519
    StrictHostKeyChecking no
    UserKnownHostsFile ~/.ssh/known_hosts

Host node1
    HostName node006
    User porvir5g
    ProxyJump jump
    IdentityFile ~/.ssh/id_ed25519
    StrictHostKeyChecking no
    UserKnownHostsFile ~/.ssh/known_hosts
EOF

chmod 600 ~/.ssh/config

echo "   ✅ ~/.ssh/config criado"
echo ""

# Testar conexão
echo "🧪 Testando conexão SSH..."
if ssh -o ConnectTimeout=5 jump "echo 'Conexão OK'" 2>/dev/null; then
    echo "   ✅ Conexão com jump host funcionando"
else
    echo "   ⚠️  Não foi possível conectar. Verifique suas credenciais."
    echo "   Você pode testar manualmente com: ssh jump"
fi

echo ""
echo "✅ Configuração SSH concluída!"
echo ""
echo "Uso:"
echo "   ssh jump          # Conectar ao jump host"
echo "   ssh node1         # Conectar ao node1 via jump host"
echo "   ./scripts-wsl/start-ssh-tunnel.sh  # Iniciar túnel Prometheus"





