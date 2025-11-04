# Passos para Configurar Grafana Dashboards - TriSLA Portal

## 🔍 Passo 1: Diagnosticar Conectividade

Antes de configurar Grafana, vamos verificar o problema de conectividade com o NodePort:

```bash
# Conectar ao node1 via SSH
ssh porvir5g@node1

# Verificar se o Service NodePort está rodando
kubectl get svc -n trisla trisla-portal

# Verificar se há firewall bloqueando porta 30080
sudo ufw status | grep 30080 || echo "Porta 30080 não encontrada nas regras"

# Testar conectividade local no node1
curl -sS http://localhost:30080/api/v1/health | jq .

# Verificar endpoints do service
kubectl get endpoints -n trisla trisla-portal
```

**Solução para erro ERR_CONNECTION_TIMED_OUT:**
- O erro pode ser devido a firewall local (Windows) ou rede
- Use port-forward como alternativa: `kubectl port-forward -n trisla svc/trisla-portal 8092:8000`

## 📊 Passo 2: Verificar Grafana no Cluster

```bash
# Conectar ao node1
ssh porvir5g@node1

# Verificar se Grafana está rodando
kubectl get pods -n monitoring -l app.kubernetes.io/name=grafana
kubectl get pods -n trisla -l app=grafana

# Verificar serviços
kubectl get svc -n monitoring -l app.kubernetes.io/name=grafana
kubectl get svc -n trisla -l app=grafana

# Verificar namespace correto
kubectl get namespaces | grep -E "monitoring|trisla"
```

## 🔐 Passo 3: Obter Credenciais do Grafana

```bash
# Tentar obter senha do namespace monitoring
kubectl get secret -n monitoring grafana -o jsonpath='{.data.admin-password}' | base64 -d
echo ""

# Tentar obter senha do namespace trisla
kubectl get secret -n trisla grafana-admin-credentials -o jsonpath='{.data.password}' | base64 -d
echo ""

# Ou verificar todos os secrets
kubectl get secrets -n monitoring | grep grafana
kubectl get secrets -n trisla | grep grafana
```

## 🔌 Passo 4: Configurar Port-Forward para Grafana

```bash
# Port-forward para Grafana (tentar ambos namespaces)
# Opção 1: Namespace monitoring
kubectl port-forward -n monitoring svc/grafana 3000:80 &

# Opção 2: Namespace trisla (se existir)
kubectl port-forward -n trisla svc/grafana 3000:80 &

# Verificar se está funcionando
sleep 2
curl -sS http://localhost:3000/api/health | jq .

# Se não funcionar, verificar qual service existe
kubectl get svc -A | grep grafana
```

## ⚙️ Passo 5: Configurar Datasource Prometheus

```bash
# Configurar Prometheus como datasource
# Primeiro, descobrir URL do Prometheus
kubectl get svc -n monitoring | grep prometheus
kubectl get svc -n trisla | grep prometheus

# Configurar datasource (ajustar URL conforme necessário)
curl -X POST http://admin:admin@localhost:3000/api/datasources \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Prometheus",
    "type": "prometheus",
    "url": "http://prometheus-server.monitoring.svc.cluster.local:80",
    "access": "proxy",
    "isDefault": true,
    "jsonData": {
      "httpMethod": "POST"
    }
  }' | jq .

# Se a URL acima não funcionar, tentar estas alternativas:
# - http://prometheus.monitoring.svc.cluster.local:9090
# - http://prometheus-server:80
# - http://prometheus:9090
```

## 📋 Passo 6: Importar Dashboards

```bash
# Opção A: Usar script automatizado
chmod +x scripts/setup_grafana_complete.sh
./scripts/setup_grafana_complete.sh

# Opção B: Importar manualmente via API
# 1. Copiar dashboard JSON para o servidor
# 2. Importar via API
curl -X POST http://admin:admin@localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @grafana-dashboards/trisla-portal-overview.json | jq .

# Opção C: Importar via interface web
# 1. Acessar http://localhost:3000
# 2. Login com admin / (senha obtida no passo 3)
# 3. Navegar para Dashboards > Import
# 4. Upload do arquivo JSON ou colar conteúdo
```

## 🎨 Passo 7: Configurar Dashboards Manuais

Se preferir configurar via interface web:

1. **Acessar Grafana**
   - URL: http://localhost:3000 (via port-forward)
   - Usuário: admin
   - Senha: (obtida no Passo 3)

2. **Configurar Datasource**
   - Ir em Configuration > Data Sources
   - Add data source > Prometheus
   - URL: `http://prometheus-server.monitoring.svc.cluster.local:80`
   - Save & Test

3. **Importar Dashboards**
   - Ir em Dashboards > Import
   - Upload dos arquivos JSON em `grafana-dashboards/`
   - Ou usar IDs de dashboards públicos do Grafana

## 🔍 Passo 8: Verificar Métricas Disponíveis

```bash
# Conectar ao Prometheus para verificar métricas
kubectl port-forward -n monitoring svc/prometheus-server 9090:80 &

# Consultar métricas disponíveis
curl -sS 'http://localhost:9090/api/v1/label/__name__/values' | jq '.data[]' | grep trisla

# Verificar métricas específicas
curl -sS 'http://localhost:9090/api/v1/query?query=up{job=~"trisla.*"}' | jq .
```

## 🐛 Troubleshooting

### Problema: Grafana não acessível
```bash
# Verificar pods
kubectl get pods -n monitoring
kubectl get pods -n trisla

# Verificar logs
kubectl logs -n monitoring -l app.kubernetes.io/name=grafana --tail=50
```

### Problema: Datasource não conecta
```bash
# Testar conectividade entre pods
kubectl exec -n monitoring -it <grafana-pod> -- wget -O- http://prometheus-server.monitoring.svc.cluster.local:80/api/v1/status/config
```

### Problema: Dashboards sem dados
```bash
# Verificar se métricas estão sendo coletadas
kubectl port-forward -n monitoring svc/prometheus-server 9090:80 &
curl -sS 'http://localhost:9090/api/v1/targets' | jq '.data.activeTargets[] | select(.labels.job | contains("trisla"))'
```

## ✅ Checklist Final

- [ ] Grafana está rodando e acessível
- [ ] Credenciais obtidas e testadas
- [ ] Port-forward configurado (3000:80)
- [ ] Datasource Prometheus configurado
- [ ] Dashboards importados
- [ ] Métricas aparecendo nos dashboards
- [ ] Alertas configurados (opcional)

## 📊 Dashboards Disponíveis

1. **TriSLA Portal Overview** (`trisla-portal-overview.json`)
   - Status dos componentes
   - Métricas de API
   - Jobs e processamento

2. **NWDAF Analytics** (via script existente)
   - Análises de rede
   - Predições QoS

3. **Dashboards Customizados** (criar conforme necessário)
   - SLAs e Slices
   - Decision Engine
   - SLA Agents

## 🔗 URLs de Acesso

- **Grafana**: http://localhost:3000 (via port-forward)
- **Prometheus**: http://localhost:9090 (via port-forward)
- **TriSLA API**: http://localhost:8092 (via port-forward node1)
- **TriSLA API Node2**: http://localhost:8093 (via port-forward node2)




