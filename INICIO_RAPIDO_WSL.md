# ⚡ Início Rápido - WSL

## 🚀 Passos Rápidos (5 minutos)

### 1. Instalar WSL (se não tiver)

```powershell
# No PowerShell (Admin)
wsl --install
# Reiniciar computador
```

### 2. Abrir WSL e Preparar

```bash
# Instalar ferramentas
sudo apt update && sudo apt install -y python3 python3-pip python3-venv curl git build-essential

# Instalar Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### 3. Copiar Arquivos

```bash
cp -r /mnt/c/Users/USER/Documents/trisla-deploy/trisla-dashboard-local ~/trisla-dashboard-local
cd ~/trisla-dashboard-local
chmod +x scripts-wsl/*.sh
```

### 4. Instalar Dependências

```bash
./scripts-wsl/install-dependencies.sh
```

### 5. Configurar SSH

```bash
./scripts-wsl/setup-ssh.sh
```

### 6. Iniciar Dashboard

```bash
./scripts-wsl/start-all.sh
```

---

## ✅ Pronto!

Acesse: **http://localhost:5173**

---

## 🔧 Comandos Úteis

```bash
./scripts-wsl/start-all.sh          # Iniciar tudo
./scripts-wsl/stop-all.sh           # Parar tudo
./scripts-wsl/start-ssh-tunnel.sh   # Túnel SSH apenas
./scripts-wsl/start-backend.sh      # Backend apenas
./scripts-wsl/start-frontend.sh    # Frontend apenas
```

---

Para detalhes completos, veja: **GUIA_MIGRACAO_WSL.md**





