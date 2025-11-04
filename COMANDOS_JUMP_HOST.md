# 📤 Comandos SCP via Jump Host

## 🔄 Acesso ao node1

```
WSL → porvir5g@ppgca.unisinos.br (com senha) → node006/node1 (sem senha)
```

---

## 📁 Comandos Individuais (Caminhos Completos)

### Arquivo 1: prometheus.py

```bash
# Criar diretório
ssh -J porvir5g@ppgca.unisinos.br node006 "mkdir -p /home/porvir5g/gtp5g/trisla-portal/apps/api"

# Copiar arquivo
scp -o ProxyJump=porvir5g@ppgca.unisinos.br \
    /mnt/c/Users/USER/Documents/trisla-deploy/trisla-portal/apps/api/prometheus.py \
    node006:/home/porvir5g/gtp5g/trisla-portal/apps/api/prometheus.py
```

### Arquivo 2: DashboardComplete.jsx

```bash
# Criar diretório
ssh -J porvir5g@ppgca.unisinos.br node006 "mkdir -p /home/porvir5g/gtp5g/trisla-portal/apps/ui/src/pages"

# Copiar arquivo
scp -o ProxyJump=porvir5g@ppgca.unisinos.br \
    /mnt/c/Users/USER/Documents/trisla-deploy/trisla-portal/apps/ui/src/pages/DashboardComplete.jsx \
    node006:/home/porvir5g/gtp5g/trisla-portal/apps/ui/src/pages/DashboardComplete.jsx
```

### Arquivo 3: SlicesManagement.jsx

```bash
# Copiar arquivo (diretório já criado)
scp -o ProxyJump=porvir5g@ppgca.unisinos.br \
    /mnt/c/Users/USER/Documents/trisla-deploy/trisla-portal/apps/ui/src/pages/SlicesManagement.jsx \
    node006:/home/porvir5g/gtp5g/trisla-portal/apps/ui/src/pages/SlicesManagement.jsx
```

---

## 🚀 Todos de uma vez (Copiar e Colar)

```bash
# Configurar variáveis
JUMP_HOST="porvir5g@ppgca.unisinos.br"
TARGET_HOST="node006"
LOCAL_BASE="/mnt/c/Users/USER/Documents/trisla-deploy/trisla-portal"
REMOTE_BASE="/home/porvir5g/gtp5g/trisla-portal"

# Criar diretórios
ssh -J "${JUMP_HOST}" "${TARGET_HOST}" "mkdir -p ${REMOTE_BASE}/apps/api"
ssh -J "${JUMP_HOST}" "${TARGET_HOST}" "mkdir -p ${REMOTE_BASE}/apps/ui/src/pages"

# Copiar arquivo 1
scp -o ProxyJump="${JUMP_HOST}" \
    "${LOCAL_BASE}/apps/api/prometheus.py" \
    "${TARGET_HOST}:${REMOTE_BASE}/apps/api/prometheus.py"

# Copiar arquivo 2
scp -o ProxyJump="${JUMP_HOST}" \
    "${LOCAL_BASE}/apps/ui/src/pages/DashboardComplete.jsx" \
    "${TARGET_HOST}:${REMOTE_BASE}/apps/ui/src/pages/DashboardComplete.jsx"

# Copiar arquivo 3
scp -o ProxyJump="${JUMP_HOST}" \
    "${LOCAL_BASE}/apps/ui/src/pages/SlicesManagement.jsx" \
    "${TARGET_HOST}:${REMOTE_BASE}/apps/ui/src/pages/SlicesManagement.jsx"

# Verificar
ssh -J "${JUMP_HOST}" "${TARGET_HOST}" \
    "ls -lh ${REMOTE_BASE}/apps/api/prometheus.py ${REMOTE_BASE}/apps/ui/src/pages/*.jsx"
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
```

Depois usar:
```bash
scp arquivo node1:/path/destino
```

---

## ✅ Verificar Arquivos Copiados

```bash
# Conectar ao node1
ssh -J porvir5g@ppgca.unisinos.br node006

# Verificar arquivos
ls -lh /home/porvir5g/gtp5g/trisla-portal/apps/api/prometheus.py
ls -lh /home/porvir5g/gtp5g/trisla-portal/apps/ui/src/pages/DashboardComplete.jsx
ls -lh /home/porvir5g/gtp5g/trisla-portal/apps/ui/src/pages/SlicesManagement.jsx
```

---

## 📝 Nota Importante

- **Jump Host**: `porvir5g@ppgca.unisinos.br` (pede senha)
- **Target**: `node006` (sem senha, acessa via jump host)
- **Node1**: É o mesmo que `node006`

Use `-J` ou `ProxyJump` para passar pelo jump host!




