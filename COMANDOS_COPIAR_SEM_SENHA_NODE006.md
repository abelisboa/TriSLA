# 📤 Comandos Corrigidos - node006 sem senha

## ⚠️ IMPORTANTE

- **Jump Host**: `porvir5g@ppgca.unisinos.br` (pede senha)
- **Target**: `porvir5g@node006` (sem senha, mas especificar usuário)

---

## 🚀 Comandos Corrigidos (Copiar e Colar)

### Todos de uma vez:

```bash
# Configurar variáveis
JUMP="porvir5g@ppgca.unisinos.br"
NODE="porvir5g@node006"  # IMPORTANTE: Especificar usuário
LOCAL="/mnt/c/Users/USER/Documents/trisla-deploy/trisla-portal"
REMOTE="/home/porvir5g/gtp5g/trisla-portal"

# Criar diretórios (especificar usuário no destino)
ssh -J "${JUMP}" "${NODE}" "mkdir -p ${REMOTE}/apps/api"
ssh -J "${JUMP}" "${NODE}" "mkdir -p ${REMOTE}/apps/ui/src/pages"

# Copiar arquivo 1
scp -o ProxyJump="${JUMP}" \
    -o StrictHostKeyChecking=no \
    "${LOCAL}/apps/api/prometheus.py" \
    "${NODE}:${REMOTE}/apps/api/prometheus.py"

# Copiar arquivo 2
scp -o ProxyJump="${JUMP}" \
    -o StrictHostKeyChecking=no \
    "${LOCAL}/apps/ui/src/pages/DashboardComplete.jsx" \
    "${NODE}:${REMOTE}/apps/ui/src/pages/DashboardComplete.jsx"

# Copiar arquivo 3
scp -o ProxyJump="${JUMP}" \
    -o StrictHostKeyChecking=no \
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
ssh -J porvir5g@ppgca.unisinos.br porvir5g@node006 \
    "mkdir -p /home/porvir5g/gtp5g/trisla-portal/apps/api"

scp -o ProxyJump=porvir5g@ppgca.unisinos.br \
    -o StrictHostKeyChecking=no \
    /mnt/c/Users/USER/Documents/trisla-deploy/trisla-portal/apps/api/prometheus.py \
    porvir5g@node006:/home/porvir5g/gtp5g/trisla-portal/apps/api/prometheus.py
```

### 2. DashboardComplete.jsx

```bash
ssh -J porvir5g@ppgca.unisinos.br porvir5g@node006 \
    "mkdir -p /home/porvir5g/gtp5g/trisla-portal/apps/ui/src/pages"

scp -o ProxyJump=porvir5g@ppgca.unisinos.br \
    -o StrictHostKeyChecking=no \
    /mnt/c/Users/USER/Documents/trisla-deploy/trisla-portal/apps/ui/src/pages/DashboardComplete.jsx \
    porvir5g@node006:/home/porvir5g/gtp5g/trisla-portal/apps/ui/src/pages/DashboardComplete.jsx
```

### 3. SlicesManagement.jsx

```bash
scp -o ProxyJump=porvir5g@ppgca.unisinos.br \
    -o StrictHostKeyChecking=no \
    /mnt/c/Users/USER/Documents/trisla-deploy/trisla-portal/apps/ui/src/pages/SlicesManagement.jsx \
    porvir5g@node006:/home/porvir5g/gtp5g/trisla-portal/apps/ui/src/pages/SlicesManagement.jsx
```

---

## 🔧 Alternativa: Configurar SSH Config

Criar `~/.ssh/config`:

```bash
Host ppgca
    HostName ppgca.unisinos.br
    User porvir5g

Host node1
    HostName node006
    User porvir5g
    ProxyJump ppgca
    StrictHostKeyChecking no
```

Depois usar simplesmente:
```bash
scp arquivo node1:/path/destino
```

---

## ✅ Diferença Principal

**Antes (errado)**:
```bash
node006  # Sem usuário, pode pedir senha
```

**Agora (correto)**:
```bash
porvir5g@node006  # Com usuário, usa chave SSH sem senha
```

---

## 🎯 Comando Final Simplificado

```bash
# Se configurou ~/.ssh/config acima
scp /mnt/c/Users/USER/Documents/trisla-deploy/trisla-portal/apps/api/prometheus.py \
    node1:/home/porvir5g/gtp5g/trisla-portal/apps/api/prometheus.py
```




