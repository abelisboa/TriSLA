# Como Criar/Copiar Dashboards no node1

## 🔍 Situação Atual

- ❌ SSH do Windows para node1 não funciona (timeout)
- ✅ Você já está conectado no node1 via outro terminal
- ✅ Você pode criar arquivos diretamente no node1

---

## 🎯 Soluções

### Opção 1: Criar via Interface Web do Grafana (MAIS FÁCIL)

Como você já está no node1 e o Grafana está acessível, pode importar diretamente via web:

#### Passos:

1. **Acessar Grafana**:
   ```bash
   # No node1, configurar port-forward (se necessário)
   kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80 &
   
   # Ou acessar diretamente via NodePort
   # http://192.168.10.16:30000
   ```

2. **Importar via Web UI**:
   - Acessar: http://localhost:3000 (ou http://192.168.10.16:30000)
   - Login: `admin` / `TriSLA2025!`
   - Ir em: **Dashboards** → **Import**
   - **Upload JSON** ou **Paste JSON**
   - Colar o conteúdo de cada arquivo JSON
   - Salvar

#### Arquivos para importar (na ordem):

1. `trisla-complete-main.json`
2. `trisla-slices-management.json`
3. `trisla-metrics-detailed.json`
4. `trisla-admin-panel.json`
5. `trisla-create-slices.json`
6. `trisla-centralized-view.json`

---

### Opção 2: Criar Arquivos via Git Clone

Se os arquivos estiverem em um repositório Git:

```bash
# No node1
cd ~/gtp5g/trisla-portal

# Se já for um repo Git
git pull origin main

# Ou clonar o repo completo se necessário
# git clone <repo-url>
```

---

### Opção 3: Copiar via USB/Transferência Manual

1. Copiar arquivos JSON do seu Windows para um pendrive/USB
2. Conectar no node1 e copiar arquivos
3. Ou usar outro método de transferência

---

### Opção 4: Criar Arquivos via cat/echo

No node1, você pode criar os arquivos JSON manualmente:

```bash
# No node1
cd ~/gtp5g/trisla-portal
mkdir -p grafana-dashboards

# Criar arquivo vazio e editar
cat > grafana-dashboards/trisla-complete-main.json << 'EOF'
[colar o conteúdo JSON completo aqui]
EOF
```

**Nota**: Isso requer copiar/colar o conteúdo completo de cada arquivo JSON.

---

## ✅ Solução Recomendada: Import via Web UI

A forma mais simples é importar diretamente via interface web do Grafana:

### Comandos no node1:

```bash
# 1. Configurar port-forward (se necessário)
kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80 &

# 2. Abrir navegador ou usar curl para testar
curl -s http://localhost:3000/api/health | jq .

# 3. Importar via web UI
# Acessar http://localhost:3000 ou http://192.168.10.16:30000
# Login: admin / TriSLA2025!
# Dashboards > Import > Paste JSON
```

### Ou usar API diretamente (se tiver os JSONs):

Se você conseguir os arquivos JSON no node1 (via git, download, etc):

```bash
cd ~/gtp5g/trisla-portal

# Verificar se arquivos existem
ls grafana-dashboards/*.json

# Se existirem, importar via API
./scripts/import_grafana_dashboards_fixed.sh
```

---

## 🎯 Recomendação Final

**Use a interface web do Grafana** - é a forma mais simples:

1. Abra o Grafana no navegador
2. Importe cada dashboard JSON via interface
3. Não precisa criar arquivos no filesystem do node1

Os dashboards importados ficam armazenados no Grafana e funcionam normalmente!




