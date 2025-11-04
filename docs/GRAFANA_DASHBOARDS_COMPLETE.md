# Guia Completo - Dashboards TriSLA no Grafana

## 📊 Dashboards Criados

### 1. **TriSLA Portal - Dashboard Principal**
- **UID**: `trisla-main`
- **Descrição**: Visão geral completa do sistema TriSLA
- **Funcionalidades**:
  - Status geral do sistema
  - Componentes TriSLA (API, Worker, Decision Engine, NWDAF, SLA Agents)
  - Slices ativos
  - Jobs processados
  - Taxa de sucesso
  - Request rate e latência
  - Distribuição de slices e jobs

### 2. **TriSLA - Gestão de Slices**
- **UID**: `trisla-slices-management`
- **Descrição**: Gerenciamento completo de slices
- **Funcionalidades**:
  - Slices ativos por tipo
  - Slices criados (24h)
  - Latência por tipo de slice
  - Bandwidth por slice
  - Tabela de status dos slices

### 3. **TriSLA - Métricas Detalhadas**
- **UID**: `trisla-metrics-detailed`
- **Descrição**: Métricas detalhadas de todos os componentes
- **Funcionalidades**:
  - CPU e Memory usage por componente
  - Network I/O
  - Decision Engine - predições e decisões
  - NWDAF - análises de rede
  - SLA Agents - status e compliance

### 4. **TriSLA - Painel Administrativo**
- **UID**: `trisla-admin-panel`
- **Descrição**: Painel completo para administração
- **Funcionalidades**:
  - Visão geral do sistema
  - Health check dos componentes
  - Métricas de performance
  - Uso de recursos do cluster
  - Alertas e notificações

### 5. **TriSLA - Criar Slices (LNP & Templates)**
- **UID**: `trisla-create-slices`
- **Descrição**: Interface para criar slices via LNP e templates
- **Funcionalidades**:
  - Variáveis interativas (tipo, bandwidth, latency)
  - Comandos prontos para criação via API
  - Templates predefinidos (URLLC, eMBB, mMTC)
  - Status de criação
  - Distribuição de slices

### 6. **TriSLA - Visão Centralizada**
- **UID**: `trisla-centralized`
- **Descrição**: Visualização centralizada de todos os componentes
- **Funcionalidades**:
  - Status de todos os componentes em um lugar
  - Métricas de performance consolidadas
  - Latência end-to-end
  - Distribuição de slices
  - Uso de recursos consolidado

## ⚠️ **IMPORTANTE: Métricas vs Dashboards**

### ✅ Métricas já estão em tempo real
- **Prometheus do NASP** já coleta métricas automaticamente
- **Services** já expõem `/metrics`
- **Não precisa importar métricas** - elas funcionam em tempo real

### ⚠️ O que importamos são os **dashboards** (visualizações)
- **Dashboards** = templates de gráficos/visualizações
- Após importar, dashboards **consultam Prometheus automaticamente**
- Métricas aparecem **em tempo real** nos gráficos

📖 Ver explicação completa: [GRAFANA_DASHBOARDS_EXPLICACAO.md](./GRAFANA_DASHBOARDS_EXPLICACAO.md)

---

## 🚀 Como Importar Dashboards

### Opção 1: Script Automatizado

```bash
# No node1, navegar para diretório do projeto
cd ~/gtp5g/trisla-portal

# Configurar port-forward do Grafana (se necessário)
kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80 &

# Executar script de importação
chmod +x scripts/import_all_grafana_dashboards.sh
./scripts/import_all_grafana_dashboards.sh
```

### Opção 2: Importação Manual via API

```bash
# Configurar variáveis
GRAFANA_URL="http://localhost:3000"
GRAFANA_USER="admin"
GRAFANA_PASS="TriSLA2025!"

# Importar cada dashboard
for dashboard in grafana-dashboards/*.json; do
  echo "Importando: $dashboard"
  curl -X POST http://${GRAFANA_USER}:${GRAFANA_PASS}@localhost:3000/api/dashboards/db \
    -H "Content-Type: application/json" \
    -d @"${dashboard}" | jq .
done
```

### Opção 3: Importação via Interface Web

