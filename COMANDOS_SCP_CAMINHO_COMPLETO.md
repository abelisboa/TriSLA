# 📤 Comandos SCP com Caminhos Completos

## 🎯 Execute arquivo por arquivo

### Configuração:

```bash
# Caminhos completos
LOCAL_BASE="/mnt/c/Users/USER/Documents/trisla-deploy/trisla-portal"
NODE1_HOST="porvir5g@192.168.10.16"
NODE1_BASE="/home/porvir5g/gtp5g/trisla-portal"
```

---

## 📁 Arquivo 1: prometheus.py

```bash
# Criar diretório no node1
ssh porvir5g@192.168.10.16 "mkdir -p /home/porvir5g/gtp5g/trisla-portal/apps/api"

# Copiar arquivo
scp /mnt/c/Users/USER/Documents/trisla-deploy/trisla-portal/apps/api/prometheus.py \
    porvir5g@192.168.10.16:/home/porvir5g/gtp5g/trisla-portal/apps/api/prometheus.py
```

---

## 📁 Arquivo 2: DashboardComplete.jsx

```bash
# Criar diretório no node1
ssh porvir5g@192.168.10.16 "mkdir -p /home/porvir5g/gtp5g/trisla-portal/apps/ui/src/pages"

# Copiar arquivo
scp /mnt/c/Users/USER/Documents/trisla-deploy/trisla-portal/apps/ui/src/pages/DashboardComplete.jsx \
    porvir5g@192.168.10.16:/home/porvir5g/gtp5g/trisla-portal/apps/ui/src/pages/DashboardComplete.jsx
```

---

## 📁 Arquivo 3: SlicesManagement.jsx

```bash
# Copiar arquivo (diretório já criado acima)
scp /mnt/c/Users/USER/Documents/trisla-deploy/trisla-portal/apps/ui/src/pages/SlicesManagement.jsx \
    porvir5g@192.168.10.16:/home/porvir5g/gtp5g/trisla-portal/apps/ui/src/pages/SlicesManagement.jsx
```

---

## 🚀 Todos de uma vez (copiar e colar)

```bash
# Configurar variáveis
LOCAL_BASE="/mnt/c/Users/USER/Documents/trisla-deploy/trisla-portal"
NODE1_HOST="porvir5g@192.168.10.16"
NODE1_BASE="/home/porvir5g/gtp5g/trisla-portal"

# Criar diretórios
ssh "${NODE1_HOST}" "mkdir -p ${NODE1_BASE}/apps/api"
ssh "${NODE1_HOST}" "mkdir -p ${NODE1_BASE}/apps/ui/src/pages"

# Copiar arquivo 1
scp "${LOCAL_BASE}/apps/api/prometheus.py" \
    "${NODE1_HOST}:${NODE1_BASE}/apps/api/prometheus.py"

# Copiar arquivo 2
scp "${LOCAL_BASE}/apps/ui/src/pages/DashboardComplete.jsx" \
    "${NODE1_HOST}:${NODE1_BASE}/apps/ui/src/pages/DashboardComplete.jsx"

# Copiar arquivo 3
scp "${LOCAL_BASE}/apps/ui/src/pages/SlicesManagement.jsx" \
    "${NODE1_HOST}:${NODE1_BASE}/apps/ui/src/pages/SlicesManagement.jsx"

# Verificar
ssh "${NODE1_HOST}" "ls -lh ${NODE1_BASE}/apps/api/prometheus.py ${NODE1_BASE}/apps/ui/src/pages/*.jsx"
```

---

## ✅ Verificar no node1

```bash
ssh porvir5g@192.168.10.16 "ls -lh /home/porvir5g/gtp5g/trisla-portal/apps/api/prometheus.py"
ssh porvir5g@192.168.10.16 "ls -lh /home/porvir5g/gtp5g/trisla-portal/apps/ui/src/pages/DashboardComplete.jsx"
ssh porvir5g@192.168.10.16 "ls -lh /home/porvir5g/gtp5g/trisla-portal/apps/ui/src/pages/SlicesManagement.jsx"
```




