# Configuração Completa do Grafana - TriSLA Portal

## 📊 Visão Geral

Este guia configura dashboards completos do Grafana para monitoramento centralizado do TriSLA Portal, incluindo:
- TriSLA Portal (API, UI, Worker)
- Decision Engine
- NWDAF
- SLA Agents
- Métricas de SLAs e Slices
- Performance e Health Checks

## 🚀 Pré-requisitos

- Grafana instalado no cluster (namespace `monitoring` ou `trisla`)
- Prometheus configurado e coletando métricas
- Acesso ao cluster Kubernetes

## 🔧 Verificar Instalação do Grafana

```bash
# Verificar se Grafana está rodando
kubectl get pods -n monitoring -l app.kubernetes.io/name=grafana
kubectl get pods -n trisla -l app=grafana

# Verificar serviços
kubectl get svc -n monitoring -l app.kubernetes.io/name=grafana
kubectl get svc -n trisla -l app=grafana

# Verificar port-forward ou NodePort
kubectl get svc -n monitoring -o wide
```

## 📝 Obter Credenciais do Grafana

```bash
# Obter senha do admin
kubectl get secret -n monitoring grafana -o jsonpath='{.data.admin-password}' | base64 -d
echo ""

# Ou se estiver no namespace trisla
kubectl get secret -n trisla grafana-admin-credentials -o jsonpath='{.data.password}' | base64 -d
echo ""
```

## 🔌 Configurar Port-Forward

```bash
# Port-forward para Grafana (escolha o namespace correto)
# Opção 1: Namespace monitoring
kubectl port-forward -n monitoring svc/grafana 3000:80 &

# Opção 2: Namespace trisla
kubectl port-forward -n trisla svc/grafana 3000:80 &

# Verificar conectividade
curl -sS http://localhost:3000/api/health | jq .
```

## 📊 Configurar Datasources

### Prometheus Datasource

```bash
# Configurar Prometheus como datasource
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
```

**Nota:** Ajuste a URL do Prometheus conforme seu ambiente:
- `http://prometheus-server.monitoring.svc.cluster.local:80`
- `http://prometheus.monitoring.svc.cluster.local:9090`
- `http://prometheus-server:80`

## 🎨 Dashboards a Configurar

1. **TriSLA Portal Overview** - Visão geral do sistema
2. **SLAs & Slices** - Monitoramento de SLAs e slices
3. **Worker & Jobs** - Processamento de jobs em background
4. **Decision Engine** - Métricas do motor de decisão
5. **NWDAF Analytics** - Análises de rede
6. **SLA Agents** - Status dos agentes SLA
7. **Performance Metrics** - Métricas de performance
8. **Health & Alerts** - Health checks e alertas

## 📋 Scripts de Configuração

Use o script `scripts/configure_grafana_dashboards.sh` ou configure manualmente através da interface web do Grafana.

## 🌐 Acesso ao Grafana

Após configurar port-forward:
- **URL**: http://localhost:3000
- **Usuário**: admin
- **Senha**: (obtida via kubectl get secret)

## 🔍 Troubleshooting

### Problema: Grafana não acessível
- Verificar se pod está Running
- Verificar se service está configurado
- Verificar firewall/portas

### Problema: Datasource não conecta
- Verificar URL do Prometheus
- Verificar se Prometheus está rodando
- Testar conectividade entre pods

### Problema: Dashboards sem dados
- Verificar se métricas estão sendo coletadas
- Verificar queries PromQL
- Verificar labels e seletores




