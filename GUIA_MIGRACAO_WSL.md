# 🚀 Guia Completo de Migração para WSL

## 📋 Índice

1. [Instalação do WSL](#instalação-do-wsl)
2. [Preparação do Ambiente](#preparação-do-ambiente)
3. [Migração de Arquivos](#migração-de-arquivos)
4. [Instalação de Dependências](#instalação-de-dependências)
5. [Configuração SSH](#configuração-ssh)
6. [Iniciar Dashboard](#iniciar-dashboard)
7. [Troubleshooting](#troubleshooting)

---

## 1️⃣ Instalação do WSL

### Windows 10/11

Abra PowerShell como **Administrador** e execute:

```powershell
wsl --install
```

Isso instalará WSL2 com Ubuntu por padrão.

### Verificar Instalação

Após reiniciar o computador:

```powershell
wsl --list --verbose
```

Deve mostrar algo como:
```
  NAME      STATE           VERSION
* Ubuntu    Running         2
```

### Primeira Inicialização

1. Abra WSL (Ubuntu) no menu Iniciar
2. Configure usuário e senha quando solicitado
3. Execute atualizações:

```bash
sudo apt update && sudo apt upgrade -y
```

---

## 2️⃣ Preparação do Ambiente

### Instalar Ferramentas Essenciais

```bash
sudo apt update
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    git \
    build-essential
```

### Instalar Node.js

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

Verificar:
```bash
node --version   # Deve mostrar v20.x.x
npm --version    # Deve mostrar 10.x.x
```

---

## 3️⃣ Migração de Arquivos

### Opção 1: Script Automático

```bash
cd ~
wget -O copy-from-windows.sh https://raw.githubusercontent.com/.../copy-from-windows.sh
chmod +x copy-from-windows.sh
./copy-from-windows.sh
```

OU use o script incluído:

```bash
cd ~/trisla-dashboard-local
chmod +x scripts-wsl/copy-from-windows.sh
./scripts-wsl/copy-from-windows.sh
```

### Opção 2: Manual

```bash
# No WSL
cp -r /mnt/c/Users/USER/Documents/trisla-deploy/trisla-dashboard-local ~/trisla-dashboard-local
cd ~/trisla-dashboard-local
```

### Ajustar Permissões

```bash
cd ~/trisla-dashboard-local
chmod +x scripts-wsl/*.sh
```

---

## 4️⃣ Instalação de Dependências

Execute o script de instalação:

```bash
cd ~/trisla-dashboard-local
./scripts-wsl/install-dependencies.sh
```

Este script:
- ✅ Cria venv Python
- ✅ Instala dependências Python (requirements.txt)
- ✅ Instala dependências npm (package.json)

**Tempo estimado:** 5-10 minutos

---

## 5️⃣ Configuração SSH

### Opção 1: Script Automático

```bash
./scripts-wsl/setup-ssh.sh
```

Este script:
- ✅ Gera chave SSH (se não existir)
- ✅ Configura ~/.ssh/config
- ✅ Testa conexão

### Opção 2: Manual

#### 5.1. Gerar Chave SSH (se necessário)

```bash
ssh-keygen -t ed25519 -C "trisla-dashboard-wsl" -f ~/.ssh/id_ed25519
```

#### 5.2. Copiar Chave para Servidor

```bash
ssh-copy-id -i ~/.ssh/id_ed25519.pub porvir5g@ppgca.unisinos.br
```

#### 5.3. Configurar ~/.ssh/config

```bash
mkdir -p ~/.ssh
cat > ~/.ssh/config << 'EOF'
Host jump
    HostName ppgca.unisinos.br
    User porvir5g
    IdentityFile ~/.ssh/id_ed25519

Host node1
    HostName node006
    User porvir5g
    ProxyJump jump
    IdentityFile ~/.ssh/id_ed25519
EOF

chmod 600 ~/.ssh/config
```

#### 5.4. Testar Conexão

```bash
ssh jump        # Deve conectar sem senha
ssh node1       # Deve conectar via jump host
```

---

## 6️⃣ Iniciar Dashboard

### Opção 1: Tudo de uma vez

```bash
./scripts-wsl/start-all.sh
```

### Opção 2: Separado (3 terminais)

**Terminal 1 - Túnel SSH:**
```bash
./scripts-wsl/start-ssh-tunnel.sh
```

**Terminal 2 - Backend:**
```bash
./scripts-wsl/start-backend.sh
```

**Terminal 3 - Frontend:**
```bash
./scripts-wsl/start-frontend.sh
```

### Parar tudo

```bash
./scripts-wsl/stop-all.sh
```

---

## 7️⃣ Troubleshooting

### Problema: WSL não inicia

**Solução:**
```powershell
# No PowerShell (Admin)
wsl --shutdown
wsl --update
```

### Problema: npm não encontrado

**Solução:**
```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### Problema: Python venv não funciona

**Solução:**
```bash
sudo apt install python3-venv
python3 -m venv venv
source venv/bin/activate
```

### Problema: SSH pede senha

**Solução:**
```bash
# Copiar chave pública
ssh-copy-id -i ~/.ssh/id_ed25519.pub porvir5g@ppgca.unisinos.br

# Ou copiar manualmente
cat ~/.ssh/id_ed25519.pub | ssh porvir5g@ppgca.unisinos.br "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

### Problema: Portas em uso

**Solução:**
```bash
# Ver processos usando portas
sudo lsof -i :5000
sudo lsof -i :5173
sudo lsof -i :9090

# Matar processos
kill -9 <PID>
```

### Problema: Permissões de arquivo

**Solução:**
```bash
chmod +x scripts-wsl/*.sh
chmod 600 ~/.ssh/config
chmod 700 ~/.ssh
```

---

## ✅ Checklist de Migração

- [ ] WSL2 instalado e funcionando
- [ ] Python3 e Node.js instalados
- [ ] Arquivos copiados para WSL
- [ ] Dependências instaladas (./install-dependencies.sh)
- [ ] SSH configurado e testado
- [ ] Dashboard iniciado com sucesso (./start-all.sh)
- [ ] Túnel SSH funcionando (opcional)
- [ ] Dashboard acessível em http://localhost:5173

---

## 🎯 Vantagens da Migração

✅ **Sem problemas de política** - npm funciona diretamente  
✅ **SSH nativo e estável** - túneis confiáveis  
✅ **Performance melhor** - desenvolvimento mais rápido  
✅ **Ambiente profissional** - padrão da indústria  
✅ **Compatibilidade** - similar ao servidor de produção  

---

## 📚 Comandos Úteis

### Ver processos rodando
```bash
ps aux | grep -E "uvicorn|vite|ssh.*9090"
```

### Ver logs
```bash
# Backend logs
tail -f ~/trisla-dashboard-local/backend/logs/*.log

# Frontend logs (no terminal onde iniciou)
```

### Reiniciar tudo
```bash
./scripts-wsl/stop-all.sh
sleep 2
./scripts-wsl/start-all.sh
```

### Verificar conexões
```bash
curl http://localhost:5000/health
curl http://localhost:5173
```

---

## 🚀 Próximos Passos

Após migração bem-sucedida:

1. ✅ Configure VS Code para usar WSL
2. ✅ Configure Git no WSL
3. ✅ Personalize seu terminal (oh-my-zsh, etc.)
4. ✅ Configure aliases úteis

---

**Pronto para começar!** Execute o guia passo a passo acima. 🎉





