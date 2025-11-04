# 📤 Comandos Corretos para Copiar para node1

## ⚠️ IMPORTANTE: Acesso via Jump Host

```
Seu PC → porvir5g@ppgca.unisinos.br (senha) → node006/node1 (sem senha)
```

---

## 🚀 Comandos Prontos (Execute no WSL)

### Opção 1: Script Automático

```bash
# Na pasta trisla-portal
chmod +x ../COPIAR_ARQUIVOS_JUMP_HOST.sh
../COPIAR_ARQUIVOS_JUMP_HOST.sh
```

### Opção 2: Comandos Manuais (Copiar e Colar)

```bash
# Configurar variáveis
JUMP="porvir5g@ppgca.unisinos.br"
NODE="node006"
LOCAL="/mnt/c/Users/USER/Documents/trisla-deploy/trisla-portal"
REMOTE="/home/porvir5g/gtp5g/trisla-portal"

# Criar diretórios
ssh -J "${JUMP}" "${NODE}" "mkdir -p ${REMOTE}/apps/api"
ssh -J "${JUMP}" "${NODE}" "mkdir -p ${REMOTE}/apps/ui/src/pages"

# Copiar arquivo 1
scp -o ProxyJump="${JUMP}" \
    "${LOCAL}/apps/api/prometheus.py" \
    "${NODE}:${REMOTE}/apps/api/prometheus.py"

# Copiar arquivo 2
scp -o ProxyJump="${JUMP}" \
    "${LOCAL}/apps/ui/src/pages/DashboardComplete.jsx" \
    "${NODE}:${REMOTE}/apps/ui/src/pages/DashboardComplete.jsx"

# Copiar arquivo 3
scp -o ProxyJump="${JUMP}" \
    "${LOCAL}/apps/ui/src/pages/SlicesManagement.jsx" \
    "${NODE}:${REMOTE}/apps/ui/src/pages/SlicesManagement.jsx"

# Verificar
ssh -J "${JUMP}" "${NODE}" \
    "ls -lh ${REMOTE}/apps/api/prometheus.py ${REMOTE}/apps/ui/src/pages/*.jsx"
```

---

## 📋 Arquivo por Arquivo

### 1. prometheus.py
```bash
ssh -J porvir5g@ppgca.unisinos.br node006 "mkdir -p /home/porvir5g/gtp5g/trisla-portal/apps/api"
scp -o ProxyJump=porvir5g@ppgca.unisinos.br \
    /mnt/c/Users/USER/Documents/trisla-deploy/trisla-portal/apps/api/prometheus.py \
    node006:/home/porvir5g/gtp5g/trisla-portal/apps/api/prometheus.py
```

### 2. DashboardComplete.jsx
```bash
ssh -J porvir5g@ppgca.unisinos.br node006 "mkdir -p /home/porvir5g/gtp5g/trisla-portal/apps/ui/src/pages"
scp -o ProxyJump=porvir5g@ppgca.unisinos.br \
    /mnt/c/Users/USER/Documents/trisla-deploy/trisla-portal/apps/ui/src/pages/DashboardComplete.jsx \
    node006:/home/porvir5g/gtp5g/trisla-portal/apps/ui/src/pages/DashboardComplete.jsx
```

### 3. SlicesManagement.jsx
```bash
scp -o ProxyJump=porvir5g@ppgca.unisinos.br \
    /mnt/c/Users/USER/Documents/trisla-deploy/trisla-portal/apps/ui/src/pages/SlicesManagement.jsx \
    node006:/home/porvir5g/gtp5g/trisla-portal/apps/ui/src/pages/SlicesManagement.jsx
```

---

## ✅ Pronto para Executar!

Execute os comandos acima no WSL. Vai pedir senha apenas uma vez para `ppgca.unisinos.br`.




