# 📤 Comandos para Copiar Arquivos para node1

## 📍 Você está em: `trisla-portal/`

## 🚀 Opção 1: Script Automático (Recomendado)

### No WSL/Bash:

```bash
# Na pasta trisla-portal
chmod +x ../COPIAR_ARQUIVOS_NODE1.sh
../COPIAR_ARQUIVOS_NODE1.sh
```

### No PowerShell (Windows):

```powershell
# Na pasta trisla-deploy
.\COPIAR_ARQUIVOS_NODE1.ps1
```

---

## 🚀 Opção 2: Comandos Manuais (WSL/Bash)

```bash
# Garantir que está na pasta correta
cd /mnt/c/Users/USER/Documents/trisla-deploy/trisla-portal

# Configurar variáveis
NODE1_HOST="porvir5g@192.168.10.16"
BASE_PATH="~/gtp5g/trisla-portal"

# 1. Backend API Prometheus
echo "Copiando prometheus.py..."
ssh "${NODE1_HOST}" "mkdir -p ${BASE_PATH}/apps/api"
scp apps/api/prometheus.py "${NODE1_HOST}:${BASE_PATH}/apps/api/prometheus.py"

# 2. Dashboard Completo
echo "Copiando DashboardComplete.jsx..."
ssh "${NODE1_HOST}" "mkdir -p ${BASE_PATH}/apps/ui/src/pages"
scp apps/ui/src/pages/DashboardComplete.jsx "${NODE1_HOST}:${BASE_PATH}/apps/ui/src/pages/DashboardComplete.jsx"

# 3. Gestão de Slices
echo "Copiando SlicesManagement.jsx..."
scp apps/ui/src/pages/SlicesManagement.jsx "${NODE1_HOST}:${BASE_PATH}/apps/ui/src/pages/SlicesManagement.jsx"

# Verificar arquivos copiados
ssh "${NODE1_HOST}" "ls -lh ${BASE_PATH}/apps/api/prometheus.py ${BASE_PATH}/apps/ui/src/pages/DashboardComplete.jsx ${BASE_PATH}/apps/ui/src/pages/SlicesManagement.jsx"
```

---

## 🚀 Opção 3: Comandos Manuais (PowerShell)

```powershell
# Na pasta trisla-deploy
$Node1Host = "porvir5g@192.168.10.16"
$BasePath = "~/gtp5g/trisla-portal"

# Criar diretórios
ssh "$Node1Host" "mkdir -p $BasePath/apps/api"
ssh "$Node1Host" "mkdir -p $BasePath/apps/ui/src/pages"

# Copiar arquivos
scp trisla-portal/apps/api/prometheus.py "${Node1Host}:${BasePath}/apps/api/prometheus.py"
scp trisla-portal/apps/ui/src/pages/DashboardComplete.jsx "${Node1Host}:${BasePath}/apps/ui/src/pages/DashboardComplete.jsx"
scp trisla-portal/apps/ui/src/pages/SlicesManagement.jsx "${Node1Host}:${BasePath}/apps/ui/src/pages/SlicesManagement.jsx"

# Verificar
ssh "$Node1Host" "ls -lh $BasePath/apps/api/prometheus.py $BasePath/apps/ui/src/pages/*.jsx"
```

---

## 📋 Arquivos a Copiar

1. ✅ `apps/api/prometheus.py` → `~/gtp5g/trisla-portal/apps/api/prometheus.py`
2. ✅ `apps/ui/src/pages/DashboardComplete.jsx` → `~/gtp5g/trisla-portal/apps/ui/src/pages/DashboardComplete.jsx`
3. ✅ `apps/ui/src/pages/SlicesManagement.jsx` → `~/gtp5g/trisla-portal/apps/ui/src/pages/SlicesManagement.jsx`

**Nota**: Os arquivos `main.py` e `App.jsx` também precisam ser atualizados no node1, mas esses já devem existir. Verifique se as alterações foram aplicadas.

---

## ✅ Após Copiar - Verificar no node1

```bash
# No node1
cd ~/gtp5g/trisla-portal

# Verificar arquivos
ls -lh apps/api/prometheus.py
ls -lh apps/ui/src/pages/DashboardComplete.jsx
ls -lh apps/ui/src/pages/SlicesManagement.jsx

# Verificar se router está no main.py
grep -A 3 "prometheus_router" apps/api/main.py

# Verificar se rotas estão no App.jsx
grep -A 3 "DashboardComplete" apps/ui/src/App.jsx
```

---

## 🔧 Se Arquivos Não Estiverem no node1

Se `main.py` e `App.jsx` não tiverem as alterações, adicione manualmente:

### No node1 - Atualizar main.py:

```bash
# Adicionar router Prometheus no final do main.py (antes do último except)
cat >> apps/api/main.py << 'EOF'

# ------------------------------------------------------------
# Prometheus router (dashboard customizado - sem Grafana)
# ------------------------------------------------------------
try:
    from prometheus import router as prometheus_router  # type: ignore

    app.include_router(prometheus_router)
    log.info("Prometheus router habilitado em /prometheus")
except Exception as e:
    log.warning("Prometheus router não carregado: %s", e)
EOF
```

### No node1 - Atualizar App.jsx:

Adicionar imports e rotas conforme o arquivo atualizado localmente.




