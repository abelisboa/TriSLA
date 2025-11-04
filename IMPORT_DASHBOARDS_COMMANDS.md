# Comandos para Importar Dashboards TriSLA no Grafana

## 📋 Pré-requisitos

1. Grafana acessível
2. Port-forward configurado (se necessário)
3. Credenciais do Grafana
4. Arquivos JSON dos dashboards no node1

## 🚀 Passo a Passo

### 1. Conectar ao node1

```bash
ssh porvir5g@192.168.10.16
```

### 2. Navegar para diretório do projeto

```bash
cd ~/gtp5g/trisla-portal
```

### 3. Verificar se dashboards existem

```bash
ls -la grafana-dashboards/*.json
```

### 4. Configurar variáveis (se necessário copiar dashboards)

Se os dashboards não estiverem no node1, copie-os primeiro:

```bash
# Criar diretório se não existir
mkdir -p grafana-dashboards

# Ou copiar do repositório se já estiver clonado
```

### 5. Configurar port-forward do Grafana

```bash
# Verificar se port-forward já está ativo
ps aux | grep "port-forward.*grafana" | grep -v grep

# Se não estiver, configurar:
kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80 &
sleep 3

# Verificar se está funcionando
curl -sS http://localhost:3000/api/health | jq .
```

### 6. Importar Dashboards

#### Opção A: Script Automatizado

```bash
# Tornar script executável
chmod +x scripts/import_all_grafana_dashboards.sh

# Executar importação
GRAFANA_USER="admin" \
GRAFANA_PASS="TriSLA2025!" \
./scripts/import_all_grafana_dashboards.sh
```

#### Opção B: Importação Manual via API

```bash
# Configurar variáveis
GRAFANA_URL="http://localhost:3000"
GRAFANA_USER="admin"
GRAFANA_PASS="TriSLA2025!"

# Importar cada dashboard
for dashboard in grafana-dashboards/*.json; do
  echo "=========================================="
  echo "Importando: $(basename $dashboard)"
  echo "=========================================="
  
  RESPONSE=$(curl -s -X POST "${GRAFANA_URL}/api/dashboards/db" \
    -u "${GRAFANA_USER}:${GRAFANA_PASS}" \
    -H "Content-Type: application/json" \
    -d @"${dashboard}")
  
  if echo "$RESPONSE" | grep -q '"status":"success"'; then
    echo "✅ Dashboard importado com sucesso"
    DASHBOARD_UID=$(echo "$RESPONSE" | jq -r '.uid')
    echo "UID: $DASHBOARD_UID"
  else
    echo "⚠️  Dashboard pode já existir ou houve erro"
    echo "$RESPONSE" | jq . 2>/dev/null || echo "$RESPONSE"
  fi
  echo ""
done
```

#### Opção C: Importação Individual

```bash
# Dashboard Principal
curl -X POST http://admin:TriSLA2025!@localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @grafana-dashboards/trisla-complete-main.json | jq .

# Gestão de Slices
curl -X POST http://admin:TriSLA2025!@localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @grafana-dashboards/trisla-slices-management.json | jq .

# Métricas Detalhadas
curl -X POST http://admin:TriSLA2025!@localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @grafana-dashboards/trisla-metrics-detailed.json | jq .

# Painel Admin
curl -X POST http://admin:TriSLA2025!@localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @grafana-dashboards/trisla-admin-panel.json | jq .

# Criar Slices
curl -X POST http://admin:TriSLA2025!@localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @grafana-dashboards/trisla-create-slices.json | jq .

# Visão Centralizada
curl -X POST http://admin:TriSLA2025!@localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @grafana-dashboards/trisla-centralized-view.json | jq .
```

### 7. Verificar Dashboards Importados

```bash
# Listar todos os dashboards TriSLA
curl -sS http://admin:TriSLA2025!@localhost:3000/api/search?query=trisla | jq .
```

## 🌐 Acessar Dashboards

Após importar, acesse:

- **Grafana Home**: http://localhost:3000 ou http://192.168.10.16:30000
- **Dashboard Principal**: http://localhost:3000/d/trisla-main/trisla-portal-dashboard-principal
- **Gestão de Slices**: http://localhost:3000/d/trisla-slices-management/trisla-gestao-de-slices
- **Métricas Detalhadas**: http://localhost:3000/d/trisla-metrics-detailed/trisla-metricas-detalhadas
- **Painel Admin**: http://localhost:3000/d/trisla-admin-panel/trisla-painel-administrativo
- **Criar Slices**: http://localhost:3000/d/trisla-create-slices/trisla-criar-slices-lnp-templates
- **Visão Centralizada**: http://localhost:3000/d/trisla-centralized/trisla-visao-centralizada

## 🔧 Criar Slices via Dashboard

### Via LNP (no dashboard "Criar Slices")

O dashboard inclui exemplos de comandos. Use:

```bash
# Exemplo de criação via LNP
curl -X POST http://192.168.10.16:8092/api/v1/slices \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Criar slice URLLC com latência de 1ms e banda de 100Mbps"
  }' | jq .
```

### Via Templates (variáveis do dashboard)

O dashboard inclui variáveis interativas. Use os valores do dashboard ou execute:

```bash
curl -X POST http://192.168.10.16:8092/api/v1/slices \
  -H "Content-Type: application/json" \
  -d '{
    "slice_type": "URLLC",
    "bandwidth": 100,
    "latency": 1,
    "description": "Slice criado via template do Grafana"
  }' | jq .
```

## ✅ Validação

Após importar, verifique:

1. ✅ Todos os dashboards aparecem na lista
2. ✅ Dashboards carregam sem erros
3. ✅ Métricas aparecem (se Prometheus estiver coletando)
4. ✅ Links entre dashboards funcionam
5. ✅ Variáveis interativas funcionam
6. ✅ Refresh automático funciona

## 📝 Próximos Passos

1. Personalizar queries conforme métricas disponíveis
2. Configurar alertas personalizados
3. Adicionar mais painéis conforme necessário
4. Integrar com UI do TriSLA Portal
5. Configurar notificações




