# 📊 Importar Dashboards TriSLA - Guia Final

## ✅ Situação Atual

- ✅ Grafana acessível: http://localhost:3000
- ✅ Credenciais: admin / TriSLA2025!
- ⚠️ Arquivos JSON não estão no node1 ainda

---

## 🎯 Opção 1: Importar via Interface Web (RECOMENDADO - Mais Fácil)

### Passos:

1. **Acessar Grafana:**
   - URL: http://localhost:3000
   - Login: `admin` / `TriSLA2025!`

2. **Importar cada dashboard:**
   - Ir em: **Dashboards** → **Import**
   - Escolher: **Paste JSON**
   - Abrir arquivo JSON no Windows (ex: `grafana-dashboards/trisla-complete-main.json`)
   - Copiar todo conteúdo (Ctrl+A, Ctrl+C)
   - Colar no Grafana
   - Clicar em **Load**
   - Clicar em **Import**
   - Repetir para cada dashboard

### Arquivos para importar (6 dashboards):

1. `trisla-complete-main.json` - Dashboard Principal
2. `trisla-slices-management.json` - Gestão de Slices
3. `trisla-metrics-detailed.json` - Métricas Detalhadas
4. `trisla-admin-panel.json` - Painel Admin
5. `trisla-create-slices.json` - Criar Slices
6. `trisla-centralized-view.json` - Visão Centralizada

---

## 🎯 Opção 2: Copiar Arquivos para node1 e Importar via API

### Passo 1: Copiar arquivos para node1

**No Windows**, você pode:

1. **Via USB/Pen Drive** (se node1 tiver acesso)
2. **Via Git** (se arquivos estiverem no repositório):
   ```bash
   # No node1
   cd ~/gtp5g/trisla-portal
   git pull  # se for repo git
   ```
3. **Criar arquivos manualmente no node1** (copiar/colar conteúdo)

### Passo 2: Importar via script

```bash
# No node1
cd ~/gtp5g/trisla-portal

# Verificar se arquivos existem
ls -lh grafana-dashboards/*.json

# Se existirem, importar
chmod +x scripts/import_dashboards_grafana.sh
./scripts/import_dashboards_grafana.sh
```

---

## 🎯 Opção 3: Criar Arquivos JSON no node1

Se você conseguir o conteúdo dos JSONs:

```bash
# No node1
cd ~/gtp5g/trisla-portal
mkdir -p grafana-dashboards

# Criar arquivo (exemplo)
cat > grafana-dashboards/trisla-complete-main.json << 'EOF'
[paste conteúdo JSON completo aqui]
EOF

# Repetir para cada dashboard
# Depois importar via script
```

---

## ✅ Solução Mais Rápida: Interface Web

Como os arquivos não estão no node1 e copiar via SSH não funciona:

**RECOMENDAÇÃO: Use a interface web do Grafana**

1. ✅ Já está funcionando (localhost:3000)
2. ✅ Credenciais corretas (admin / TriSLA2025!)
3. ✅ Não precisa copiar arquivos
4. ✅ Apenas colar JSON via web UI

---

## 🔧 Se Precisar Importar via API

### Verificar se arquivos existem:

```bash
# No node1
cd ~/gtp5g/trisla-portal
ls grafana-dashboards/*.json 2>&1

# Se existirem:
chmod +x scripts/import_dashboards_grafana.sh
./scripts/import_dashboards_grafana.sh
```

### Comando manual (se arquivos existirem):

```bash
# No node1
GRAFANA_URL="http://localhost:3000"
GRAFANA_USER="admin"
GRAFANA_PASS="TriSLA2025!"

# Lista explícita (sem wildcard)
dashboards=(
  "grafana-dashboards/trisla-complete-main.json"
  "grafana-dashboards/trisla-slices-management.json"
  "grafana-dashboards/trisla-metrics-detailed.json"
  "grafana-dashboards/trisla-admin-panel.json"
  "grafana-dashboards/trisla-create-slices.json"
  "grafana-dashboards/trisla-centralized-view.json"
)

for dashboard in "${dashboards[@]}"; do
  if [ -f "$dashboard" ]; then
    echo "Importando: $(basename $dashboard)"
    curl -s -X POST "${GRAFANA_URL}/api/dashboards/db" \
      -u "${GRAFANA_USER}:${GRAFANA_PASS}" \
      -H "Content-Type: application/json" \
      -d @"${dashboard}" | jq -r '.status // .message // "OK"'
    echo ""
  else
    echo "⚠️  Arquivo não encontrado: $dashboard"
  fi
done
```

---

## 📋 Checklist

- [x] ✅ Grafana acessível: http://localhost:3000
- [x] ✅ Credenciais: admin / TriSLA2025!
- [ ] Importar dashboards via interface web
- [ ] Ou copiar arquivos para node1 e importar via API
- [ ] Verificar dashboards importados
- [ ] Configurar datasource Prometheus (se necessário)

---

## 💡 Recomendação Final

**Use a interface web do Grafana** para importar os dashboards:
- ✅ Mais simples
- ✅ Não precisa copiar arquivos
- ✅ Funciona imediatamente
- ✅ Visual e intuitivo

**Passos:**
1. Acessar http://localhost:3000
2. Login: admin / TriSLA2025!
3. Dashboards → Import → Paste JSON
4. Colar conteúdo de cada arquivo JSON
5. Importar e repetir




