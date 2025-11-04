# 🚀 Importar Dashboards via API (Grafana já está acessível!)

## ✅ Situação Atual

- ✅ Grafana está acessível em http://localhost:3000
- ✅ Port-forward já está ativo ou Grafana rodando na porta
- ✅ Pode importar dashboards via API diretamente

---

## 🎯 Importar Dashboards via API

### Comandos no node1:

```bash
# No node1, já conectado
cd ~/gtp5g/trisla-portal

# Configurar variáveis
GRAFANA_URL="http://localhost:3000"
GRAFANA_USER="admin"
GRAFANA_PASS="TriSLA2025!"

# Verificar conectividade
curl -s "${GRAFANA_URL}/api/health" | jq .

# Como os arquivos JSON não existem no node1 ainda, temos 2 opções:
```

---

## 📋 Opção 1: Criar Arquivos JSON no node1 via cat

Crie cada arquivo JSON no node1 manualmente usando `cat`:

```bash
# No node1
cd ~/gtp5g/trisla-portal
mkdir -p grafana-dashboards

# Exemplo: Criar primeiro dashboard
cat > grafana-dashboards/trisla-complete-main.json << 'EOF'
[paste o conteúdo JSON completo aqui]
EOF
```

**Mas isso requer copiar/colar o conteúdo completo de cada arquivo JSON.**

---

## 📋 Opção 2: Importar via API com JSON inline (Recomendado)

Se você tem acesso ao conteúdo JSON dos dashboards, pode importar diretamente via API:

```bash
# No node1
GRAFANA_URL="http://localhost:3000"
GRAFANA_USER="admin"
GRAFANA_PASS="TriSLA2025!"

# Criar script temporário com JSON inline
# Ou usar curl com JSON inline
```

---

## 📋 Opção 3: Baixar do Repositório Git

Se os arquivos estão em um repositório Git:

```bash
# No node1
cd ~/gtp5g/trisla-portal

# Verificar se é repo Git
if [ -d ".git" ]; then
    git pull origin main  # ou master
fi

# Se não for repo Git, clonar:
# git clone <repo-url> .
# ou apenas baixar os arquivos específicos
```

---

## 📋 Opção 4: Usar Interface Web do Grafana (MAIS FÁCIL)

Já que o Grafana está acessível, use a interface web:

### No navegador do seu computador:

1. **Configurar port-forward do node1 para seu computador** (se necessário):
   ```bash
   # No node1
   kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80
   # Manter esse comando rodando
   ```

2. **Acessar Grafana**: http://192.168.10.16:30000 (NodePort) ou via port-forward

3. **Importar via UI**:
   - Login: `admin` / `TriSLA2025!`
   - Ir em: **Dashboards** → **Import**
   - **Paste JSON** → Colar conteúdo de cada arquivo
   - **Load** → **Import**

---

## 🎯 Solução Rápida: Usar NodePort

Se o Grafana tiver NodePort configurado, você pode acessar diretamente:

```bash
# No node1, verificar NodePort do Grafana
kubectl get svc -n monitoring | grep grafana

# Exemplo de saída:
# monitoring-grafana   NodePort   10.96.x.x   30000:30000/TCP

# Acessar via NodePort
# http://192.168.10.16:30000
```

---

## ✅ Recomendação Final

**Use a interface web do Grafana** - é a forma mais simples:

1. Verificar NodePort ou configurar port-forward do node1 para seu PC
2. Acessar Grafana no navegador: http://192.168.10.16:30000
3. Importar cada dashboard via UI (Paste JSON)

**Ou** se você conseguir os arquivos JSON no node1 via Git/download:

```bash
# Após ter os arquivos JSON no node1:
cd ~/gtp5g/trisla-portal
chmod +x scripts/import_grafana_dashboards_fixed.sh
./scripts/import_grafana_dashboards_fixed.sh
```