1. Acessar Grafana: http://localhost:3000 ou http://192.168.10.16:30000
2. Login: admin / TriSLA2025!
3. Ir em: Dashboards > Import
4. Upload de cada arquivo JSON de `grafana-dashboards/`
5. Salvar e verificar

## 🔧 Criar Slices via Dashboard

### Via LNP (Linguagem Natural)

```bash
# Exemplo: Criar slice URLLC via descrição em português
curl -X POST http://192.168.10.16:8092/api/v1/slices \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Criar slice URLLC com latência de 1ms e banda de 100Mbps para telecirurgia"
  }' | jq .
```

### Via Template

```bash
# URLLC Template
curl -X POST http://192.168.10.16:8092/api/v1/slices \
  -H "Content-Type: application/json" \
  -d '{
    "slice_type": "URLLC",
    "bandwidth": 100,
    "latency": 1,
    "description": "Slice URLLC via template"
  }' | jq .

# eMBB Template
curl -X POST http://192.168.10.16:8092/api/v1/slices \
  -H "Content-Type: application/json" \
  -d '{
    "slice_type": "eMBB",
    "bandwidth": 500,
    "latency": 5,
    "description": "Slice eMBB via template"
  }' | jq .

# mMTC Template
curl -X POST http://192.168.10.16:8092/api/v1/slices \
  -H "Content-Type: application/json" \
  -d '{
    "slice_type": "mMTC",
    "bandwidth": 50,
    "latency": 10,
    "description": "Slice mMTC via template"
  }' | jq .
```

## 📋 Endpoints da API TriSLA

### Slices
- **POST** `/api/v1/slices` - Criar slice
- **GET** `/api/v1/slices` - Listar slices
- **GET** `/api/v1/slices/{id}` - Obter slice específico

### Health & Status
- **GET** `/api/v1/health` - Health check
- **GET** `/api/v1/status` - Status detalhado

### Métricas
- **GET** `/metrics` - Métricas Prometheus
- **GET** `/api/v1/metrics` - Métricas JSON

## 🎨 Design Responsivo

Todos os dashboards foram criados com:
- ✅ Design responsivo (grid adaptativo)
- ✅ Tema dark (otimizado para monitoramento)
- ✅ Gráficos modernos (timeseries, stat, gauge, piechart, barchart)
- ✅ Refresh automático (10s-30s)
- ✅ Time ranges configuráveis
- ✅ Variáveis interativas (templates)

## 🔗 Navegação Entre Dashboards

Os dashboards incluem links de navegação:
- **Dashboard Principal** → Links para todos os outros
- **Gestão de Slices** → Link para criar slices
- **Métricas** → Links para métricas detalhadas
- **Admin** → Link para painel administrativo

## 📊 Métricas Monitoradas

### Componentes
- TriSLA Portal (API, UI, Worker)
- Decision Engine
- NWDAF
- SLA Agents

### Métricas
- CPU Usage
- Memory Usage
- Network I/O
- HTTP Requests/sec
- Latency (p95, p99)
- Jobs (completed, failed, active)
- Slices (active, created, by type)
- Predictions e Decisions
- SLA Compliance

## 🔍 Troubleshooting

### Dashboards sem dados
1. Verificar se Prometheus está coletando métricas
2. Verificar queries PromQL
3. Verificar labels e seletores
4. Verificar datasource configurado

### Métricas não aparecem
1. Verificar se `/metrics` endpoint está exposto
2. Verificar ServiceMonitor configurado
3. Verificar pods estão Running
4. Consultar métricas diretamente no Prometheus

### Erro ao importar
1. Verificar formato JSON
2. Verificar permissões do usuário
3. Verificar datasource UID correto
4. Tentar importar via interface web

## ✅ Checklist de Configuração

- [ ] Grafana acessível
- [ ] Datasource Prometheus configurado
- [ ] Dashboards importados
- [ ] Métricas aparecendo
- [ ] Links funcionando
- [ ] Variáveis funcionando
- [ ] Refresh configurado
- [ ] Alertas configurados (opcional)

## 🎯 Próximos Passos

1. Importar todos os dashboards
2. Configurar alertas personalizados
3. Personalizar queries conforme necessário
4. Adicionar métricas customizadas
5. Configurar notificações (email, Slack, etc.)
