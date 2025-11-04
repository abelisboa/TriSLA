# Comandos Corrigidos para Importar Dashboards TriSLA

## 🚀 Comandos Prontos para Executar no node1

### Opção 1: Script Corrigido (Recomendado)

```bash
# No node1, já conectado
cd ~/gtp5g/trisla-portal

# Tornar script executável e executar
chmod +x scripts/import_grafana_dashboards_fixed.sh
./scripts/import_grafana_dashboards_fixed.sh
```

### Opção 2: Comandos Manuais Corrigidos

```bash
# 1) Verificar se port-forward está ativo
ps aux | grep "port-forward.*grafana" | grep -v grep

# Se não estiver, configurar:
kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80 &
sleep 3

# 2) Verificar conectividade
curl -sS http://localhost:3000/api/health | jq .

# 3) Importar dashboards (um por um)
GRAFANA_URL="http://localhost:3000"
GRAFANA_USER="admin"
GRAFANA_PASS="TriSLA2025!"

# Dashboard Principal
echo "Importando: Dashboard Principal..."
curl -s -X POST "${GRAFANA_URL}/api/dashboards/db" \
  -u "${GRAFANA_USER}:${GRAFANA_PASS}" \
  -H "Content-Type: application/json" \
  -d @grafana-dashboards/trisla-complete-main.json | jq -r '.status // .message // "OK"'

# Gestão de Slices
echo "Importando: Gestão de Slices..."
curl -s -X POST "${GRAFANA_URL}/api/dashboards/db" \
  -u "${GRAFANA_USER}:${GRAFANA_PASS}" \
  -H "Content-Type: application/json" \
  -d @grafana-dashboards/trisla-slices-management.json | jq -r '.status // .message // "OK"'

# Métricas Detalhadas
echo "Importando: Métricas Detalhadas..."
curl -s -X POST "${GRAFANA_URL}/api/dashboards/db" \
  -u "${GRAFANA_USER}:${GRAFANA_PASS}" \
  -H "Content-Type: application/json" \
  -d @grafana-dashboards/trisla-metrics-detailed.json | jq -r '.status // .message // "OK"'

# Painel Admin
echo "Importando: Painel Admin..."
curl -s -X POST "${GRAFANA_URL}/api/dashboards/db" \
  -u "${GRAFANA_USER}:${GRAFANA_PASS}" \
  -H "Content-Type: application/json" \
  -d @grafana-dashboards/trisla-admin-panel.json | jq -r '.status // .message // "OK"'

# Criar Slices
echo "Importando: Criar Slices..."
curl -s -X POST "${GRAFANA_URL}/api/dashboards/db" \
  -u "${GRAFANA_USER}:${GRAFANA_PASS}" \
  -H "Content-Type: application/json" \
  -d @grafana-dashboards/trisla-create-slices.json | jq -r '.status // .message // "OK"'

# Visão Centralizada
echo "Importando: Visão Centralizada..."
curl -s -X POST "${GRAFANA_URL}/api/dashboards/db" \
  -u "${GRAFANA_USER}:${GRAFANA_PASS}" \
  -H "Content-Type: application/json" \
  -d @grafana-dashboards/trisla-centralized-view.json | jq -r '.status // .message // "OK"'

# 4) Verificar dashboards importados
echo ""
echo "Dashboards importados:"
curl -s "${GRAFANA_URL}/api/search?query=trisla" \
  -u "${GRAFANA_USER}:${GRAFANA_PASS}" | jq '.[] | {title: .title, uid: .uid, url: .url}'
```

### Opção 3: Loop com Lista Explícita

```bash
GRAFANA_URL="http://localhost:3000"
GRAFANA_USER="admin"
GRAFANA_PASS="TriSLA2025!"

# Lista explícita de dashboards
dashboards=(
  "trisla-complete-main.json"
  "trisla-slices-management.json"
  "trisla-metrics-detailed.json"
  "trisla-admin-panel.json"
  "trisla-create-slices.json"
  "trisla-centralized-view.json"
)

for dashboard in "${dashboards[@]}"; do
  echo "=========================================="
  echo "Importando: $dashboard"
  echo "=========================================="
  
  if [ -f "grafana-dashboards/$dashboard" ]; then
    curl -s -X POST "${GRAFANA_URL}/api/dashboards/db" \
      -u "${GRAFANA_USER}:${GRAFANA_PASS}" \
      -H "Content-Type: application/json" \
      -d @"grafana-dashboards/$dashboard" | jq -r '.status // .message // "OK"'
    echo ""
  else
    echo "⚠️  Arquivo não encontrado: grafana-dashboards/$dashboard"
    echo ""
  fi
done

# Verificar dashboards
echo "Dashboards importados:"
curl -s "${GRAFANA_URL}/api/search?query=trisla" \
  -u "${GRAFANA_USER}:${GRAFANA_PASS}" | jq '.[] | {title: .title, uid: .uid}'
```

## 🔍 Verificar Arquivos

Antes de importar, verifique se os arquivos existem:

```bash
cd ~/gtp5g/trisla-portal
ls -lh grafana-dashboards/*.json
```

Se não existirem, você precisa copiar os arquivos criados localmente para o node1:

```bash
# Do seu computador local (Windows), copie os arquivos para o node1
scp grafana-dashboards/*.json porvir5g@192.168.10.16:~/gtp5g/trisla-portal/grafana-dashboards/
```

## ✅ Validação

Após importar, valide:

```bash
# Listar todos os dashboards TriSLA
curl -s http://admin:TriSLA2025!@localhost:3000/api/search?query=trisla | jq '.[] | .title'

# Acessar Grafana
# http://localhost:3000 (via port-forward)
# ou http://192.168.10.16:30000 (se NodePort configurado)
```

## 🎯 Próximos Passos

1. ✅ Importar todos os dashboards
2. ✅ Verificar se todos aparecem na lista
3. ✅ Configurar datasource Prometheus (se necessário)
4. ✅ Personalizar queries conforme métricas disponíveis
5. ✅ Configurar alertas personalizados (opcional)




